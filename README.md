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

## Set it up: `config.txt`

Everything you'd normally type lives in **`config.txt`**, next to `run.cmd` —
because the tool is meant to be double-clicked, and double-clicking gives you
nowhere to type. Fill in the lines and save:

```
EULERSTREAM_API_KEY=xyz
YOUTUBE=https://www.youtube.com/@TieulinhHOTA
TIKTOK=https://www.tiktok.com/@tieulinhhota/live
```

Leave a line empty and the built-in default is used. `#` lines and blank lines
are ignored.

**First, once per clone** — so your key can never be committed:

```
git update-index --skip-worktree config.txt
```

The key is free: <https://www.eulerstream.com/dashboard>. Without it TikTok
drops out every few minutes — see [tiktok.md](documents/tiktok.md).

## Command line

Flags beat `config.txt` when you want a one-off:

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

## Details

- [documents/install.md](documents/install.md) — install, common errors
- [documents/overlay.md](documents/overlay.md) — OBS, URL options (`?plate`, `?fade`, `?mark`, `?yt`, `?tt`)
- [documents/tiktok.md](documents/tiktok.md) — `config.txt`, the sign key, why TikTok drops
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

## Cài đặt: `config.txt`

Mọi thứ bình thường phải gõ tay đều nằm trong **`config.txt`** cạnh `run.cmd` —
vì tool được bấm đúp để chạy, mà bấm đúp thì không có chỗ gõ. Điền vào rồi lưu:

```
EULERSTREAM_API_KEY=xyz
YOUTUBE=https://www.youtube.com/@TieulinhHOTA
TIKTOK=https://www.tiktok.com/@tieulinhhota/live
```

Để trống dòng nào thì dùng mặc định có sẵn. Dòng `#` và dòng trống bị bỏ qua.

**Chạy một lần trước tiên** — để key không bao giờ bị commit:

```
git update-index --skip-worktree config.txt
```

Key miễn phí: <https://www.eulerstream.com/dashboard>. Không có key thì TikTok
cứ vài phút lại đứt — xem [tiktok.md](documents/tiktok.md).

## Dòng lệnh

Tham số dòng lệnh thắng `config.txt`, dùng khi cần đổi tạm một lần:

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

## Chi tiết

- [documents/install.md](documents/install.md) — cài đặt, lỗi hay gặp
- [documents/overlay.md](documents/overlay.md) — OBS, tham số URL (`?plate`, `?fade`, `?mark`, `?yt`, `?tt`)
- [documents/tiktok.md](documents/tiktok.md) — `config.txt`, sign key, vì sao TikTok đứt
- [documents/notes.md](documents/notes.md) — các quyết định thiết kế, và điều không nên tin
