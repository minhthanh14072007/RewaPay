# Điểm Thưởng — Hệ thống quản lý hoàn tiền và điểm thưởng

Ứng dụng web mô phỏng nghiệp vụ ghi nhận giao dịch, tích lũy/đổi điểm, hoàn giao dịch và duyệt giao dịch giá trị cao. Ứng dụng chỉ dùng dữ liệu giả lập, chạy trên máy cá nhân và không kết nối ngân hàng, cổng thanh toán hay dịch vụ bên ngoài.

## Notebook nộp bài: Google Colab / Jupyter

Tệp [HeThong_HoanTien_DiemThuong.ipynb](./HeThong_HoanTien_DiemThuong.ipynb) là bản chạy độc lập trên Python 3, tự sinh dữ liệu và không cần cài thư viện hay upload tệp khác. Đây là hình thức Notebook theo yêu cầu học phần; ứng dụng web bên dưới là demo trực quan bổ sung.

- **Google Colab:** tải notebook lên Google Drive → nhấp phải tệp → **Open with → Google Colaboratory** → **Runtime → Run all**.
- **Jupyter Notebook/JupyterLab:** mở notebook trong Jupyter → **Run → Run All Cells**.
- Trạng thái notebook nằm trong RAM của kernel. Chạy lại cell tạo `book` để khởi tạo lại phiên demo.
- Notebook gồm quy tắc nghiệp vụ, cấu trúc dữ liệu và giải thuật, dashboard, tra cứu/sắp xếp, hàng chờ, đổi/hoàn điểm, 14 kiểm tra và benchmark.

## Chạy ứng dụng

- **Cách đơn giản:** nhấp đúp tệp `MO_APP.bat` trong thư mục `rewards_app`. Một cửa sổ máy chủ sẽ mở và ứng dụng được mở trong trình duyệt.
- Nếu Windows hỏi xác nhận mở tệp, chọn **Run** hoặc **Open**.
- Đóng cửa sổ máy chủ hoặc nhấn `Ctrl+C` trong cửa sổ đó để dừng ứng dụng.
- Nếu máy báo chưa có Python, cần cài Python 3 trước khi chạy.
- Cách thủ công: mở PowerShell tại thư mục này, chạy `python app.py` hoặc `py -3 app.py`, rồi mở `http://127.0.0.1:8000`.

Lần chạy đầu, ứng dụng sao chép bộ dữ liệu giả lập từ `data/sample_data.json` sang `data/store.json`. Các thay đổi được lưu nguyên tử vào `data/store.json` và tồn tại sau khi khởi động lại. Muốn khôi phục dữ liệu ban đầu, dừng máy chủ, xóa riêng tệp `data/store.json`, rồi chạy lại. Không sửa tệp mẫu nếu muốn giữ bản demo gốc.

## Chức năng

- Xem tổng tiền hoàn, điểm còn lưu hành, số giao dịch và giao dịch chờ duyệt.
- Ghi nhận giao dịch cho hội viên giả lập; giao dịch trên 5.000.000 ₫ được giữ chờ duyệt.
- Duyệt giao dịch theo FIFO hoặc ưu tiên số tiền lớn nhất.
- Tra cứu chính xác theo mã giao dịch; sắp xếp tăng/giảm theo số tiền.
- Đổi điểm lấy giá trị mô phỏng; hoàn giao dịch đã duyệt, nếu điểm thưởng chưa bị sử dụng.
- Hoàn tác thao tác gần nhất trong phiên máy chủ.

## Quy tắc nghiệp vụ minh họa

| Quy tắc | Giá trị trong bản demo |
| --- | --- |
| Hoàn tiền giao dịch được duyệt | 1% số tiền, làm tròn xuống đến VND nguyên |
| Tích điểm | 1 điểm cho mỗi 10.000 ₫, phần lẻ bị bỏ |
| Đổi điểm | Tối thiểu 100 điểm, bội số của 100 |
| Giá trị quy đổi | 1 điểm = 100 ₫ |
| Duyệt bổ sung | Giao dịch trên 5.000.000 ₫ chưa nhận thưởng cho đến khi được duyệt |
| Hoàn giao dịch | Thu hồi tiền hoàn và điểm chưa sử dụng; từ chối nếu điểm đã được đổi |

Đây là giả định phục vụ học tập, không phải điều khoản sản phẩm ngân hàng hay tư vấn tài chính. Dữ liệu mẫu, hội viên và giao dịch đều được tạo giả lập.

## Cấu trúc dữ liệu và độ phức tạp

