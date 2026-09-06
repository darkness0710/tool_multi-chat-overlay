# Overlay in OBS

`web.cmd` (or `run.cmd --web`) serves a transparent page at
`http://127.0.0.1:8770/`. In OBS: **Sources → + → Browser**, that URL, and
leave **Custom CSS empty** — the page is already transparent. About 480 × 900
fits. Untick *Shutdown source when not visible* if you want chat to keep
running while the scene is hidden.

Sample output:

```
21:45:00  [YT] live: Chủ nhật ko ch.ết biome  (sd9BBehBBTY)
21:45:00  [TT] live: @tieulinhhota
21:45:01  [YT] NguyenA: Hello
21:45:02  [TT] abc123: Xin chào
```

## URL options

Change these in the OBS URL box — no restart needed. They combine:
`?mark=tag&plate&fade=45&yt=d9a13b`.

```
?plate            dark blur plate behind each message
?fade=45          keep messages 45s instead of 30
?mark=tag         (default)  <ava> <name> [YT]
?mark=badge       small shape on the avatar corner
?mark=bar         vertical colour bar on the left
?mark=none        no platform marker
?yt=f08a7e        (default)  de-chroma'd red
?tt=25f4ee        (default)  TikTok teal
```

Hex digits only, no `#` — a query string is untrusted input, and a CSS custom
property accepts more than a colour, so anything else is dropped.

## Why it looks like this

The look is **your existing YouTube-chat userstyle** — same Montserrat, same
name pills, same owner / mod / member colours, same 30s fade. One addition: a
**platform-coloured ring on the avatar**, red for YouTube, teal for TikTok.

**Text that survives a bright game.** The userstyle uses white text with *one*
soft offset `text-shadow`: readable on dark scenes, invisible on snow, sand or
bright stone. This overlay outlines text in **eight directions** before the
soft shadow, so contrast comes with the text whatever is under it.
`-webkit-text-stroke` is not used — Chromium draws that stroke *inward*, which
thins bold glyphs until they look broken. If a map is still too bright, add
`?plate`.

**Channel emoji.** pytchat's `item.message` replaces every emoji with a
`:shortcode:`, which is how a message ends up reading
`:face-orange-biting-nails:`. The overlay uses `messageEx` instead and gets
each part with its image URL. **Unicode** emoji are still drawn as
**characters**, not images: YouTube puts the character itself in `emojiId`, and
a font glyph is sharper than a 24px png and costs no request. Only
channel-specific emoji — which no font has — become `<img>`.

**Platform marker.** `tag` is the default and uses **square brackets**, not a
second solid chip: the name pill is already a solid block, and two of them side
by side on a game scene cost more than the information they carry. The `[YT]`
text is platform-coloured and shares the 8-direction outline, so it stays
readable on snow. **`badge`** puts a *shape* on the avatar — play triangle for
YouTube, music note for TikTok — so it is the one option that **doesn't depend
on colour**: red-green colourblind viewers can still tell them apart. Drawn as
inline SVG, no request. Not on the list: recolouring the name pill per
platform — that pill already means owner / mod / member, so taking it trades
one piece of information for another instead of adding.

**Housekeeping.** The userstyle fades messages out and leaves them in the DOM;
four hours of stream is thousands of invisible nodes. This page removes the
node after the fade.

**Why a page and not a console window.** OBS can capture a window, but a
console brings its own background, font and title bar, and cannot be
transparent. A Browser Source already is.

**Server-sent events**, not polling and not websockets: the data only travels
one way, SSE is the only option needing no library at either end, and it
reconnects by itself when OBS refreshes the source.

---

# Overlay trong OBS

`web.cmd` (hoặc `run.cmd --web`) phục vụ một trang trong suốt ở
`http://127.0.0.1:8770/`. Trong OBS: **Sources → + → Browser**, dán URL đó,
**Custom CSS để trống** — trang đã trong suốt sẵn. Rộng ~480, cao ~900 là vừa.
Bỏ tick *Shutdown source when not visible* nếu muốn chat vẫn chạy khi ẩn scene.

Kết quả:

```
21:45:00  [YT] đang live: Chủ nhật ko ch.ết biome  (sd9BBehBBTY)
21:45:00  [TT] đang live: @tieulinhhota
21:45:01  [YT] NguyenA: Hello
21:45:02  [TT] abc123: Xin chào
```

