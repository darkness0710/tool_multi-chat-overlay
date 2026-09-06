"""Two live chats, one window: a YouTube live and a TikTok LIVE, merged.

    python merge_chat.py                       the two channels this was built for
    python merge_chat.py --youtube @NAME --tiktok @NAME
    python merge_chat.py --youtube VIDEO_URL   a fixed video instead of a channel
    python merge_chat.py --log chat.txt        keep a transcript as well
    python merge_chat.py --only yt             one side only, for testing

Neither side needs the streamer's account, and neither needs a login of yours:
both read the public chat of a public livestream, the way a viewer's browser
does. That is the whole reason this exists rather than Casterlabs, which
merges the platforms YOU have connected, not two links you paste.

Channels, not links
-------------------
Give it a channel on each side and it finds the live itself, then waits and
looks again when there is none. A video URL still works and is taken as is,
for reading the chat of one particular stream.

Finding the YouTube live costs one request and no key. The obvious route is
the Data API's search.list with eventType=live, which needs an API key and
spends 100 quota units per call -- polling that all evening runs a default
project out of quota. yt-dlp reads the channel's /streams tab instead, which
carries live_status on every entry: measured against this channel, half a
second, and it says is_live rather than leaving it to be inferred.

Read this before relying on it
------------------------------
Both chat readers are unofficial. TikTokLive reverse-engineers TikTok's
Webcast protocol, and the YouTube readers speak the same private endpoint the
watch page uses. Neither is a contract: when a platform changes something,
that half goes quiet. So the tool says out loud what it connected to and what
it is waiting for -- a silence should never be ambiguous between "nobody is
chatting" and "this broke an hour ago".

Messages are printed in the order they ARRIVE, not the order they were sent.
The two sources have different lag, so a TikTok line and a YouTube line a
second apart can land the other way round. For following a conversation that
is fine; for anything that needs a true ordering it is not.
"""
import argparse
import os
import queue
import re
import sys
import threading
import time

# The two accounts this was written for, so it runs with no arguments.
YOUTUBE = "https://www.youtube.com/@TieulinhHOTA"
TIKTOK = "https://www.tiktok.com/@tieulinhhota/live"
POLL = 60.0                     # seconds between "is anybody live yet" checks

RESET = "\033[0m"
COLOUR = {"yt": "\033[38;5;203m",       # YouTube red
          "tt": "\033[38;5;51m",        # TikTok cyan
          "--": "\033[38;5;244m"}       # the tool talking about itself
TAG = {"yt": "YT", "tt": "TT"}


def _ansi():
    """Ask the Windows console to interpret escape codes, and say if it will."""
    if os.name != "nt":
        return sys.stdout.isatty()
    try:
        import ctypes
        k = ctypes.windll.kernel32
        # ENABLE_PROCESSED_OUTPUT | ENABLE_WRAP_AT_EOL_OUTPUT
        # | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(k.SetConsoleMode(k.GetStdHandle(-11), 7))
    except Exception:
        return False


# ------------------------------------------------------------- addresses ----
# A YouTube video id is eleven characters of [A-Za-z0-9_-]. Matching that with
# a regex rather than parsing the query means one function reads a popout chat
# link, a watch link, a youtu.be link and a bare id.
_YT_ID = re.compile(r"(?:^|[/=])([A-Za-z0-9_-]{11})(?:[&?/]|$)")


def youtube_target(text):
    """('video', id) for one stream, ('channel', url) for a whole channel.

    A channel address has no video id in it, so the id test decides which of
    the two this is; anything left is treated as a handle.
    """
    text = (text or "").strip()
    if not text:
        return None, None
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", text):
        return "video", text
    if "/watch" in text or "youtu.be/" in text or "live_chat" in text:
        match = _YT_ID.search(text)
        if match:
            return "video", match.group(1)
    if text.startswith("@"):
        return "channel", f"https://www.youtube.com/{text}"
    if "youtube.com/" in text:
        return "channel", text
    return "channel", f"https://www.youtube.com/@{text.lstrip('@')}"


def tiktok_user(text):
    """The @name of a TikTok LIVE link, without the @."""
    text = (text or "").strip()
    match = re.search(r"@([A-Za-z0-9_.]+)", text)
    if match:
        return match.group(1)
    return text.lstrip("@").strip("/") or None


