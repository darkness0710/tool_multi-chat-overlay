"""An OBS Browser Source for the merged chat: one page on 127.0.0.1.

    python merge_chat.py --web            then point OBS at http://127.0.0.1:8770/

Why a page and not the console: OBS can capture a window, but a console window
brings its own background, its own font and a title bar, and cannot be made
transparent. A Browser Source is transparent by default, so the chat sits over
the game with nothing behind it.

The look is the Stylus userstyle this project's author already uses on
YouTube's own chat -- same Montserrat, same name pill, same per-role colours,
same 30-second fade -- so the merged chat matches what viewers already see
rather than introducing a second visual language. What it adds is a ring
around the avatar in the platform's colour, because the one thing that style
never had to say is which site a line came from.

Server-sent events, not polling and not a websocket: the traffic goes one way,
and SSE is the one push mechanism that needs no library on either end and
reconnects by itself when OBS reloads the source.
"""
import json
import queue
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KEEPALIVE = 15.0                # seconds; a silent chat must not look dead
BACKLOG = 40                    # messages a source gets on connect


class Hub:
    """Fan-out from the readers to however many browser sources are open."""

    def __init__(self):
        self._lock = threading.Lock()
        self._subs = set()
        self._recent = []

    def publish(self, payload):
        with self._lock:
            self._recent.append(payload)
            del self._recent[:-BACKLOG]
            subs = list(self._subs)
        for sub in subs:
            try:
                sub.put_nowait(payload)
            except queue.Full:              # a source that stopped reading
                pass

    def subscribe(self):
        sub = queue.Queue(maxsize=500)
        with self._lock:
            self._subs.add(sub)
            backlog = list(self._recent)
        return sub, backlog

    def drop(self, sub):
        with self._lock:
            self._subs.discard(sub)


