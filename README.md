# Multi-chat overlay

One window showing the chat of **someone else's** YouTube + TikTok livestream.
No login, no API key. You give it a **channel**, not a video link — it finds
the live video itself, and waits if the channel isn't live yet.

## Run this

| file | what it does |
|---|---|
| **`web.cmd`** | double-click → overlay for OBS at `http://127.0.0.1:8770/` |
| **`run.cmd`** | same feed, terminal only |
| **`Install.cmd`** | build / repair the environment (`run.cmd` does it itself the first time) |

```
run.cmd --youtube @AiDo --tiktok @AiDo     other channels
run.cmd --youtube https://youtu.be/XXXX    one exact video, no searching
run.cmd --only yt                          one side only
run.cmd --log chat.txt                     also write to a file
run.cmd --web 9000                         different port
run.cmd --help                             everything else
```

**OBS:** Sources → + → Browser, URL `http://127.0.0.1:8770/`, Custom CSS
**empty**. About 480 × 900.

**TikTok drops out?** It needs a sign key — 3 steps:

1. `git update-index --skip-worktree sign_key.txt` — once, so your key can't be committed
2. copy your API key from <https://www.eulerstream.com/dashboard> (free plan)
3. paste it on the blank line in `sign_key.txt`, save, run `web.cmd`

More in [tiktok.md](documents/tiktok.md).

## Details

- [documents/install.md](documents/install.md) — install, common errors
- [documents/overlay.md](documents/overlay.md) — OBS, URL options (`?plate`, `?fade`, `?mark`, `?yt`, `?tt`)
- [documents/tiktok.md](documents/tiktok.md) — why TikTok drops, sign key
- [documents/notes.md](documents/notes.md) — design decisions, and what not to trust it with

---

# Gộp chat YouTube + TikTok

Một cửa sổ hiện chat livestream của **người khác**, cả YouTube lẫn TikTok.
Không cần đăng nhập, không cần API key. Đưa **kênh**, không cần link video —
tool tự tìm kênh đang live ở video nào, chưa live thì chờ.

## Chạy cái này

| file | làm gì |
|---|---|
| **`web.cmd`** | bấm đúp → overlay cho OBS ở `http://127.0.0.1:8770/` |
| **`run.cmd`** | y hệt, nhưng chỉ hiện trong cửa sổ dòng lệnh |
| **`Install.cmd`** | dựng / sửa môi trường (`run.cmd` tự làm lần đầu) |

```
run.cmd --youtube @AiDo --tiktok @AiDo     kênh khác
run.cmd --youtube https://youtu.be/XXXX    một video cụ thể, không tự tìm
run.cmd --only yt                          chỉ một bên
run.cmd --log chat.txt                     ghi thêm ra file
run.cmd --web 9000                         cổng khác
run.cmd --help                             các tuỳ chọn còn lại
```

**OBS:** Sources → + → Browser, URL `http://127.0.0.1:8770/`, Custom CSS
**để trống**. Rộng ~480, cao ~900.

**TikTok hay đứt?** Cần sign key — 3 bước:

1. `git update-index --skip-worktree sign_key.txt` — chạy một lần, để key không bị commit
2. vào <https://www.eulerstream.com/dashboard> copy API key (gói miễn phí)
3. dán key vào dòng trống trong `sign_key.txt`, lưu, chạy `web.cmd`

Chi tiết ở [tiktok.md](documents/tiktok.md).

## Chi tiết

- [documents/install.md](documents/install.md) — cài đặt, lỗi hay gặp
- [documents/overlay.md](documents/overlay.md) — OBS, tham số URL (`?plate`, `?fade`, `?mark`, `?yt`, `?tt`)
- [documents/tiktok.md](documents/tiktok.md) — vì sao TikTok đứt, sign key
- [documents/notes.md](documents/notes.md) — các quyết định thiết kế, và điều không nên tin
