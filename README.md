# 🎵 Orpheus

**Orpheus** là ứng dụng nghe nhạc TUI (Terminal User Interface) hiện đại, nhẹ và mạnh mẽ trên Linux (hỗ trợ Wayland & X11) và macOS, được xây dựng bằng Python và framework Textual. Âm thanh được phát mượt mà qua mpv JSON IPC.

---

## ⚡ Cài đặt nhanh (1 dòng lệnh)

Chỉ cần chạy lệnh sau trong terminal để tải và cài đặt tự động:

```bash
curl -fsSL https://raw.githubusercontent.com/Chau-Phu-Thinh/Orpheus/main/install.sh | bash
```

Sau khi cài đặt xong, bạn có thể mở ứng dụng ngay lập tức bằng lệnh:

```bash
orpheus
```

*(Yêu cầu hệ thống: Python 3.11+ và `mpv`. Nếu máy chưa có `mpv`, hãy cài bằng `sudo apt install mpv` trên Ubuntu/Debian hoặc `brew install mpv` trên macOS).*

---

## ✨ Tính năng nổi bật (Features)

- **🎧 Phát nhạc Local-First**: Quét thư mục nhạc máy tính (`~/Music` hoặc tùy chọn qua `--music-dir`), hỗ trợ hầu hết định dạng âm thanh phổ biến: MP3, FLAC, Ogg, WAV, M4A, OPUS,... Đọc tags metadata (tên bài hát, ca sĩ, album, thời lượng) siêu tốc bằng `mutagen`.
- **⚡ Động cơ mpv hiệu năng cao**: Kết nối qua giao thức mpv JSON IPC ngầm, không mở cửa sổ video, không giật lag giao diện, xuất âm thanh trực tiếp qua PipeWire / PulseAudio.
- **📜 Synced Lyrics thời gian thực**: Tự động tra cứu và cuộn lời bài hát đồng bộ từng giây từ [LRCLIB](https://lrclib.net); hỗ trợ cả plain lyrics và lưu cache cục bộ SQLite 30 ngày.
- **⏱️ Chỉnh độ trễ (Delay) Lyrics trực tiếp**: Tinh chỉnh độ trễ lời bài hát ngay khi nghe bằng phím tắt `[` / `]` (±0.25s). Mức delay được lưu riêng cho từng bài vào database.
- **📋 Hàng đợi phát (Queue) bền bỉ**: Thêm bài (`e`), xóa bài (`Delete`), tự động chuyển bài tiếp theo khi hết nhạc. Toàn bộ hàng đợi được lưu liên tục vào SQLite, không sợ mất khi tắt app.
- **🎤 Tách giọng hát Karaoke (Demucs)**: Tạo bản beat không giọng hát (Instrumental) cục bộ bằng Demucs (`k`). Giữ nguyên tiến trình giây phát và trạng thái khi chuyển đổi giữa bản gốc và bản karaoke.
- **🎨 Giao diện tùy biến với Color Themes**: Tích hợp 5 chủ đề màu sắc ấn tượng (`github-dark-contrast`, `blackmetal`, `catppuccin-latte`, `sequoia-light-monochrome`, `github-light-contrast`), chuyển đổi ngay trong TUI hoặc qua cờ `--theme`.
- **🌐 Nguồn nhạc trực tuyến & YouTube Metadata**:
  - Hỗ trợ nguồn danh mục âm thanh HTTPS có giấy phép Creative Commons qua cờ `--catalog`.
  - Tra cứu metadata bài hát qua YouTube Data API v3 (`--youtube`).

---

## ⌨️ Phím tắt điều khiển (Shortcuts)

| Phím | Chức năng |
| :--- | :--- |
| **Enter** | Phát bài hát đang chọn |
| **`e`** | Thêm bài đang chọn vào hàng đợi phát (Queue) |
| **Tab** / **Shift+Tab** | Di chuyển focus giữa các khung (Search, Track List, Queue, Lyrics) |
| **Delete** | Xóa mục được chọn ra khỏi hàng đợi |
| **Space** | Tạm dừng (Pause) / Tiếp tục phát |
| **`s`** / **`n`** | Dừng hẳn phát / Chuyển sang bài tiếp theo |
| **`←`** / **`→`** | Tua lùi / Tua tiến 5 giây |
| **`-`** / **`+`** | Giảm / Tăng âm lượng |
| **`[`** / **`]`** | Giảm / Tăng delay lời bài hát 0.25 giây |
| **`r`** | Tải lại lời bài hát từ cache / API LRCLIB |
| **`k`** | Bật Karaoke (Instrumental) / Quay lại bản gốc |
| **Ctrl+Q** | Thoát ứng dụng |

---

## 🛠️ Tùy chọn dòng lệnh (CLI Options)

```bash
# Xem toàn bộ trợ giúp
orpheus --help

# Chỉ định thư mục nhạc cụ thể
orpheus --music-dir "$HOME/Music/Favorites"

# Chạy với danh mục nhạc mẫu có bản quyền
orpheus --catalog examples/catalog.json

# Khởi động với giao diện màu yêu thích
orpheus --theme github-dark-contrast

# Tìm kiếm metadata YouTube (cần YOUTUBE_API_KEY)
YOUTUBE_API_KEY="your_api_key" orpheus --youtube
```

---

## 💻 Cài đặt thủ công dành cho lập trình viên

```bash
git clone https://github.com/Chau-Phu-Thinh/Orpheus.git
cd Orpheus

python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Chạy kiểm thử & linter
pytest
ruff check src tests

# Chạy app
python -m orpheus --catalog examples/catalog.json
```

---

## 📄 Bản quyền & Đóng góp

Dự án được phân phối theo giấy phép mã nguồn mở. Mọi đóng góp, báo lỗi (issue) và pull request đều được hoan nghênh!