PAGE = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Merged chat overlay</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  /* The author's own YouTube userstyle, kept value for value. */
  :root {
    --nameTextColorOwner: #b42ac1;
    --nameBackgroundColorOwner: #ffffff;
    --nameTextColorMember: #ffffff;
    --nameBackgroundColorMember: #a32834;
    --nameTextColor: #ffffff;
    --nameBackgroundColor: #8b5509;
    --nameTextColorMod: #ffffff;
    --nameBackgroundColorMod: #1e90ff;
    --nameFontSize: 18px;
    --chatFontSize: 18px;
    --fade-at: 30s;
    /* #ff0033 was YouTube's own red at full chroma, which over a game reads
       as an alarm rather than as a label. Same hue family, chroma well down
       and luminance up: a 12px tag with a black stroke behind it wants to be
       LIGHT, not saturated. Override either with ?yt= / ?tt= in the URL. */
    --yt: #f08a7e;
    --tt: #25f4ee;
    /* An outline, not a shadow. A single soft shadow is what the userstyle
       has, and it disappears the moment the map underneath is snow: the game
       is as likely to be white as dark, so the text has to carry its own
       contrast in every direction rather than lean on one corner. Eight hard
       offsets trace the glyph; the soft one after them lifts it off the map.
       -webkit-text-stroke would be tidier but Chromium draws it INSIDE the
       glyph, which thins bold text until it looks broken. */
    --ink-outline:
      1px 1px 0 #000, -1px 1px 0 #000, 1px -1px 0 #000, -1px -1px 0 #000,
      1px 0 0 #000, -1px 0 0 #000, 0 1px 0 #000, 0 -1px 0 #000,
      0 2px 5px rgba(0, 0, 0, .75);
  }
  /* Transparent all the way down, or OBS composites a black rectangle. */
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden;
               background: rgba(0, 0, 0, 0); border: none; }
  body { font-family: 'Montserrat', 'Roboto', 'Noto Sans', sans-serif; }

  /* Anchored to the bottom, so a new line pushes the old ones up the way a
     chat does, without the page ever needing to scroll. */
  #chat { position: absolute; left: 0; right: 0; bottom: 0;
          display: flex; flex-direction: column; justify-content: flex-end;
          padding: 8px; gap: 1px; }

  /* Which platform a line came from, four ways, chosen with ?mark= in the
     URL because it is a matter of taste and taste is quicker to try than to
     describe. The default is the tag -- <avatar> <name> [YT] -- written as
     brackets rather than as a second filled chip: the name pill is already a
     solid block, and two of them side by side over a game is heavier than the
     one fact they carry between them. The badge alternative puts a shape on
     the avatar instead, which survives colour blindness.
     Not on the list: recolouring the name pill. That pill already means
     owner / mod / member, and taking it over would trade one fact for
     another rather than add one. */
  .msg { display: flex; align-items: flex-start; padding: 4px;
         border-left: 3px solid transparent;
         animation: rise .18s ease-out, fade 1s forwards;
         animation-delay: 0s, var(--fade-at); }
  /* ?mark=bar -- a stripe down the side of the row. */
  .mark-bar .msg { padding-left: 7px; }
  .mark-bar .yt, .mark-bar .tt { border-left-color: var(--ring); }
  /* Hidden by default and shown by the mode, rather than the other way
     round. Listing the modes that hide it put a (0,2,0) rule against the
     (0,2,0) `.msg .badge` below, which wins on being later -- so ?mark=tag
     drew the badge AND the tag. Showing from the mode is (0,3,0) and does
     not care what order the file is in. */
  .mark-badge .msg .badge { display: flex; }
  .mark-tag .yt .ptag, .mark-tag .tt .ptag { display: inline-block; }
  @keyframes rise { from { opacity: 0; transform: translateY(6px); }
                    to   { opacity: 1; transform: none; } }
  @keyframes fade { to { opacity: 0; } }

  .msg .avwrap { position: relative; flex: none; margin: 1px 8px 0 0;
                 width: 28px; height: 28px; }
  .msg .av { width: 28px; height: 28px; border-radius: 50%; display: block;
             object-fit: cover; background: rgba(0, 0, 0, .35);
             box-shadow: 0 1px 3px rgba(0, 0, 0, .5); }
  /* Sat on the avatar's corner, the way a presence dot is, so it costs no
     width and cannot be mistaken for part of the name. */
  .msg .badge { position: absolute; right: -3px; bottom: -3px;
                width: 15px; height: 15px; border-radius: 50%;
                background: var(--ring);
                box-shadow: 0 0 0 1.5px rgba(0, 0, 0, .6);
                display: none; align-items: center;
                justify-content: center; }
  .msg .badge svg { width: 9px; height: 9px; display: block; }
  .yt { --ring: var(--yt); }
  .tt { --ring: var(--tt); }
  /* No face and no pill: a system line lines up with the names instead. */
  .sys { --ring: #8b93a1; padding-left: 40px; }

  .msg .body { display: flex; flex-direction: column; min-width: 0;
               flex-grow: 1; }
  /* The pill and its tag share a line; the pill keeps shrinking on its own
     so a long name still ellipsises instead of pushing the tag off. */
  .msg .nameline { display: flex; align-items: baseline; gap: 7px;
                   min-width: 0; }
  .ptag { flex: none; display: none; font-size: 12px; font-weight: 700;
          letter-spacing: .5px; color: var(--ring); opacity: .95;
          text-shadow: var(--ink-outline); position: relative; top: -1px;
          font-family: ui-monospace, Consolas, monospace; }
  .msg .who { max-width: 100%; min-width: 0;
              font-size: var(--nameFontSize); font-weight: 700;
              padding: 4px 8px; border-radius: 20px;
              white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
              box-shadow: 1px 1px 3px rgba(0, 0, 0, .2);
              text-shadow: 1px 1px 2px rgba(0, 0, 0, .6);
              background: var(--nameBackgroundColor);
              color: var(--nameTextColor); }
  /* Owner swaps the two, exactly as the userstyle does. */
  .owner .who  { background: var(--nameTextColorOwner);
                 color: var(--nameBackgroundColorOwner); }
  .mod .who    { background: var(--nameBackgroundColorMod);
                 color: var(--nameTextColorMod); }
  .member .who { background: var(--nameBackgroundColorMember);
                 color: var(--nameTextColorMember); }

  /* The negative margin tucks the text under the pill, as in the userstyle. */
  .msg .txt { font-size: var(--chatFontSize); line-height: 1.55;
              font-weight: 700; color: #fff; padding: 5px 10px 3px;
              margin-top: -9px; background: transparent; border: none;
              text-shadow: var(--ink-outline);
              overflow-wrap: break-word; word-wrap: break-word; }

  /* Eight hard shadows are a cage around every letter: at 18px bold it reads
     as a sticker rather than as text. paint-order draws a real stroke behind
     the fill, so the outline sits OUTSIDE the glyph and can be thinner while
     covering more. The shadow version stays as the fallback -- it is ugly but
     it is legible, which is the property that matters. */
  @supports (paint-order: stroke) {
    .msg .txt, .ptag {
      -webkit-text-stroke: 3px rgba(0, 0, 0, .88);
      paint-order: stroke fill;
      text-shadow: 0 2px 6px rgba(0, 0, 0, .55);
    }
  }

  /* Add ?plate to the URL when even an outline is not enough -- a bright,
     busy map. A query parameter rather than a setting, so it can be toggled
     in OBS's own URL box without restarting anything. */
  body.plate .msg .txt { background: rgba(0, 0, 0, .5); border-radius: 12px;
                         padding: 6px 12px; }
  body.plate .msg .txt img.em { vertical-align: -0.28em; }

  /* A channel emoji, sized to the line rather than to its own pixels. */
  .msg .txt img.em { height: 1.3em; width: auto; vertical-align: -0.28em;
                     margin: 0 1px; }
  .sys .txt { font-weight: 600; opacity: .75; font-size: 13px;
              margin-top: 0; padding: 2px 10px; }
  .sys .who, .sys .avwrap { display: none; }
</style>
</head>
<body>
<div id="chat"></div>
<script>
const chat = document.getElementById("chat");

// ?plate puts a dark pane behind each message, for a map too bright for an
// outline alone. ?fade=NN changes how long a line stays.
const opts = new URLSearchParams(location.search);
if (opts.has("plate")) document.body.classList.add("plate");
// ?yt=f08a7e / ?tt=25f4ee -- hex digits only, no leading #, and nothing but
// hex digits ever reaches setProperty: a query string is untrusted input, and
// a custom property is a place CSS would happily accept far more than a
// colour.
const HEX = /^[0-9a-fA-F]{3,8}$/;
for (const key of ["yt", "tt"]) {
  const want = opts.get(key);
  if (want && HEX.test(want)) {
    document.documentElement.style.setProperty("--" + key, "#" + want);
  }
}

const MARKS = ["tag", "badge", "bar", "none"];
const mark = MARKS.indexOf(opts.get("mark")) >= 0 ? opts.get("mark") : "tag";
document.body.classList.add("mark-" + mark);
const fadeSec = Number(opts.get("fade"));
if (isFinite(fadeSec) && fadeSec > 0) {
  document.documentElement.style.setProperty("--fade-at", fadeSec + "s");
}

// The userstyle fades a message out and leaves it in the DOM. Over a
// four-hour stream that is thousands of invisible nodes, so this takes them
// away once the fade has finished.
const GONE_MS = ((isFinite(fadeSec) && fadeSec > 0 ? fadeSec : 30) + 1.5)
               * 1000;

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s == null ? "" : s;
  return d.innerHTML;
}

