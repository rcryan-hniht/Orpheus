# Xác minh TermMusic MVP

Ngày kiểm tra: 2026-11-01. Python 3.14.4 trong virtualenv của workspace.

| Hạng mục | Kết quả |
| --- | --- |
| `python -m pytest -q -rs` | 27 passed, 2 skipped |
| `python -m ruff check src tests` | Passed |
| `python -m ruff format --check src tests` | Passed |
| `python -m compileall -q src` | Passed |
| CLI `--help`, đường dẫn lỗi, cấu hình YouTube thiếu key | Passed |
| Build wheel bằng pip, không cài lại dependencies | Passed |
| Danh mục CC BY 3.0 mẫu | Qua validation của provider |
| mpv giải mã WAV tự tạo bằng `--ao=null` | Exit 0 |

Các test chạy được kiểm tra quét/validation nguồn nhạc, metadata-only YouTube,
SQLite sau khi mở lại, lyrics cache/404/offline và dữ liệu lỗi, LRC/delay, routing
IPC/event/error/EOF, quyền tách local, cache và xử lý lỗi của tiến trình Demucs giả.

Sol 6.1 xhigh đã review và xác nhận sửa các lỗi sau bằng kiểm tra logic riêng:

1. EOF của bài cũ không làm đánh dấu bài vừa tải là đã kết thúc.
2. Đóng tài nguyên không dùng nhầm cờ `_closed` của Textual và vẫn tiếp tục khi
   worker bị hủy hoặc một service gặp lỗi đóng.
3. Snapshot cũ không dùng EOF để ghi đè lựa chọn bài mới của người dùng.

Kiểm tra logic UI riêng trích xuất phương thức thật, không chạy framework Textual;
nó bổ sung cho review, không thay thế test tích hợp giao diện.

## Những phần chưa được xác minh trực tiếp

- Shell không truy cập được PyPI. Đã dùng dependencies thật có sẵn ở cache local
  để chạy backend/CLI/lint; Textual không có sẵn nên toàn bộ `test_app.py` bị skip.
  Các test headless cho search, queue, phím tắt, lyrics, karaoke, EOF và shutdown
  đã được viết nhưng cần cài dependencies theo README để chạy.
- Sandbox chặn Unix socket. Test điều khiển mpv thật qua IPC bị skip; test routing
  dùng stream trong bộ nhớ vẫn chạy. Giải mã WAV qua mpv thành công chưa xác minh
  phát âm thanh qua thiết bị Ubuntu/Wayland thật.
- Không tải model hoặc chạy inference Demucs thật. Không gọi LRCLIB/YouTube live
  hoặc phát URL online trong shell; các API được mô phỏng trong test.
- `.agents` và `.codex` là mount chỉ đọc. Cấu hình TOML được parse, kiểm tra liên
  kết file và đóng gói ở `agent-config/` cùng `orpheus-agent-config.zip`; chưa
  được cài vào hai thư mục host đó.

Chạy lại toàn bộ lệnh kiểm thử trên Ubuntu có mạng và dependencies đầy đủ trước
khi coi các phần tích hợp bị skip là đã được xác minh.
