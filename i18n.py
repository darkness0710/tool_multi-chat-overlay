"""Every line this tool says to a person, in one place, in two languages.

English is the default because the code, the comments and the documents a
contributor reads are English; Vietnamese is what the streamer this was
written for actually reads. Neither one can be the only one, so the strings
left the code and came here.

Named keys, not English-as-the-key. A key survives a reworded message, a
missing translation is a thing that can be found (see `missing()`), and one
file holds the whole vocabulary of the tool -- the same reason web.cmd calls
run.cmd instead of repeating it: one copy cannot drift.

Choosing the language, in the order the rest of the tool resolves settings:

    python merge_chat.py --lang vi       this run
    CHAT_MERGE_LANG=vi                   this shell
    LANG=vi   in config.txt              this machine, and the only one of the
                                         three a person who double-clicks a
                                         .cmd can reach

What is NOT here: run.cmd, Install.cmd and get_python.ps1 speak English only.
They run before there is a Python to ask, so they cannot read this file, and a
message catalogue written a second time in batch is a thing that goes stale.

argparse's own furniture -- "usage:", "options:", its error messages -- stays
English in both languages. That text belongs to the standard library, and
translating it would mean shipping a locale for it.
"""
DEFAULT = "en"
ENV = "CHAT_MERGE_LANG"

EN = {
    # ---------------------------------------------------------- youtube ----
    "yt.no_ytdlp": "yt-dlp is not installed.  pip install yt-dlp",
    "yt.channel_unreadable": "could not read the channel: {why}",
    "yt.pytchat_broke": "pytchat failed ({why}); trying chat-downloader",
    "yt.no_chat_lib": "no chat reader installed.  "
                      "pip install pytchat   (or chat-downloader)",
    "yt.stopped": "stopped: {why}",
    "yt.reading_video": "reading the chat of video {value}",
    "yt.chat_closed": "chat is closed",
    "yt.live": "live now: {title}  ({vid})",
    "yt.chat_closed_retry": "chat is closed; looking again in {poll}s",
    "yt.not_live": "channel is not live; retrying in {poll}s",

    # ----------------------------------------------------------- tiktok ----
    "tt.no_lib": "TikTokLive is not installed.  pip install TikTokLive",
    "tt.not_live": "@{user} is not live; retrying in {poll}s",
    "tt.status_failed": "could not read live status ({reason})",
    "tt.live": "live now: @{user}",
    "tt.disconnected": "connection lost",
    "tt.connect_failed": "could not connect: {reason}",
    "tt.retry": "retrying in {wait}s",
    "tt.retry_fails": " ({fails} failures in a row)",
    "tt.reason.offline": "not live",
    "tt.reason.no_user": "no such account",
    "tt.reason.age": "age-restricted live, needs a signed-in session",
    "tt.reason.rate": "sign server quota used up",
    "tt.reason.sign_api": "sign server returned an error",
    "tt.reason.no_ws": "sign server returned no websocket URL",
    "tt.reason.blocked": "TikTok blocked the connection from this IP",
    "tt.sig_refused_key": " -- TikTok refused the signature; let it back off "
                          "and reconnect, do not restart it over and over",
    "tt.sig_refused_anon": " -- the anonymous signature was refused, "
                           "see --sign-key",

    # --------------------------------------------------------- sign key ----
    "sign.ignored": "TikTok : sign key IGNORED -- this build of TikTokLive no "
                    "longer has WebDefaults.{attr}, so it runs anonymously "
                    "and will be rate-limited per IP. See requirements.txt",
    "sign.ignored_log": "sign key NOT loaded: WebDefaults has no {attr} "
                        "(TikTokLive too new?)",
    "sign.loaded": "TikTok : using sign key (…{tail})",
    "sign.loaded_log": "sign key loaded into TikTokLive",

    # ------------------------------------------------------- the banner ----
    "cli.log": "Log     : {path}  (send this file when reporting a fault)",
    "cli.bad_youtube": "not a YouTube address: {value}",
    "cli.bad_tiktok": "not a TikTok address: {value}",
    "cli.overlay": "Overlay : {url}",
    "cli.overlay_obs": "          OBS > Sources > + > Browser > the URL "
                       "above, leave Custom CSS empty.",
    "cli.overlay_zoom": "          Text too small or too big: Ctrl and +/-, "
                        "or Ctrl and the mouse wheel.",
    "cli.youtube": "YouTube: {value}",
    "cli.tiktok": "TikTok : @{user}",
    "cli.auto_find": "  (finds the live itself)",
    "cli.stop_hint": "Ctrl+C to stop.",
    "cli.both_stopped": "both sources have stopped.",
    "cli.stopped": "stopped.",
    "cli.stopped_log": "user stopped it with Ctrl+C",

    # ----------------------------------------------------------- --help ----
    "arg.description": "Merge a YouTube live chat and a TikTok LIVE chat into "
                       "one window. Give it a channel, not a video link: it "
                       "finds the live itself.",
    "arg.youtube": "a channel (@name or channel link) whose live to find, or "
                   "the link/id of one particular video; falls back to "
                   "YOUTUBE in config.txt",
    "arg.tiktok": "@name or TikTok LIVE link; falls back to TIKTOK in "
                  "config.txt",
    "arg.only": "run one side only",
    "arg.poll": "how long between checks while nothing is live "
                "(default {poll})",
    "arg.web": "serve the OBS overlay on 127.0.0.1:PORT (default 8770)",
    "arg.ws_timeout": "how long to wait for the TikTok websocket handshake "
                      "(default 30)",
    "arg.sign_key": "API key for TikTokLive's sign server; without one it "
                    "runs anonymously and is rate-limited per IP. Also read "
                    "from EULERSTREAM_API_KEY in config.txt or the "
                    "TIKTOK_SIGN_API_KEY environment variable",
    "arg.log": "also write to a file (no colour)",
    "arg.lang": "language of the messages: en or vi (default en). Also read "
                "from LANG in config.txt",
    "arg.channel_or_video": "CHANNEL|VIDEO",
    "arg.channel": "CHANNEL",
    "arg.seconds": "SECONDS",

    # -------------------------------------------------------- debug.log ----
    "log.capped": "log reached {mb}MB, nothing more is written",
    "log.versions_unreadable": "could not read",
    "log.not_installed": "NOT INSTALLED",
    "log.command": "command  : {argv}",
    "log.python": "python   : {version}  ({platform})",
    "log.libraries": "libraries: {versions}",
    "log.youtube": "YouTube  : {value}",
    "log.tiktok": "TikTok   : {value}",
    "log.sign_key": "sign key : {state}",
    "log.sign_have": "yes (…{tail})",
    "log.sign_none": "NONE",
    "log.events_only": "(events and faults only -- no chat content)",
    "log.traceback_end": "==== end of traceback ====",
    "log.counts": "messages received: {counts}",
    "log.end": "--- end ---",
}

