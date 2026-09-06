# TikTok keeps dropping: why, and what to do

TikTokLive **cannot open the websocket without a signature**. It asks
`api.eulerstream.com` for one, and by default asks **anonymously** — a share
handed out per IP. Run out and TikTok refuses the handshake:

```
server rejected WebSocket connection: HTTP 400
```

That is why it connects, runs fine for a few minutes, then gets turned away
next time.

## Get a sign key — 3 steps

The **Community** plan is **$0 forever, 2,500 requests/day**, and only
*opening a connection* spends one, so a streaming session uses a few dozen.

**1. Open the file.** `sign_key.txt` already sits next to `run.cmd` — it ships
with the repo holding two comment lines and one empty line:

```
# EN: Paste your TikTok sign key on the line below. Get one free at https://www.eulerstream.com/dashboard
# VI: Dán sign key TikTok vào dòng dưới. Lấy miễn phí ở https://www.eulerstream.com/dashboard

```

**2. Get the key.** Open <https://www.eulerstream.com/dashboard>, sign in, and
copy your **API key** from the dashboard.

**3. Paste it in.** Put the key on the blank line under the comments and save.
No quotes, no `KEY=`, nothing else. Then double-click `web.cmd` — it reads the
file by itself. Lines starting with `#` and blank lines are skipped, so leave
the comments where they are.

The file exists because the tool is meant to be double-clicked, and
double-clicking gives you nowhere to type an argument.

### Keeping your key out of git

`sign_key.txt` is **tracked**, so the template travels with the repo — which
means your pasted key would otherwise show up in `git status` and could be
committed. Run this once per clone, before pasting:

```
git update-index --skip-worktree sign_key.txt
```

That tells git to ignore edits to a file it tracks. `git status` then stays
clean whatever the file holds, and the key cannot be committed by accident.
To undo it — only needed to change the template itself:

```
git update-index --no-skip-worktree sign_key.txt
```

Two other ways, same effect:

```
web.cmd --sign-key YOUR_KEY
setx TIKTOK_SIGN_API_KEY "YOUR_KEY"
```

(`setx` only takes effect in command windows opened afterwards.)

Priority: command-line argument → environment variable → `sign_key.txt`.

At startup the tool prints the **last four characters**, so you can tell which
key is in use without exposing it in a screenshot or a pasted log:

```
TikTok : using sign key (…Yzlk)
```

> **The key is a secret.** Don't commit it, don't paste it into a chat or an
> issue. If it leaks, create a new one on the dashboard and replace the
> contents of `sign_key.txt`.

Plainly: I **have not verified** that a key makes it stable, because getting
one belongs to your account. The plumbing is there and uses the library's own
path (`WebDefaults.tiktok_sign_api_key`); how much it saves you is something
only you can measure.

## Two things the tool already does

**Backs off on failure.** Retrying steadily every 60s is exactly what turns one
refusal into a queue of refusals. Each consecutive failure doubles the wait —
60 → 120 → 240 → 480 → 900 seconds (ceiling) — and a real connection clears the
counter.

**Says what actually failed.** TikTokLive names its error types, and they mean
very different things: some need only patience, some need a key, some cannot be
fixed from this machine. Collapsing them into "couldn't connect" throws that
away.

| message | meaning |
|---|---|
| `not live` | the account isn't streaming — just wait |
| `sign server quota for this IP exhausted` | use a sign key |
| `signature rejected, try --sign-key` | the HTTP 400 above |
| `TikTok is blocking this IP` | a key won't fix it; change network / VPN |
| `age-restricted live` | needs a logged-in session; this tool doesn't do that |

---

# TikTok hay đứt: vì sao và làm gì

TikTokLive **không mở được websocket nếu không có chữ ký**. Nó xin chữ ký từ
`api.eulerstream.com`, và mặc định xin **ẩn danh** — tức bị chia phần theo IP.
Hết phần thì TikTok từ chối cái bắt tay:

```
server rejected WebSocket connection: HTTP 400
```

Đó là lý do nó nối được, chạy ngon vài phút, rồi lần sau bị đuổi.

## Lấy sign key — 3 bước

