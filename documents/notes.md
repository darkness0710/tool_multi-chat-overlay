# Design decisions, and what not to trust it with

## Its own venv, not the project's

`TikTokLive` drags in protobuf, httpx and a websocket stack; the video-cutting
pipeline next door runs on numpy, opencv and yt-dlp. Installing one on top of
the other risks the dependency resolver picking a version that breaks **the
thing that repository exists to do** — just to run a chat window. Keeping them
apart costs one folder (`.venv` inside this directory, already in
`.gitignore`).

That also makes this folder **self-contained**: it imports nothing from `tlh/`,
and no script points outside it. Copy the folder elsewhere and it runs.

## Finding the live stream without an API key

The "official" way is YouTube Data API `search.list` with `eventType=live`, but
it **needs an API key and costs 100 quota units per call** — polling all evening
burns the default daily allowance.

Instead the tool reads the channel's `/streams` tab with yt-dlp: every entry
already carries `live_status`. Measured on this very channel: **0.5 seconds,
one request, no key, no quota.**

```
live_status=is_live      sd9BBehBBTY  Chủ nhật ko ch.ết biome
live_status=was_live     GxlsvhRyDSg  Thứ 7 máu chảy về stream ^_^
```

`@channel/live` is not used, even though it also resolves to the right id,
because it **doesn't say whether that video is still live or already over** —
which is the actual question.

## Reading chat without an API key either

`pytchat` and `chat-downloader` call the same endpoint the browser's watch page
calls. The tool tries `pytchat` first and falls back to `chat-downloader` when
it breaks — **and says that it switched**.

## Before you trust it

**Both chat readers are unofficial libraries.** `TikTokLive` is a reverse
engineering of TikTok's Webcast protocol. If a platform changes something, that
side goes quiet — so the tool always prints **"live: …"** per side when it
connects, and **"not live; retrying in Ns"** when it doesn't. A silence is
never ambiguous between "nobody is chatting" and "it broke a while ago".

**Line order is ARRIVAL order, not send order.** The two sources have different
latency, so two messages a second apart can show up reversed. Fine for
watching; useless as evidence of timing.

**Casterlabs can't do this** — it merges chat from platforms *you have connected
an account to*; there is no box for pasting someone else's channel.

## If one side breaks

```
.venv\Scripts\python.exe -m pip install -U -r requirements.txt
```

Or delete `.venv` and run `run.cmd` again to rebuild from scratch.

---

# Các quyết định thiết kế, và điều không nên tin

## Môi trường riêng, không dùng venv của dự án

`TikTokLive` kéo theo protobuf, httpx và một tầng websocket; pipeline cắt video
bên cạnh chạy trên numpy, opencv và yt-dlp. Cài chồng lên nhau là có rủi ro
trình giải phụ thuộc chọn một phiên bản làm hỏng **chính thứ mà repo kia sinh
ra để làm** — chỉ để chạy một cửa sổ chat. Tách ra chỉ tốn một thư mục (`.venv`
trong chính thư mục này, đã nằm trong `.gitignore`).

Cũng vì thế thư mục này **tự đứng được**: không import gì từ `tlh/`, không
script nào trỏ ra ngoài. Copy nguyên thư mục sang chỗ khác là chạy được.

## Tìm live không cần API key

Cách "chính thức" là `search.list` với `eventType=live` của YouTube Data API,
nhưng nó **cần API key và tốn 100 quota units mỗi lần gọi** — poll cả buổi tối
là hết hạn mức mặc định trong ngày.

Thay vào đó tool đọc tab `/streams` của kênh bằng yt-dlp: mỗi mục có sẵn
`live_status`. Đo trên chính kênh này: **0,5 giây, một request, không key,
không quota.**

```
live_status=is_live      sd9BBehBBTY  Chủ nhật ko ch.ết biome
live_status=was_live     GxlsvhRyDSg  Thứ 7 máu chảy về stream ^_^
```

Không dùng `@kênh/live` dù nó cũng ra đúng id, vì nó **không nói cho biết video
đó còn đang live hay đã kết thúc** — mà đó chính là câu hỏi cần trả lời.

## Đọc chat cũng không cần API key

`pytchat` và `chat-downloader` gọi thẳng endpoint mà trang xem của trình duyệt
vẫn gọi. Tool thử `pytchat` trước, hỏng thì tự chuyển sang `chat-downloader`
**và nói ra là đã chuyển**.

## Điều cần biết trước khi tin nó

**Cả hai bên đọc chat đều là thư viện không chính thức.** `TikTokLive` là bản
dịch ngược giao thức Webcast của TikTok. Nền tảng đổi gì đó là bên đó câm — nên
tool luôn in dòng **"đang live: …"** cho từng bên khi nối được, và in **"chưa
live; thử lại sau Ns"** khi chưa. Một khoảng lặng không bao giờ mơ hồ giữa
"không ai chat" và "hỏng từ nãy".

**Thứ tự dòng là thứ tự ĐẾN, không phải thứ tự gửi.** Hai nguồn độ trễ khác
nhau, nên hai câu cách nhau một giây có thể hiện ngược. Theo dõi thì không sao;
làm bằng chứng thời điểm thì không dùng được.

**Casterlabs không làm được việc này** — nó gộp chat của những nền tảng *bạn đã
kết nối tài khoản*, không có ô để dán kênh của người khác.

## Nếu một bên hỏng

```
.venv\Scripts\python.exe -m pip install -U -r requirements.txt
```

Xoá thư mục `.venv` rồi chạy lại `run.cmd` là dựng lại từ đầu.