# ----------------------------------------------------------------- lines ----
class Line:
    __slots__ = ("at", "where", "who", "what", "avatar", "role", "parts")

    def __init__(self, where, who, what, avatar=None, role=None, parts=None):
        self.at = time.time()
        self.where = where
        self.who = who
        self.what = what                # plain text, which is all a terminal
        self.avatar = avatar            # can show
        self.role = role                # "owner" | "mod" | "member" | None
        self.parts = parts              # for the overlay: see message_parts()


def why(exc, limit=90):
    """One line describing an exception, even when it carries no message.

    TimeoutError arrives with an empty str(), so splitlines() returns [] and
    taking [0] of it raises inside the handler that was there to report the
    first fault -- which is how a connect timeout came out as an IndexError
    traceback and killed the thread.
    """
    lines = str(exc).splitlines()
    return (lines[0][:limit] if lines else "") or type(exc).__name__


def note(out, where, text):
    """The tool saying something about a source, rather than a viewer."""
    out.put(Line("--", TAG.get(where, "··"), text))


# ---------------------------------------------------------------- lookup ----
def find_live(channel_url, out):
    """(video_id, title) of the channel's live right now, or (None, None)."""
    try:
        import yt_dlp
    except ImportError:
        note(out, "yt", "chưa cài yt-dlp.  pip install yt-dlp")
        return None, None

    url = channel_url.rstrip("/")
    if not url.endswith("/streams"):
        url += "/streams"
    # Flat, and only the newest few: a live stream is always at the top of the
    # streams tab, and asking for the whole listing would cost seconds.
    opts = {"quiet": True, "no_warnings": True,
            "extract_flat": "in_playlist", "playlistend": 5}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        note(out, "yt", f"không đọc được kênh: {why(exc, 120)}")
        return None, None
    for entry in info.get("entries") or []:
        if entry and entry.get("live_status") == "is_live":
            return entry.get("id"), entry.get("title") or ""
    return None, None


# --------------------------------------------------------------- youtube ----
def _youtube_chat(video_id, out, stop):
    """Pump one video's chat until it ends. Returns when there is no more.

    Two libraries, tried in order, because this is exactly the kind of tool
    that dies when one of them goes stale: pytchat is smaller and speaks only
    live chat, chat-downloader is the more actively kept.
    """
    try:
        import pytchat
    except ImportError:
        pytchat = None

    if pytchat is not None:
        try:
            # interruptable=False or pytchat installs a SIGINT handler,
            # which only the main thread is allowed to do: from here it
            # raises "signal only works in main thread" and never reads a
            # line. Measured against a live stream, which is the only way
            # this shows up at all.
            chat = pytchat.create(video_id=video_id, interruptable=False)
            while chat.is_alive() and not stop.is_set():
                for item in chat.get().sync_items():
                    a = item.author
                    role = ("owner" if getattr(a, "isChatOwner", False) else
                            "mod" if getattr(a, "isChatModerator", False) else
                            "member" if getattr(a, "isChatSponsor", False)
                            else None)
                    out.put(Line("yt", a.name, item.message,
                                 getattr(a, "imageUrl", None), role,
                                 message_parts(getattr(item, "messageEx",
                                                       None))))
                stop.wait(1.0)
            return
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            note(out, "yt", f"pytchat hỏng ({why(exc)}); thử chat-downloader")

    try:
        from chat_downloader import ChatDownloader
    except ImportError:
        note(out, "yt", "chưa cài thư viện đọc chat.  "
                        "pip install pytchat   (hoặc chat-downloader)")
        stop.wait(30)
        return

    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        for message in ChatDownloader().get_chat(url):
            if stop.is_set():
                break
            author = message.get("author") or {}
            images = author.get("images") or []
            badges = " ".join(str(b.get("title", "")).lower()
                              for b in (author.get("badges") or []))
            role = ("owner" if "owner" in badges else
                    "mod" if "moderator" in badges else
                    "member" if "member" in badges else None)
            out.put(Line("yt", author.get("name") or "?",
                         message.get("message") or "",
                         (images[-1].get("url") if images else None), role))
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as exc:
        note(out, "yt", f"dừng: {why(exc, 120)}")