## Tham số URL

Đổi ngay trong ô URL của OBS, không phải khởi động lại tool. Ghép được với
nhau: `?mark=tag&plate&fade=45&yt=d9a13b`.

```
?plate            nền tối mờ sau mỗi tin
?fade=45          giữ tin 45 giây thay vì 30
?mark=tag         (mặc định)  <ava> <name> [YT]
?mark=badge       huy hiệu nhỏ ở góc avatar
?mark=bar         thanh màu dọc bên trái dòng
?mark=none        không đánh dấu gì
?yt=f08a7e        (mặc định)  đỏ đã hạ chroma
?tt=25f4ee        (mặc định)  xanh ngọc TikTok
```

Chỉ chữ số hex, không có dấu `#` — chuỗi query là dữ liệu không tin được, mà
một CSS custom property thì nhận nhiều thứ hơn một mã màu, nên phần còn lại bị
bỏ.

## Vì sao nó trông như vậy

Giao diện dùng **đúng userstyle bạn đang dùng cho chat YouTube** — cùng
Montserrat, cùng pill tên, cùng màu theo vai (owner / mod / member), cùng mờ
dần sau 30 giây. Thêm một thứ duy nhất: **vòng viền quanh avatar theo nền
tảng** — đỏ là YouTube, xanh ngọc là TikTok.

**Chữ không chìm vào nền game.** Userstyle gốc để chữ trắng với *một*
`text-shadow` mềm lệch một góc: nền tối thì đọc được, trên tuyết, cát hay
tường thành sáng thì mất hút. Overlay này viền chữ theo **tám hướng** rồi mới
đổ bóng mềm, nên chữ tự mang tương phản bất kể dưới nó là gì. Không dùng
`-webkit-text-stroke` vì Chromium vẽ viền **vào trong** nét chữ, làm chữ đậm
mảnh đi trông như vỡ. Bản đồ vẫn sáng quá thì thêm `?plate`.

**Emoji riêng của kênh.** `item.message` của pytchat thay mọi emoji bằng
`:shortcode:` dạng chữ — đó là lý do một tin ra thành
`:face-orange-biting-nails:`. Overlay dùng `messageEx`, tách được từng mảnh
kèm URL ảnh. Emoji **unicode** thì vẫn vẽ bằng **ký tự**, không phải ảnh:
YouTube để chính ký tự đó trong `emojiId`, mà glyph của font thì nét hơn ảnh
png 24px và không tốn một request. Chỉ emoji riêng của kênh — thứ không font
nào có — mới thành `<img>`.

**Đánh dấu nền tảng.** `tag` là mặc định, viết bằng **dấu ngoặc vuông** chứ
không phải một chip nền đặc thứ hai: pill tên đã là một khối đặc rồi, hai khối
đặc cạnh nhau trên nền game nặng hơn giá trị của thông tin chúng chở. Chữ
`[YT]` tô màu nền tảng và dùng chung viền 8 hướng, nên vẫn đọc được trên
tuyết. **`badge`** đặt một *hình* lên avatar — tam giác play cho YouTube, nốt
nhạc cho TikTok — nên là lựa chọn duy nhất **không phụ thuộc màu**: mù màu
đỏ-lục vẫn phân biệt được. Vẽ bằng SVG nội tuyến, không tải ảnh. Không có
trong danh sách: đổi màu pill tên theo nền tảng — pill đó đã mang nghĩa
owner / mod / member, cướp nó là đổi một thông tin lấy một thông tin khác chứ
không phải thêm.

**Dọn dẹp.** Userstyle làm tin nhắn mờ đi rồi để nguyên trong DOM; qua bốn
tiếng stream là hàng nghìn node vô hình. Trang này xoá node sau khi mờ xong.

**Vì sao là một trang chứ không phải cửa sổ console.** OBS bắt được cửa sổ,
nhưng console mang theo nền, font và title bar của nó, và không làm trong suốt
được. Browser Source thì trong suốt sẵn.

**Server-sent events**, không phải polling cũng không phải websocket: dữ liệu
chỉ đi một chiều, SSE là cách duy nhất không cần thư viện ở cả hai đầu, lại tự
nối lại khi OBS refresh source.