// A message is either plain text or a list of pieces, and the pieces are the
// only way a channel's own emoji can be drawn: YouTube hands those over as
// :shortcodes: in the plain text. Escaping happens per piece, so the emoji
// tag is the only markup that ever reaches innerHTML.
function body(m) {
  if (!m.parts || !m.parts.length) return esc(m.text);
  return m.parts.map(p => p[0] === "e"
    ? '<img class="em" src="' + esc(p[1]) + '" alt="' + esc(p[2] || "") +
      '" title="' + esc(p[2] || "") + '">'
    : esc(p[1])).join("");
}

// Drawn here rather than fetched: two shapes are smaller than one request,
// and an overlay that has just started must not wait on a CDN to say which
// platform a line came from.
const ICON = {
  yt: '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<polygon points="9,6.5 18.5,12 9,17.5" fill="#fff"/></svg>',
  tt: '<svg viewBox="0 0 24 24" aria-hidden="true">' +
      '<circle cx="9" cy="17" r="3.6" fill="#fff"/>' +
      '<rect x="11.7" y="4.5" width="2.7" height="12.5" rx="1.35" fill="#fff"/>' +
      '<path d="M13.8 4.9c1.3 2.2 3.2 3.1 4.9 3.2v2.8c-2-.1-3.7-1-4.9-2.1z"' +
      ' fill="#fff"/></svg>'
};