def message_parts(message_ex):
    """pytchat's messageEx as [("t", text) | ("e", url, alt)], or None.

    item.message replaces every emoji with its :shortcode:, which is why a
    channel emoji came out as literal ":face-orange-biting-nails:" text.
    messageEx keeps the pieces apart, each emoji carrying an image url.

    A standard emoji is drawn as the CHARACTER, not the image: for those
    YouTube puts the character itself in emojiId, and a font glyph is sharper
    than a 24px png and needs no request. Only a channel's own emoji, which no
    font has, becomes an <img>.
    """
    if not message_ex:
        return None
    parts = []
    for piece in message_ex:
        if isinstance(piece, str):
            if piece:
                parts.append(("t", piece))
            continue
        if not hasattr(piece, "get"):
            continue
        ident = piece.get("id") or ""
        # An emojiId of one or two characters is the character; a custom one
        # is a long opaque id.
        if ident and len(ident) <= 4 and not ident.isascii():
            parts.append(("t", ident))
        elif piece.get("url"):
            parts.append(("e", piece["url"], piece.get("txt") or ""))
        elif piece.get("txt"):
            parts.append(("t", piece["txt"]))
    return parts or None


def youtube_reader(kind, value, out, stop, poll):
    while not stop.is_set():
        if kind == "video":
            note(out, "yt", f"đọc chat của video {value}")
            _youtube_chat(value, out, stop)
            note(out, "yt", "chat đã đóng")
            return                              # a fixed video does not return
        vid, title = find_live(value, out)
        if vid:
            note(out, "yt", f"đang live: {title[:60]}  ({vid})")
            _youtube_chat(vid, out, stop)
            note(out, "yt", f"chat đã đóng; {poll:.0f}s nữa tìm lại")
        else:
            note(out, "yt", f"kênh chưa live; thử lại sau {poll:.0f}s")
        if stop.wait(poll):
            return


# ---------------------------------------------------------------- tiktok ----
# TikTokLive names its failures, and they mean very different things: one is
# waited out, one is fixed with a key, one cannot be fixed from here at all.
# Lumping them into "could not connect" threw that away.
TT_REASON = {
    "UserOfflineError": "chưa live",
    "UserNotFoundError": "không có tài khoản này",
    "AgeRestrictedError": "live giới hạn tuổi, cần phiên đăng nhập",
    "SignatureRateLimitError": "hết hạn mức của sign server",
    "SignAPIError": "sign server trả lỗi",
    "WebsocketURLMissingError": "sign server không trả về URL websocket",
    "WebcastBlocked200Error": "TikTok chặn kết nối từ IP này",
}


# Set once a key has been loaded, so the advice below stops recommending the
# thing that is already done. Measured while chasing an HTTP 400 with a valid
# key in place: the quota was 2494/2500, so "try a key" was not only useless,
# it pointed at the one explanation already ruled out.
HAVE_KEY = False


def tt_reason(exc):
    """What a TikTok failure actually was, in words worth acting on."""
    named = TT_REASON.get(type(exc).__name__)
    if named:
        return named
    text = why(exc, 120)
    if "HTTP 400" in text:
        # TikTok refused the signed url. Without a key that is usually the
        # anonymous signature allowance; with one it is TikTok's own edge,
        # and waiting is the only thing that has ever helped.
        return text + (" -- TikTok từ chối chữ ký; để nó tự lùi và nối lại, "
                       "đừng khởi động lại liên tục" if HAVE_KEY
                       else " -- chữ ký ẩn danh bị từ chối, xem --sign-key")
    return text


