# Install

Normally there is **nothing to do**: double-click `web.cmd` and the first run
builds the environment and downloads the libraries, 1–2 minutes. This file is
for when that fails, or when you want to do it by hand.

## Prerequisites

**None.** A brand-new machine with no Python works: `Install.cmd` looks for it,
**installs it** if it isn't there, and never asks for Administrator.

No YouTube or TikTok account, no API key, no OBS (OBS is only for the overlay).

### How it installs Python by itself

`get_python.ps1` does three things, in order:

1. **Looks** for Python 3.10+ everywhere it can hide — `py`, `python`, plus
   `%LOCALAPPDATA%\Programs\Python\` and `Program Files`. It has to scan places
   **not on PATH**, because right after winget installs it, the running
   process's PATH knows nothing about it. The `WindowsApps` copy is skipped —
   that's a Microsoft Store stub, not Python.
2. If there is none: **`winget install --scope user`** — no Administrator.
3. If winget is broken or missing: **download the python.org installer** and run
   it with `InstallAllUsers=0`, also without Administrator.

One detail in step 3 matters more than it looks: **the newest version is not the
newest installer**. Once a Python line goes security-fix-only, CPython ships
source only. Measured on 3.12: **3.12.11 through 3.12.14 have no `.exe` at
all**, the newest one with an installer is **3.12.10**. So the script HEADs each
version before downloading — grabbing the top of the list 404s on exactly the
machines this branch exists to serve.

## One click

```
Install.cmd            build it, or leave it alone if it's already there
Install.cmd -u         update the libraries to their latest
Install.cmd -f         throw the environment away and build it again
```

It runs three steps and **says which one failed**: create the venv, install the
libraries, then verify with a real `import` and `pip check`. Only then does it
report success.

`run.cmd` builds it on first use anyway, so `Install.cmd` is for the two cases
that can't serve: **installing ahead of time**, and **repairing**.

## By hand

```
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Check:

```
.venv\Scripts\python.exe -c "import TikTokLive, yt_dlp, pytchat; print('ok')"
.venv\Scripts\python.exe -m pip check
```

`No broken requirements found` means done.

## Common errors

### `may nay chua co Python`

Not installed, or installed without ticking "Add to PATH". Re-open the Python
installer → **Modify** → tick it, or reinstall. If typing `python` opens the
**Microsoft Store**, that's a Windows stub, not real Python — get the official
build from python.org.

### `Python cua may nay qua cu`

Needs **3.10+**. Not an arbitrary number: `TikTokLive`, `TikTokLiveProto`,
`EulerApiSdk` and `yt-dlp` all declare `Requires-Python >=3.10`. Install a newer
one, then run `Install.cmd -f`.

### `Duong dan thu muc nay qua dai cho Windows`

Windows 10 and 11 **still ship with Long Path off**, so every path must stay
under **260 characters**. And `EulerApiSdk` is a generated client with filenames
like:

```
record_string_is_live_boolean_room_id_string_or_null_additional_property.py
```

Measured: the deepest path the install creates is **156 characters** from this
folder. So the folder holding it must not exceed ~100 characters.

Hit for real while testing: pip downloaded almost everything, then died with
`No such file or directory` on exactly that file. `Install.cmd` now **checks
before downloading**, so you find out immediately instead of after the wait.

Fastest fix: move the whole folder somewhere short, e.g. `C:\chat_merge`.
Alternative (needs Administrator): enable Windows Long Paths.

### pip says `Access is denied` partway through

An antivirus is holding a `.pyd` file while pip writes it. Happened once
building this environment. Re-run the install command; verify with `pip check`
rather than trusting the error line — that time pip complained but the file had
been written.

### `chưa cài TikTokLive` / `chưa cài thư viện nào cho YouTube`

The environment exists but a package is missing:

```
.venv\Scripts\python.exe -m pip install -U -r requirements.txt
```

### Rebuild from scratch

`Install.cmd -f`, or delete `.venv` by hand and run `web.cmd`.

## Libraries, and why

| package | for |
|---|---|
| `TikTokLive` | read TikTok LIVE chat by account name, no login |
| `yt-dlp` | find which video a YouTube channel is live on — one request, no API key |
| `pytchat` | read YouTube chat, no API key |
| `chat-downloader` | fallback when `pytchat` breaks |

Both chat readers are **unofficial** — they talk to the watch page's internal
endpoints. If a platform changes something, that side goes quiet; the fix is to
update: `Install.cmd -u`.

TikTok also needs a sign key to stay connected — see [tiktok.md](tiktok.md).

---

# Cài đặt

Bình thường thì **không phải làm gì cả**: bấm đúp `web.cmd`, lần đầu nó tự dựng
môi trường và tải thư viện, mất 1–2 phút. File này dành cho lúc việc đó hỏng,
hoặc lúc bạn muốn tự tay.

## Cần sẵn

**Không cần gì cả.** Máy mới tinh chưa có Python cũng chạy được: `Install.cmd`
tự tìm, không thấy thì **tự cài**, và không hỏi quyền Administrator.

Không cần tài khoản YouTube hay TikTok, không cần API key, không cần OBS (OBS
chỉ dùng khi muốn overlay).

### Nó tự cài Python thế nào

`get_python.ps1` làm ba việc, theo thứ tự:

