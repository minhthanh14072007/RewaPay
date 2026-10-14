# ĐIỂM THƯỞNG
## Hệ thống quản lý hoàn tiền và điểm thưởng cho giao dịch

**Thời lượng đề xuất:** 15 phút trình bày + 5 phút demo + 5 phút hỏi đáp  
**Người trình bày:** cập nhật tên thành viên thật trước khi thuyết trình.

---

### Slide 1 — Bài toán và bối cảnh (1 phút)

- Một chương trình hội viên cần ghi nhận giao dịch và tính quyền lợi minh bạch.
- Khó khăn: tra cứu giao dịch, xử lý khoản giá trị cao, đổi/thu hồi điểm chính xác.
- Mục tiêu: xây demo có thể thao tác và giải thích được cấu trúc dữ liệu.
- Dữ liệu hoàn toàn giả lập; không kết nối ngân hàng.

**Lời dẫn:** “Đây là đồ án cấu trúc dữ liệu, không phải sản phẩm tài chính production.”

### Slide 2 — Ai sử dụng? (1 phút)

- Nhân viên vận hành: ghi nhận, tra cứu, duyệt giao dịch.
- Quản trị viên: theo dõi tổng hoàn và điểm đang lưu hành.
- Hội viên mô phỏng: kiểm tra số dư, đổi điểm.
- Tập trung vào luồng giao dịch bán lẻ mẫu.

### Slide 3 — Phạm vi và quy tắc (30 giây)

- Hoàn tiền: 1% giao dịch được duyệt, làm tròn xuống VND.
- Tích điểm: 1 điểm / 10.000 ₫.
- Giao dịch trên 5.000.000 ₫ phải chờ duyệt.
- Đổi điểm: tối thiểu 100, theo bội số 100; 1 điểm = 100 ₫.
- Hoàn giao dịch bị chặn nếu điểm đã đổi.

### Slide 4 — Môi trường chạy (30 giây)

```text
Notebook Python (Colab/Jupyter, sản phẩm chính)
Ứng dụng web cục bộ (demo bổ sung): HTML/JS → app.py → rewards.py → JSON
```

- Công cụ chạy là Google Colab/Jupyter; chọn Run All.
- Không cần giải thích sâu công nghệ giao diện; thời gian tập trung cho thuật toán.

### Slide 5 — Cấu trúc dữ liệu (2,5 phút)

| Cấu trúc | Dùng ở đâu? | Vì sao? |
| --- | --- | --- |
| List | Danh sách giao dịch | Dễ duyệt và sắp xếp |
| Queue (`deque`) | Chờ duyệt FIFO | Lấy đầu O(1) |
| Stack (`list`) | Hoàn tác thao tác | LIFO, push/pop O(1) |
| Hash Table (`dict`) | Tìm theo mã | Trung bình O(1) |
| Heap (`heapq`) | Chọn giao dịch tiền cao nhất | Lấy ưu tiên O(log q) sau khi dựng |

### Slide 6 — Thuật toán tra cứu và sắp xếp (2,5 phút)

- Tìm theo mã bằng Hash Table (`dict`): O(1) trung bình, O(n) xấu nhất.
- Merge sort theo số tiền và mã: O(n log n), bộ nhớ phụ O(n).
- Merge sort: chia đôi → sắp từng nửa → trộn hai nửa đã sắp xếp.
- Bộ sắp xếp xử lý cả danh sách rỗng và các khoản bằng tiền.

### Slide 7 — Thuật toán duyệt giao dịch (2,5 phút)

- Queue (cài bằng `deque`): `popleft()` lấy đầu O(1); trong demo phải quét List để dựng Queue nên toàn bộ lần duyệt là O(n).
- Heap dùng khóa `(-số_tiền, mã)` để lấy giao dịch giá trị cao nhất.
- Heap lấy phần tử sau khi dựng là O(log q). Bản demo quét n giao dịch, heapify q giao dịch mỗi lần bấm: tổng O(n + q).
- Ngưỡng duyệt khiến giao dịch chưa nhận quyền lợi trước khi được duyệt.