def tiktok_reader(unique_id, out, stop, poll, ws_timeout=30.0):
    """Public LIVE chat of one TikTok account.

    TikTokLive needs the account NAME and nothing else -- no login, no token,
    not the streamer's and not yours. It is asyncio underneath, so it gets a
    thread and an event loop of its own, and a fresh client per attempt
    because a client that failed to connect is not reusable.
    """
    try:
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import CommentEvent, ConnectEvent, \
            DisconnectEvent
    except ImportError:
        note(out, "tt", "chưa cài TikTokLive.  pip install TikTokLive")
        return

    import asyncio

    # TikTok answers a burst of reconnects with HTTP 400 on the handshake --
    # seen after a session that had been running fine. Retrying at a fixed
    # rate is what turns one rejection into a queue of them, so each failure
    # in a row waits longer, and a connection that actually worked clears the
    # count.
    fails = 0

    while not stop.is_set():
        connected = {"yes": False}
        # An HTTP check before the websocket, because the two fail for
        # different reasons and only one of them is worth waiting out.
        # Measured: is_live answers in 0.6s while the websocket handshake was
        # timing out, which is how "the account is live but this machine
        # cannot reach the Webcast socket" became tellable from "not live".
        client = TikTokLiveClient(
            unique_id=f"@{unique_id}",
            # websockets defaults open_timeout to 10s, which is tight over a
            # slow or tunnelled route.
            ws_kwargs={"open_timeout": ws_timeout})
        try:
            if not asyncio.run(client.is_live()):
                note(out, "tt", f"@{unique_id} chưa live; "
                                f"thử lại sau {poll:.0f}s")
                if stop.wait(poll):
                    return
                continue
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            note(out, "tt", f"không hỏi được trạng thái live "
                            f"({tt_reason(exc)})")

        @client.on(ConnectEvent)
        async def _connected(_event):
            connected["yes"] = True
            note(out, "tt", f"đang live: @{unique_id}")

        @client.on(DisconnectEvent)
        async def _gone(_event):
            note(out, "tt", "mất kết nối")

        recent = {}                             # key -> when it arrived

        @client.on(CommentEvent)
        async def _comment(event):
            user = getattr(event, "user", None)
            who = (getattr(user, "nickname", None)
                   or getattr(user, "unique_id", None) or "?")
            # TikTokLive hands the same comment over twice on connect, which
            # showed as six messages printed twice in one second. Prefer the
            # library's own id; fall back to the pair, over a window short
            # enough that somebody genuinely repeating themselves still shows
            # up twice.
            key = None
            for path in ("common.msg_id", "base_message.msg_id", "msg_id"):
                node = event
                for part in path.split("."):
                    node = getattr(node, part, None)
                    if node is None:
                        break
                if node:
                    key = f"id:{node}"
                    break
            now = time.time()
            if key is None:
                key = f"{len(who)}|{who}|{event.comment}"
            for old_key, when in list(recent.items()):
                if now - when > 5.0:
                    recent.pop(old_key, None)
            if key in recent:
                return
            recent[key] = now
            avatar = None
            for name in ("avatar_thumb", "avatar_medium", "avatar_large"):
                image = getattr(user, name, None)
                urls = getattr(image, "url_list", None) if image else None
                if urls:
                    avatar = urls[0]
                    break
            out.put(Line("tt", who, event.comment, avatar))

        try:
            client.run()
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:
            # BaseException, not Exception: a connect that times out surfaces
            # as asyncio.CancelledError, which does NOT inherit from
            # Exception, so the narrower catch let it kill the thread with a
            # traceback and take the TikTok half down for good.
            note(out, "tt", f"không nối được: {tt_reason(exc)}")
        fails = 0 if connected["yes"] else fails + 1
        wait = min(poll * 2 ** min(fails - 1, 4), 900.0) if fails else poll
        note(out, "tt", f"thử lại sau {wait:.0f}s"
                        + (f" (hỏng {fails} lần liên tiếp)" if fails > 1 else ""))
        if stop.wait(wait):
            return