1. **Tìm** Python 3.10+ ở mọi chỗ nó có thể nấp — `py`, `python`, và cả
   `%LOCALAPPDATA%\Programs\Python\` lẫn `Program Files`. Phải quét cả những chỗ
   **không nằm trên PATH**, vì sau khi winget cài xong thì PATH của tiến trình
   đang chạy chưa biết gì về nó. Bản trong `WindowsApps` bị bỏ qua — đó là stub
   mở Microsoft Store, không phải Python.
2. Không có thì **`winget install --scope user`** — không cần Administrator.
3. winget hỏng hoặc máy không có winget thì **tải installer python.org** và chạy
   với `InstallAllUsers=0`, cũng không cần Administrator.

Một chi tiết ở bước 3 quan trọng hơn vẻ ngoài: **bản mới nhất không phải bản có
installer**. Khi một dòng Python chuyển sang chỉ-vá-bảo-mật, CPython chỉ phát
hành mã nguồn. Đo thật trên 3.12: **3.12.11 đến 3.12.14 không có `.exe` nào**,
bản mới nhất còn installer là **3.12.10**. Nên script hỏi từng bản một bằng HEAD
rồi mới tải — lấy đại bản đầu danh sách là 404 trên đúng những máy mà nhánh này
sinh ra để phục vụ.

## Cài bằng một cú bấm

```
Install.cmd            dựng môi trường, có rồi thì để yên
Install.cmd -u         cập nhật thư viện lên bản mới nhất
Install.cmd -f         xoá sạch rồi dựng lại từ đầu
```

Nó làm ba bước và **nói rõ bước nào hỏng**: dựng venv, cài thư viện, rồi kiểm
tra bằng `import` thật và `pip check`. Xong mới báo xong.

`run.cmd` cũng tự dựng lần đầu, nên `Install.cmd` là dành cho hai việc mà
`run.cmd` không phục vụ được: **cài trước** cho lúc cần dùng ngay, và **sửa**
khi hỏng.

## Tự cài bằng tay

```
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -U pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Kiểm tra:

```
.venv\Scripts\python.exe -c "import TikTokLive, yt_dlp, pytchat; print('ok')"
.venv\Scripts\python.exe -m pip check
```

`pip check` in ra `No broken requirements found` là xong.

## Lỗi hay gặp

### `may nay chua co Python`

Chưa cài, hoặc cài rồi mà không tick "Add to PATH". Mở lại bộ cài Python →
**Modify** → tick lại, hoặc cài lại. Nếu gõ `python` mà **Microsoft Store hiện
lên** thì đó là stub của Windows, không phải Python thật — vẫn phải tải bản
chính thức ở python.org.

### `Python cua may nay qua cu`

Cần **3.10 trở lên**. Không phải chọn con số cho đẹp: `TikTokLive`,
`TikTokLiveProto`, `EulerApiSdk` và `yt-dlp` đều khai báo
`Requires-Python >=3.10`. Cài bản mới rồi chạy `Install.cmd -f`.

### `Duong dan thu muc nay qua dai cho Windows`

Windows 10 và 11 **vẫn tắt Long Path mặc định**, tức mọi đường dẫn phải dưới
**260 ký tự**. Mà `EulerApiSdk` là client sinh tự động, có những tên file như:

```
record_string_is_live_boolean_room_id_string_or_null_additional_property.py
```

Đo thật: đường dẫn sâu nhất mà bản cài tạo ra là **156 ký tự** tính từ thư mục
này. Nên thư mục chứa nó **không được dài quá ~100 ký tự**.

Gặp thật khi thử: pip tải xong gần hết rồi chết giữa chừng với `No such file or
directory` đúng ở cái file trên. Giờ `Install.cmd` **kiểm trước khi tải**, nên
bạn biết ngay thay vì chờ hết rồi mới hỏng.

Cách nhanh nhất: chuyển cả thư mục sang chỗ ngắn, ví dụ `C:\chat_merge`. Cách
khác (cần quyền Administrator): bật Long Path của Windows.

### pip báo `Access is denied` giữa chừng

Trình quét virus giữ file `.pyd` ngay lúc pip ghi. Gặp thật một lần khi dựng môi
trường này. Chạy lại lệnh cài là qua — và kiểm bằng `pip check` chứ đừng tin mỗi
dòng báo lỗi, vì lần đó pip kêu lỗi nhưng file đã ghi xong.

### `chưa cài TikTokLive` / `chưa cài thư viện nào cho YouTube`

Môi trường có nhưng thiếu gói:

```
.venv\Scripts\python.exe -m pip install -U -r requirements.txt
```

### Muốn dựng lại từ đầu

`Install.cmd -f`, hoặc xoá tay thư mục `.venv` rồi chạy `web.cmd`.

## Thư viện dùng và vì sao

| gói | để làm gì |
|---|---|
| `TikTokLive` | đọc chat TikTok LIVE bằng tên tài khoản, không cần đăng nhập |
| `yt-dlp` | tìm kênh YouTube đang live ở video nào — một request, không cần API key |
| `pytchat` | đọc chat YouTube, không cần API key |
| `chat-downloader` | dự phòng cho `pytchat` khi nó hỏng |

Hai thư viện đọc chat đều **không chính thức** — chúng nói chuyện với endpoint
nội bộ của trang xem. Nền tảng đổi gì đó là bên đó câm; cách sửa là cập nhật:
`Install.cmd -u`.

TikTok còn cần sign key mới trụ được lâu — xem [tiktok.md](tiktok.md).