Gói **Community** là **$0 vĩnh viễn, 2.500 request/ngày**, mà mỗi lần *mở kết
nối* mới tốn một request, nên một buổi stream chỉ dùng vài chục.

**1. Mở file.** `sign_key.txt` có sẵn cạnh `run.cmd` — nó đi kèm repo, bên
trong là hai dòng comment và một dòng trống:

```
# EN: Paste your TikTok sign key on the line below. Get one free at https://www.eulerstream.com/dashboard
# VI: Dán sign key TikTok vào dòng dưới. Lấy miễn phí ở https://www.eulerstream.com/dashboard

```

**2. Lấy key.** Vào <https://www.eulerstream.com/dashboard>, đăng nhập, copy
**API key** trong dashboard.

**3. Dán vào.** Dán key vào dòng trống dưới phần comment rồi lưu. Không dấu
nháy, không `KEY=`, không gì thêm. Rồi bấm đúp `web.cmd` — tool tự đọc file.
Dòng bắt đầu bằng `#` và dòng trống đều bị bỏ qua, nên cứ để nguyên comment.

Chọn cách file vì tool được bấm đúp để chạy, mà bấm đúp thì không có chỗ gõ
tham số.

### Giữ key không lọt vào git

`sign_key.txt` giờ **được track** để template đi theo repo — nghĩa là key bạn
dán vào sẽ hiện trong `git status` và có thể bị commit nhầm. Chạy một lần sau
khi clone, trước khi dán key:

```
git update-index --skip-worktree sign_key.txt
```

Lệnh này bảo git lờ đi mọi thay đổi của một file mà nó đang track. Từ đó
`git status` luôn sạch bất kể trong file có gì, và key không thể bị commit
nhầm. Muốn bỏ — chỉ cần khi sửa chính template:

```
git update-index --no-skip-worktree sign_key.txt
```

Hai cách khác, cùng tác dụng:

```
web.cmd --sign-key KEY_CUA_BAN
setx TIKTOK_SIGN_API_KEY "KEY_CUA_BAN"
```

(`setx` chỉ có tác dụng ở cửa sổ dòng lệnh mở sau đó)

Thứ tự ưu tiên: tham số dòng lệnh → biến môi trường → `sign_key.txt`.

Khi chạy, tool in **bốn ký tự cuối** của key để bạn biết nó đang dùng key nào
mà không lộ cả key ra ảnh chụp màn hình hay log dán đi:

```
TikTok : dùng sign key (…Yzlk)
```

> **Key là bí mật.** Đừng commit, đừng dán vào chat hay issue. Lỡ lộ thì vào
> dashboard tạo key mới và thay nội dung `sign_key.txt` — key cũ bỏ đi.

Nói thẳng: tôi **chưa kiểm chứng được** rằng key làm nó ổn định, vì lấy key là
việc thuộc tài khoản của bạn. Phần cắm key thì đã có và chạy đúng đường của
thư viện (`WebDefaults.tiktok_sign_api_key`); còn nó cứu được bao nhiêu thì
phải bạn thử mới biết.

## Hai thứ tool tự làm sẵn

**Lùi dần khi hỏng.** Thử lại đều đặn 60 giây chính là thứ biến một lần bị từ
chối thành một hàng dài bị từ chối. Mỗi lần hỏng liên tiếp chờ gấp đôi —
60 → 120 → 240 → 480 → 900 giây (trần) — và nối được thật thì xoá bộ đếm.

**Nói rõ hỏng vì cái gì.** TikTokLive đặt tên cho từng loại lỗi, mà chúng có ý
nghĩa rất khác nhau: cái thì chỉ cần chờ, cái cần key, cái không sửa được từ
máy này. Gộp hết thành "không nối được" là vứt đi thông tin đó.

| báo | nghĩa |
|---|---|
| `chưa live` | tài khoản chưa lên sóng — chỉ cần chờ |
| `hết hạn mức của sign server cho IP này` | dùng sign key |
| `chữ ký bị từ chối, thử --sign-key` | chính là HTTP 400 ở trên |
| `TikTok chặn kết nối từ IP này` | không sửa được bằng key; đổi mạng/VPN |
| `live giới hạn tuổi` | cần phiên đăng nhập, tool này không làm |