# ------------------------------------------------------------------ main ----
def sign_key(given=None):
    """The TikTok sign key, from the flag, the environment, or a local file.

    A file because the tool is launched by double-clicking a .cmd, where there
    is nowhere to type a flag -- and sign_key.txt is in .gitignore, so the key
    stays out of every commit. It is a secret: it belongs next to the tool on
    one machine, not in the source that gets pushed.
    """
    if given:
        return given.strip()
    from_env = os.environ.get("TIKTOK_SIGN_API_KEY")
    if from_env:
        return from_env.strip()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "sign_key.txt")
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    except OSError:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(
        description="Gộp chat YouTube live + TikTok LIVE vào một cửa sổ. "
                    "Đưa kênh, không cần link video: tool tự tìm live.")
    ap.add_argument("--youtube", default=YOUTUBE, metavar="KÊNH|VIDEO",
                    help="kênh (@tên hoặc link kênh) để tự tìm live, "
                         "hoặc link/id một video cụ thể")
    ap.add_argument("--tiktok", default=TIKTOK, metavar="KÊNH",
                    help="@tên hoặc link TikTok LIVE")
    ap.add_argument("--only", choices=("yt", "tt"), help="chỉ chạy một bên")
    ap.add_argument("--poll", type=float, default=POLL, metavar="GIÂY",
                    help=f"bao lâu kiểm tra lại khi chưa live (mặc định {POLL:.0f})")
    ap.add_argument("--web", nargs="?", type=int, const=8770, default=None,
                    metavar="PORT",
                    help="mở overlay cho OBS ở 127.0.0.1:PORT (mặc định 8770)")
    ap.add_argument("--ws-timeout", type=float, default=30.0, metavar="GIÂY",
                    help="chờ bắt tay websocket TikTok (mặc định 30)")
    ap.add_argument("--sign-key", default=None, metavar="KEY",
                    help="API key cho sign server của TikTokLive; không có thì "
                         "chạy ẩn danh và bị giới hạn theo IP. Cũng đọc từ "
                         "sign_key.txt hoặc biến môi trường "
                         "TIKTOK_SIGN_API_KEY")
    ap.add_argument("--log", metavar="FILE", help="ghi thêm ra file (không màu)")
    ap.add_argument("--no-colour", action="store_true")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:                       # a pipe that cannot be told
            pass
    colour = _ansi() and not args.no_colour

    key = sign_key(args.sign_key)
    if key:
        # TikTokLive cannot open the Webcast socket without a signature, and
        # unkeyed signatures are rationed per IP -- which is what a burst of
        # HTTP 400s on the handshake looks like from here.
        try:
            from TikTokLive.client.web.web_settings import WebDefaults
            WebDefaults.tiktok_sign_api_key = key
            globals()["HAVE_KEY"] = True
            # Four characters is enough to tell two keys apart and not enough
            # to be one: this line ends up in screenshots and pasted logs.
            print(f"TikTok : dùng sign key (…{key[-4:]})")
        except ImportError:
            pass
    poll = max(10.0, args.poll)                 # politeness floor

    kind, value = youtube_target(args.youtube)
    user = tiktok_user(args.tiktok)
    if args.only != "tt" and not value:
        print(f"không hiểu địa chỉ YouTube: {args.youtube}")
        return 2
    if args.only != "yt" and not user:
        print(f"không hiểu địa chỉ TikTok: {args.tiktok}")
        return 2

    hub = None
    if args.web:
        import overlay
        hub = overlay.Hub()
        url = overlay.serve(hub, port=args.web)
        print(f"Overlay : {url}")
        print("          OBS > Sources > + > Browser > URL o tren, "
              "bo trong Custom CSS.")

    out = queue.Queue()
    stop = threading.Event()
    threads = []
    if args.only != "tt":
        print(f"YouTube: {value}" + ("" if kind == "video" else "  (tự tìm live)"))
        threads.append(threading.Thread(
            target=youtube_reader, args=(kind, value, out, stop, poll),
            daemon=True))
    if args.only != "yt":
        print(f"TikTok : @{user}  (tự tìm live)")
        threads.append(threading.Thread(
            target=tiktok_reader,
            args=(user, out, stop, poll, args.ws_timeout), daemon=True))
    for t in threads:
        t.start()

    log = open(args.log, "a", encoding="utf-8") if args.log else None
    print("Ctrl+C để dừng.\n")
    try:
        while True:
            try:
                line = out.get(timeout=0.5)
            except queue.Empty:
                if not any(t.is_alive() for t in threads):
                    print("\ncả hai nguồn đã dừng.")
                    break
                continue
            clock = time.strftime("%H:%M:%S", time.localtime(line.at))
            plain = f"{clock}  [{line.who if line.where == '--' else TAG[line.where]}] " \
                    f"{line.what if line.where == '--' else line.who + ': ' + line.what}"
            if colour:
                c = COLOUR.get(line.where, "")
                if line.where == "--":
                    print(f"\033[38;5;244m{clock}  [{line.who}] "
                          f"{line.what}{RESET}")
                else:
                    print(f"\033[38;5;244m{clock}{RESET}  "
                          f"{c}[{TAG[line.where]}] {line.who}{RESET}: "
                          f"{line.what}")
            else:
                print(plain)
            if hub:
                hub.publish({"p": "sys" if line.where == "--" else line.where,
                             "who": line.who, "text": line.what,
                             "avatar": line.avatar, "role": line.role,
                             "parts": line.parts})
            if log:
                log.write(plain + "\n")
                log.flush()
    except KeyboardInterrupt:
        print("\ndừng.")
    finally:
        stop.set()
        if log:
            log.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