VI = {
    # ---------------------------------------------------------- youtube ----
    "yt.no_ytdlp": "chưa cài yt-dlp.  pip install yt-dlp",
    "yt.channel_unreadable": "không đọc được kênh: {why}",
    "yt.pytchat_broke": "pytchat hỏng ({why}); thử chat-downloader",
    "yt.no_chat_lib": "chưa cài thư viện đọc chat.  "
                      "pip install pytchat   (hoặc chat-downloader)",
    "yt.stopped": "dừng: {why}",
    "yt.reading_video": "đọc chat của video {value}",
    "yt.chat_closed": "chat đã đóng",
    "yt.live": "đang live: {title}  ({vid})",
    "yt.chat_closed_retry": "chat đã đóng; {poll}s nữa tìm lại",
    "yt.not_live": "kênh chưa live; thử lại sau {poll}s",

    # ----------------------------------------------------------- tiktok ----
    "tt.no_lib": "chưa cài TikTokLive.  pip install TikTokLive",
    "tt.not_live": "@{user} chưa live; thử lại sau {poll}s",
    "tt.status_failed": "không hỏi được trạng thái live ({reason})",
    "tt.live": "đang live: @{user}",
    "tt.disconnected": "mất kết nối",
    "tt.connect_failed": "không nối được: {reason}",
    "tt.retry": "thử lại sau {wait}s",
    "tt.retry_fails": " (hỏng {fails} lần liên tiếp)",
    "tt.reason.offline": "chưa live",
    "tt.reason.no_user": "không có tài khoản này",
    "tt.reason.age": "live giới hạn tuổi, cần phiên đăng nhập",
    "tt.reason.rate": "hết hạn mức của sign server",
    "tt.reason.sign_api": "sign server trả lỗi",
    "tt.reason.no_ws": "sign server không trả về URL websocket",
    "tt.reason.blocked": "TikTok chặn kết nối từ IP này",
    "tt.sig_refused_key": " -- TikTok từ chối chữ ký; để nó tự lùi và nối "
                          "lại, đừng khởi động lại liên tục",
    "tt.sig_refused_anon": " -- chữ ký ẩn danh bị từ chối, xem --sign-key",

    # --------------------------------------------------------- sign key ----
    "sign.ignored": "TikTok : sign key BỊ BỎ QUA -- bản TikTokLive này không "
                    "còn WebDefaults.{attr}, nên chạy như ẩn danh và sẽ bị "
                    "giới hạn theo IP. Xem requirements.txt",
    "sign.ignored_log": "sign key KHÔNG nạp được: WebDefaults thiếu {attr} "
                        "(TikTokLive quá mới?)",
    "sign.loaded": "TikTok : dùng sign key (…{tail})",
    "sign.loaded_log": "sign key đã nạp vào TikTokLive",

    # ------------------------------------------------------- the banner ----
    "cli.log": "Log     : {path}  (gửi file này khi báo lỗi)",
    "cli.bad_youtube": "không hiểu địa chỉ YouTube: {value}",
    "cli.bad_tiktok": "không hiểu địa chỉ TikTok: {value}",
    "cli.overlay": "Overlay : {url}",
    "cli.overlay_obs": "          OBS > Sources > + > Browser > URL o tren, "
                       "bo trong Custom CSS.",
    "cli.overlay_zoom": "          Chu qua nho/qua to: Ctrl + dau +/- hoac "
                        "Ctrl + lan chuot.",
    "cli.youtube": "YouTube: {value}",
    "cli.tiktok": "TikTok : @{user}",
    "cli.auto_find": "  (tự tìm live)",
    "cli.stop_hint": "Ctrl+C để dừng.",
    "cli.both_stopped": "cả hai nguồn đã dừng.",
    "cli.stopped": "dừng.",
    "cli.stopped_log": "người dùng dừng bằng Ctrl+C",

    # ----------------------------------------------------------- --help ----
    "arg.description": "Gộp chat YouTube live + TikTok LIVE vào một cửa sổ. "
                       "Đưa kênh, không cần link video: tool tự tìm live.",
    "arg.youtube": "kênh (@tên hoặc link kênh) để tự tìm live, hoặc link/id "
                   "một video cụ thể; không có thì lấy YOUTUBE trong "
                   "config.txt",
    "arg.tiktok": "@tên hoặc link TikTok LIVE; không có thì lấy TIKTOK trong "
                  "config.txt",
    "arg.only": "chỉ chạy một bên",
    "arg.poll": "bao lâu kiểm tra lại khi chưa live (mặc định {poll})",
    "arg.web": "mở overlay cho OBS ở 127.0.0.1:PORT (mặc định 8770)",
    "arg.ws_timeout": "chờ bắt tay websocket TikTok (mặc định 30)",
    "arg.sign_key": "API key cho sign server của TikTokLive; không có thì "
                    "chạy ẩn danh và bị giới hạn theo IP. Cũng đọc từ "
                    "EULERSTREAM_API_KEY trong config.txt hoặc biến môi "
                    "trường TIKTOK_SIGN_API_KEY",
    "arg.log": "ghi thêm ra file (không màu)",
    "arg.lang": "ngôn ngữ thông báo: en hoặc vi (mặc định en). Cũng đọc từ "
                "LANG trong config.txt",
    "arg.channel_or_video": "KÊNH|VIDEO",
    "arg.channel": "KÊNH",
    "arg.seconds": "GIÂY",

    # -------------------------------------------------------- debug.log ----
    "log.capped": "log đã đạt {mb}MB, ngừng ghi từ đây",
    "log.versions_unreadable": "không đọc được",
    "log.not_installed": "CHƯA CÀI",
    "log.command": "lệnh     : {argv}",
    "log.python": "python   : {version}  ({platform})",
    "log.libraries": "thư viện : {versions}",
    "log.youtube": "YouTube  : {value}",
    "log.tiktok": "TikTok   : {value}",
    "log.sign_key": "sign key : {state}",
    "log.sign_have": "có (…{tail})",
    "log.sign_none": "KHÔNG có",
    "log.events_only": "(chỉ ghi sự kiện và lỗi -- không ghi nội dung chat)",
    "log.traceback_end": "==== hết traceback ====",
    "log.counts": "số tin nhận được: {counts}",
    "log.end": "--- kết thúc ---",
}

CATALOGUE = {"en": EN, "vi": VI}
LANGS = tuple(CATALOGUE)

_active = EN
_name = DEFAULT


def use(lang_name):
    """Switch language. An unknown name falls back to English rather than
    failing: a typo in config.txt must not stop a stream from being read."""
    global _active, _name
    _name = (lang_name or DEFAULT).strip().lower()[:2]
    if _name not in CATALOGUE:
        _name = DEFAULT
    _active = CATALOGUE[_name]
    return _name


def lang():
    """The language in force, already normalised to one of LANGS."""
    return _name


def t(key, **kw):
    """The message for `key` in the active language.

    Three fallbacks, all silent on purpose, because every caller here is
    already reporting something: an untranslated key drops to English, an
    unknown key comes back as itself, and a message whose placeholders do not
    match its arguments comes back unformatted. None of those is worth
    replacing a fault report with a KeyError.
    """
    text = _active.get(key) or EN.get(key)
    if text is None:
        return key
    if not kw:
        return text
    try:
        return text.format(**kw)
    except (KeyError, IndexError, ValueError):
        return text


def missing(lang_name):
    """Keys English has and `lang_name` does not -- for a check or a test."""
    return sorted(set(EN) - set(CATALOGUE.get(lang_name, {})))