function add(m) {
  const el = document.createElement("div");
  el.className = "msg " + (m.p || "sys") + (m.role ? " " + m.role : "");
  const face = m.avatar
    ? '<img class="av" src="' + esc(m.avatar) + '" alt="" ' +
      'onerror="this.removeAttribute(&quot;src&quot;)">'
    : '<span class="av"></span>';
  const badge = ICON[m.p]
    ? '<span class="badge">' + ICON[m.p] + "</span>" : "";
  const av = '<span class="avwrap">' + face + badge + "</span>";
  const tag = m.p === "yt" ? "[YT]" : m.p === "tt" ? "[TT]" : "";
  el.innerHTML = av + '<div class="body"><div class="nameline">' +
                 '<span class="who">' + esc(m.who) + "</span>" +
                 (tag ? '<span class="ptag">' + tag + "</span>" : "") +
                 '</div><div class="txt">' + body(m) + "</div></div>";
  chat.appendChild(el);
  setTimeout(() => el.remove(), GONE_MS);
  // A burst can still outrun the timers, so keep the list bounded as well.
  while (chat.children.length > 60) chat.firstChild.remove();
}

// EventSource reconnects on its own, which is what makes this survive OBS
// refreshing the source or the tool being restarted underneath it.
const es = new EventSource("/events");
es.onmessage = e => { try { add(JSON.parse(e.data)); } catch (err) {} };
</script>
</body>
</html>
"""


def serve(hub, port=8770, host="127.0.0.1"):
    """Start the overlay server in a daemon thread. Returns the URL."""

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args):
            pass                            # the chat is the output, not this

        def do_GET(self):
            if self.path.split("?")[0] == "/":
                body = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path.split("?")[0] == "/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                sub, backlog = hub.subscribe()
                try:
                    for payload in backlog:
                        self._event(payload)
                    while True:
                        try:
                            self._event(sub.get(timeout=KEEPALIVE))
                        except queue.Empty:
                            # A comment line: keeps the socket and any proxy
                            # from deciding a quiet chat has hung up.
                            self.wfile.write(b": keepalive\n\n")
                            self.wfile.flush()
                except ConnectionError:
                    # ConnectionError, not the two named subclasses: a
                    # browser source that goes away raises whichever of
                    # Broken / Reset / Aborted the platform picks, and on
                    # Windows a refresh raises the Aborted one -- which was
                    # not in the list, so every refresh printed a traceback
                    # into the console the chat is being read in.
                    pass
                finally:
                    hub.drop(sub)
                return
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _event(self, payload):
            data = json.dumps(payload, ensure_ascii=False)
            self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
            self.wfile.flush()

    class Server(ThreadingHTTPServer):
        def handle_error(self, request, client_address):
            # A source closing mid-stream is how SSE ends, not a fault, and
            # socketserver prints a traceback for it by default. Anything that
            # is not the socket going away still gets printed.
            if isinstance(sys.exc_info()[1], ConnectionError):
                return
            super().handle_error(request, client_address)

    server = Server((host, port), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://{host}:{port}/"