**Ví dụ giải thích:** 6, 9, 7 triệu → Heap lưu khóa -6, -9, -7; giá trị nhỏ nhất là -9, nên giao dịch 9 triệu được lấy trước.

### Slide 8 — Quy tắc thưởng (1 phút)

- Giao dịch đã duyệt: tính hoàn tiền và cộng điểm theo quy tắc minh họa.
- Giao dịch lớn chỉ được tính thưởng sau duyệt.
- Chặn đổi điểm quá số dư; chặn hoàn giao dịch nếu điểm đã dùng.

### Slide 9 — Kiểm thử (30 giây)

- Hội viên/mã giao dịch giả lập, không có dữ liệu khách hàng thật.
- 13 kiểm thử ứng dụng web và 14 kiểm tra trong notebook.
- Bao phủ ngưỡng giao dịch, queue trống, sai dữ liệu, hoàn lặp, đổi điểm thiếu và lưu sau khởi động lại.
- Benchmark tái lập bằng `python benchmarks.py`; điền số đo thực tế từ máy trình bày.

### Slide 10 — Demo trực tiếp (5 phút)

1. Mở notebook trong Colab/Jupyter và chọn **Run All**.
2. Chỉ ra dashboard và dữ liệu giả lập.
3. Tìm `GD0001`, sắp xếp và xem FIFO/heap ưu tiên.
4. Ghi giao dịch 850.000 ₫ và khoản 9.000.000 ₫; quan sát ngưỡng duyệt.
5. Đổi điểm; thử hoàn giao dịch và quan sát kiểm tra nghiệp vụ.
6. Dùng undo, xem kết quả 14 kiểm tra và benchmark.
7. Nếu còn thời gian, trình diễn web demo ở `http://127.0.0.1:8000`.

### Slide 11 — Kết quả và giới hạn (1 phút)

- Demo tích hợp UI, API, dữ liệu lưu bền, 5 cấu trúc/thuật toán.
- 13/13 unit test web và 14/14 kiểm tra notebook đạt.
- Giới hạn: lưu file JSON, một tiến trình, không đăng nhập, chưa có audit trail.
- Không sử dụng cho quy trình thanh toán thật.

### Slide 12 — Kết luận và hướng phát triển (1 phút)

- Cấu trúc dữ liệu cần được chọn theo thao tác nghiệp vụ và độ phức tạp.
- Tách ledger và quy tắc tính điểm giúp tránh cập nhật số dư rời rạc.
- Hướng tiếp theo: database ACID, audit log, phân quyền, idempotency, kiểm thử tải.
- Mời giảng viên đặt câu hỏi.

## Câu hỏi dự kiến

**Vì sao dùng Hash Table (`dict`) thay vì tìm tuyến tính?** Tìm theo mã là thao tác chính, Hash Table trung bình O(1), dù xấu nhất O(n).

**Tại sao heap lưu số tiền âm?** `heapq` là min-heap; số âm đảo thứ tự để khoản tiền lớn nhất có khóa nhỏ nhất.

**Hoàn giao dịch ảnh hưởng điểm ra sao?** Ledger đánh dấu giao dịch hoàn; điểm/hoàn tiền từ giao dịch không còn khả dụng. Nếu điểm đã tiêu, yêu cầu hoàn bị từ chối.

**Có thể triển khai thật không?** Không; cần database ACID, audit trail, quyền truy cập, chính sách sản phẩm đã duyệt và đánh giá bảo mật.

**Tại sao không dùng cơ sở dữ liệu?** Mục tiêu demo tập trung so sánh cấu trúc dữ liệu; JSON giúp chạy dễ không cần setup. Đây là đánh đổi chỉ phù hợp một tiến trình.
