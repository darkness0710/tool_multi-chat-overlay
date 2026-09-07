"""A debug log written without being asked, for someone who cannot read one.

The tool is double-clicked by people who will not pass --log, will not run it
from a terminal, and cannot copy a traceback out of a console window that
closes with the process. When something breaks, the only thing they can be
asked for is a file. So this writes one every run, whether or not anything
goes wrong.

It logs what the tool says about ITSELF and nothing else. Chat is not in it.
That is not a size decision: the file exists to be sent to a stranger, and
the messages in it were written by people who were talking to a streamer, not
filing a bug report. The two kinds of line travel by different routes in
merge_chat.py -- note() for the tool, out.put(Line(...)) for a viewer -- so
hooking note() gets every event and cannot accidentally get a message. Anyone
who does want the chat on disk already has --log.

Two things the console does not have and the file does:

  * A header. Versions of four libraries that break independently, the
    channels actually in use, and whether the sign key landed. Half the
    questions asked of a bug report are answered before it is written.
  * Full tracebacks. The reader threads catch BaseException and report one
    truncated line, deliberately: a viewer does not want a stack trace
    scrolling past the chat. But that line is not enough to fix anything, so
    the stack goes to the file, where it costs nobody anything.

The sign key never reaches it either -- four characters, the same as the
console gets.
"""
import io
import os
import sys
import time
import traceback

from i18n import t

CAP = 2 * 1024 * 1024           # events only, so this is already generous

_fh = None
_written = 0
_capped = False


def _stamp():
    return time.strftime("%H:%M:%S")


def _raw(text):
    """Append to the file, and stop for good once the cap is reached."""
    global _written, _capped
    if _fh is None or _capped:
        return
    try:
        _fh.write(text)
        _fh.flush()             # the interesting runs are the ones that crash
        _written += len(text)
        if _written >= CAP:
            _capped = True
            _fh.write(f"\n[{_stamp()}] -- "
                      + t("log.capped", mb=CAP // 1024 // 1024)
                      + " --\n")
            _fh.flush()
    except Exception:
        # A log that takes the tool down with it is worse than no log: this
        # runs on machines with antivirus holding files open and folders that
        # turn out to be read-only.
        pass


def write(text):
    """One event into the log, one timestamped line per line of text."""
    for line in str(text).splitlines() or [""]:
        _raw(f"[{_stamp()}] {line}\n")


def _versions():
    try:
        from importlib.metadata import version, PackageNotFoundError
    except ImportError:
        return t("log.versions_unreadable")
    out = []
    for name in ("TikTokLive", "yt-dlp", "pytchat", "chat-downloader"):
        try:
            out.append(f"{name} {version(name)}")
        except PackageNotFoundError:
            out.append(f"{name} " + t("log.not_installed"))
        except Exception:
            out.append(f"{name} ?")
    return ", ".join(out)


def start(path, youtube, tiktok, key=None):
    """Open the log, rotate the previous run out, and write the header.

    The previous run is kept as .1 and no further: the run being asked about
    is nearly always the last one or the one before it, and a non-technical
    user should not have to choose between eight files.
    """
    global _fh, _written, _capped
    _written, _capped = 0, False
    try:
        if os.path.exists(path):
            os.replace(path, path + ".1")
    except OSError:
        pass                    # held open by an editor; the open below wins
    try:
        _fh = io.open(path, "w", encoding="utf-8", errors="replace",
                      newline="\n")
    except OSError:
        _fh = None
        return False

    write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    write(t("log.command", argv=" ".join(sys.argv)))
    write(t("log.python", version=sys.version.split()[0],
            platform=sys.platform))
    write(t("log.libraries", versions=_versions()))
    write(t("log.youtube", value=youtube))
    write(t("log.tiktok", value=tiktok))
    # Four characters is enough to tell two keys apart and not enough to be
    # one. This file gets sent to other people; that is the point of it.
    write(t("log.sign_key",
            state=t("log.sign_have", tail=key[-4:]) if key
            else t("log.sign_none")))
    write(t("log.events_only"))
    write("-" * 58)
    return True


def event(where, text):
    """Something the tool said about a source. Never a chat message."""
    write(f"[{where}] {text}")


def exception(where, exc):
    """A full traceback, which the console deliberately does not show."""
    _raw(f"[{_stamp()}] ==== traceback ({where}) ====\n")
    _raw("".join(traceback.format_exception(type(exc), exc,
                                            exc.__traceback__)))
    _raw(f"[{_stamp()}] " + t("log.traceback_end") + "\n")


def install_hooks():
    """Catch what nothing else caught, including inside a thread.

    A crash in a reader thread prints to stderr and is gone the moment the
    window closes -- which is exactly when the log needs to have kept it.
    """
    import threading

    prev_thread = threading.excepthook
    prev_main = sys.excepthook

    def on_thread(args):
        exception(f"thread {args.thread.name if args.thread else '?'}",
                  args.exc_value)
        prev_thread(args)

    def on_main(kind, value, tb):
        exception("main", value)
        prev_main(kind, value, tb)

    threading.excepthook = on_thread
    sys.excepthook = on_main


def close(counts=None):
    """Close, after one line saying whether anything arrived at all.

    Counts, not content: "did any message reach the tool" is the first thing
    worth knowing when someone reports an empty overlay, and it separates a
    dead connection from a broken display without quoting anybody.
    """
    global _fh
    if _fh is None:
        return
    if counts:
        write(t("log.counts", counts=", ".join(
            f"{k}={v}" for k, v in sorted(counts.items()))))
    write(t("log.end"))
    try:
        _fh.close()
    except Exception:
        pass
    _fh = None