| Cấu trúc theo bảng học phần | Cách cài đặt trong Python | Vị trí sử dụng và độ phức tạp |
| --- | --- | --- |
| List | `list` | Lưu giao dịch, hội viên, lịch sử đổi; duyệt O(n), thêm cuối O(1) trung bình; kết hợp merge sort để sắp xếp O(n log n) |
| Queue | `collections.deque` | Hàng chờ duyệt FIFO; lấy phần tử đầu O(1) |
| Stack | `list` | Lưu snapshot để hoàn tác; thêm/lấy đỉnh O(1), snapshot tốn O(n) bộ nhớ |
| Hash Table | `dict` | Chỉ mục mã giao dịch/hội viên; tra cứu trung bình O(1), xấu nhất O(n) |
| Heap | `heapq` | Ưu tiên giao dịch giá trị cao; dựng heap O(q), lấy phần tử O(log q); mỗi lần bấm trong demo còn quét n giao dịch nên tổng O(n + q) |

Đồ án chỉ chọn năm cấu trúc trong bảng này; không cài Trie, AVL hoặc Skip List vì phạm vi demo không cần gợi ý mã theo tiền tố hay cây tra cứu có thứ tự. Merge sort là thuật toán, không phải cấu trúc dữ liệu. `benchmarks.py` còn thực nghiệm Insertion Sort và Selection Sort cho Mục 7.3 của báo cáo; hai thuật toán này không thay đổi cách sắp xếp trên giao diện. Mỗi lần dựng dashboard, dữ liệu JSON được đọc vào bộ nhớ và lập lại các chỉ mục/hàng chờ; đây là lựa chọn đơn giản, phù hợp đồ án một máy và quy mô demo, không phải triển khai đa người dùng.

## Cây thư mục

```text
rewards_app/
├── app.py                 # HTTP server/API, chỉ bind vào 127.0.0.1
├── rewards.py             # Quy tắc nghiệp vụ, cấu trúc dữ liệu và thuật toán
├── HeThong_HoanTien_DiemThuong.ipynb # Notebook độc lập cho Colab/Jupyter
├── BAO_CAO.md              # Báo cáo theo outline PDF
├── PRESENTATION.md         # Kịch bản thuyết trình 15 phút
├── benchmarks.py           # Benchmark bản ứng dụng
├── data/
│   ├── sample_data.json   # Hội viên và giao dịch hoàn toàn giả lập
│   └── store.json         # Được tạo khi chạy lần đầu; dữ liệu làm việc
├── static/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── background.jpg    # Ảnh nền chính
│   └── mascots/
│       ├── bunny-directions.webp
│       ├── bunny-reactions.webp
│       └── LICENSE.txt   # Giấy phép của bộ ảnh mascot
└── tests/
    └── test_rewards.py
```

Ứng dụng mở đầu bằng màn hình giới thiệu RewaPay; nhấn **Khám phá RewaPay** để
vào dashboard. Linh vật thỏ ở màn hình này được dựng bằng HTML/CSS/JavaScript
thuần, không cần React hay cài thêm npm package. Hai sprite sheet nằm trong
`static/mascots/`; giấy phép MIT và thông tin bản quyền của bộ mascot được lưu
cùng thư mục.

## Kiểm thử

Từ thư mục `rewards_app`, chạy:

```powershell
python -m unittest discover -s tests -v
```

Kiểm thử bao gồm dữ liệu rỗng, một phần tử, tìm thấy/không tìm thấy, sắp tăng/giảm, giao dịch biên qua ngưỡng, hàng đợi FIFO/ưu tiên, đổi điểm, hoàn giao dịch, hoàn tác, lưu sau khởi động lại và dữ liệu không hợp lệ.

## API nội bộ

| Phương thức | Đường dẫn | Mục đích |
| --- | --- | --- |
| GET | `/api/state` | Dashboard, hội viên, hàng chờ và chỉ số |
| GET | `/api/transactions?sort=desc\|asc\|newest\|oldest` | Sắp theo số tiền giảm/tăng dần hoặc theo thời gian mới/cũ nhất |
| GET | `/api/transactions/search?id=GD0001` | Tra cứu theo mã |
| POST | `/api/transactions` | Ghi nhận giao dịch |
| POST | `/api/reviews/process` | Duyệt giao dịch `fifo` hoặc `priority` |
| POST | `/api/redemptions` | Đổi điểm |
| POST | `/api/refunds` | Hoàn giao dịch |
| POST | `/api/undo` | Hoàn tác thao tác gần nhất |

## Giới hạn và hướng mở rộng

Ứng dụng chưa có đăng nhập, phân quyền, cơ sở dữ liệu giao dịch, khóa sổ, nhật ký bất biến, kiểm thử tải hay tích hợp tài chính. Tệp JSON và hoàn tác trong bộ nhớ chỉ phù hợp với demo một tiến trình, một người dùng. Trước khi dùng thật cần thiết kế xác thực/phân quyền, lưu trữ giao dịch ACID, audit trail, chính sách điểm/hoàn tiền đã được phê duyệt và rà soát bảo mật.
