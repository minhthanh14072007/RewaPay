# BÁO CÁO PROJECT

## Hệ thống quản lý hoàn tiền và điểm thưởng cho giao dịch

**Học phần:** Cấu trúc dữ liệu tài chính và giải thuật  
**Giảng viên hướng dẫn:** Phạm Thuỷ Tú  
**Nhóm:** …  
**Thành viên:** …  
**Phiên bản sản phẩm:** 1.0 · 13/10/2026  

> Tất cả tài khoản hội viên, mã giao dịch và số liệu trong project đều là dữ liệu tự mô phỏng. Các mức hoàn tiền/điểm chỉ là giả định học thuật, không phải chính sách tài chính thực tế.

## Tóm tắt project

Project xây dựng một ứng dụng Python/Notebook để minh họa quy trình quản lý chương trình hoàn tiền và tích lũy điểm thưởng cho các giao dịch bán lẻ giả lập. Bài toán xuất phát từ nhu cầu theo dõi nhiều giao dịch theo hội viên: giao dịch phải được tìm lại nhanh theo mã, sắp xếp theo giá trị, cộng thưởng nhất quán, xử lý giao dịch có giá trị cao trước khi ghi nhận thưởng và không cho phép đổi/hoàn vượt quá số dư. Người dùng chính trong phạm vi demo là nhân viên vận hành chương trình và quản trị viên; hội viên được mô phỏng qua mã và tên không chứa thông tin nhận dạng thật.

Đầu vào gồm mã hội viên, số tiền nguyên VND và danh mục giao dịch. Dữ liệu được kiểm tra miền giá trị trước khi tiếp nhận. Theo quy tắc minh họa, giao dịch đã duyệt nhận 1% hoàn tiền (làm tròn xuống đến VND nguyên) và một điểm cho mỗi 10.000 VND. Giao dịch trên 5.000.000 VND chuyển sang trạng thái chờ duyệt; chỉ sau khi được duyệt mới cộng thưởng. Hội viên có thể đổi tối thiểu 100 điểm theo bội số 100, với giá trị quy đổi minh họa 100 VND/điểm. Giao dịch đã duyệt có thể được hoàn nếu số điểm phát sinh từ giao dịch đó chưa bị sử dụng.

Chương trình chỉ sử dụng các cấu trúc trong bảng yêu cầu học phần: List lưu sổ giao dịch và làm Stack snapshot; Queue được cài bằng `collections.deque` cho FIFO; Hash Table được cài bằng `dict` để tra cứu mã; Heap được cài bằng `heapq` cho ưu tiên giao dịch giá trị cao. Merge sort là thuật toán sắp xếp trên List, không phải cấu trúc dữ liệu. Kết quả là Notebook Python tự chạy, kèm ứng dụng web tiếng Việt bổ sung, dữ liệu giả lập, 13 kiểm thử web và 14 kiểm tra trong Notebook. Sản phẩm không kết nối ngân hàng, không xử lý tiền thật và không được thiết kế làm hệ thống production.

## Bảng phân công và mức độ đóng góp

| Thành viên | Công việc | Mức đóng góp |
| --- | --- | --- |
| Nguyễn … | Phân tích nghiệp vụ, cấu trúc dữ liệu và kiểm thử | …% |
| Trần … | Cài đặt giao diện, báo cáo và thuyết trình | …% |

Nhóm cần thay tên và phần trăm bằng kết quả đóng góp thực tế trước khi nộp.

## 1. Giới thiệu project

### 1.1 Bối cảnh thực tế

Chương trình khách hàng thân thiết cần ghi nhận giao dịch, phản ánh quyền lợi của từng hội viên và đưa ra quyết định có thể giải thích. Một danh sách đơn thuần có thể biểu diễn giao dịch, nhưng tra cứu tuần tự chậm dần khi dữ liệu tăng; xóa phần tử khỏi hàng đợi bằng thao tác đầu danh sách cũng dịch chuyển các phần tử còn lại. Bài toán phù hợp để so sánh cấu trúc dữ liệu tuyến tính, bảng băm và cấu trúc ưu tiên.

### 1.2 Vấn đề cần giải quyết

1. Làm sao lưu nhiều giao dịch và tra cứu đúng giao dịch bằng mã?
2. Làm sao sắp xếp giao dịch theo số tiền và xử lý giao dịch cần duyệt đúng thứ tự?
3. Làm sao tính, đổi và thu hồi điểm/hoàn tiền mà không tạo số dư âm?
4. Làm sao kiểm thử dữ liệu trống, trùng thao tác, sai miền và giao dịch vượt ngưỡng?

### 1.3 Mục tiêu

- Cung cấp demo thao tác được trên trình duyệt, chạy hoàn toàn cục bộ.
- Dùng ít nhất ba cấu trúc dữ liệu phù hợp và giải thích lựa chọn.
- Có thuật toán sắp xếp và tra cứu/ưu tiên, nêu độ phức tạp.
- Bảo toàn trạng thái hợp lệ khi đổi điểm, duyệt hoặc hoàn giao dịch.
- Dùng dữ liệu giả lập và kiểm thử các trường hợp bình thường, biên, lỗi.

### 1.4 Phạm vi

Trong phạm vi: hội viên giả lập; giao dịch VND; chính sách một tỷ lệ hoàn và một tỷ lệ tích điểm cố định; duyệt giao dịch theo ngưỡng; đổi điểm; hoàn giao dịch; tìm kiếm theo mã; sắp xếp; hoàn tác trong phiên; dashboard và lưu JSON cục bộ.

Ngoài phạm vi: xử lý thanh toán, ngân hàng/cổng thanh toán thật, đăng nhập và phân quyền, phân hạng tự động, chiến dịch thưởng thay đổi theo thời gian, đa tiền tệ, giao dịch đồng thời, cơ sở dữ liệu production và phát hiện gian lận bằng học máy.

### 1.5 Sản phẩm

`HeThong_HoanTien_DiemThuong.ipynb` là sản phẩm Notebook độc lập, chạy trực tiếp trên Google Colab hoặc Jupyter theo yêu cầu công nghệ của học phần. `app.py` + `rewards.py` và `static/` là demo web bổ sung; `data/sample_data.json` là dữ liệu mẫu; `tests/` là kiểm thử ứng dụng; `benchmarks.py` và cell benchmark trong notebook là thí nghiệm lặp lại; `README.md` là hướng dẫn chạy; `PRESENTATION.md` là nội dung thuyết trình.

## 2. Phân tích bài toán nghiệp vụ

### 2.1 Đối tượng sử dụng

| Đối tượng | Nhu cầu trong bản demo |
| --- | --- |
| Nhân viên vận hành | Ghi giao dịch, xem trạng thái, xử lý hàng chờ |
| Quản trị viên | Theo dõi tổng số liệu, hội viên và chính sách giả lập |
| Hội viên (mô phỏng) | Xem số dư điểm và yêu cầu quy đổi |

### 2.2 Quy trình nghiệp vụ

1. Nhân viên chọn hội viên, nhập số tiền và danh mục.
2. Hệ thống xác thực hội viên, số tiền 1.000–1.000.000.000 VND và danh mục.
3. Mã giao dịch được cấp tuần tự. Dưới hoặc bằng ngưỡng, giao dịch được duyệt; trên ngưỡng, giao dịch ở trạng thái chờ.
4. Giao dịch chờ được xử lý theo FIFO hoặc theo ưu tiên giá trị cao nhất.
5. Với giao dịch được duyệt, hệ thống tính hoàn tiền và điểm; dashboard tổng hợp lại từ ledger.
6. Yêu cầu đổi điểm được kiểm tra số dư, mức tối thiểu và bội số. Yêu cầu không hợp lệ bị từ chối, dữ liệu không đổi.
7. Hoàn giao dịch đã duyệt sẽ thu hồi quyền lợi chưa dùng. Nếu điểm đã đổi, hệ thống từ chối hoàn để không tạo số dư âm.
8. Thao tác gần nhất có thể được khôi phục trong phiên hiện tại.

### 2.3 Yêu cầu chức năng

| Mã | Chức năng | Kết quả mong đợi |
| --- | --- | --- |
| F01 | Xem tổng quan và danh sách hội viên/giao dịch | Hiển thị số liệu tính từ dữ liệu hiện tại |
| F02 | Ghi giao dịch | Tạo mã mới; áp dụng ngưỡng duyệt |
| F03 | Tra cứu theo mã | Trả đúng một bản ghi hoặc thông báo không tìm thấy |
| F04 | Sắp xếp số tiền | Kết quả tăng/giảm đúng, hòa được phân định ổn định bằng mã |
| F05 | Duyệt FIFO | Duyệt giao dịch chờ được tiếp nhận sớm nhất |
| F06 | Duyệt ưu tiên | Duyệt giao dịch chờ có số tiền cao nhất |
| F07 | Đổi điểm | Không vượt số dư; trừ đúng điểm và lưu giá trị quy đổi |
| F08 | Hoàn giao dịch | Thu hồi điểm và tiền hoàn; chặn hoàn lặp/điểm đã tiêu |
| F09 | Hoàn tác | Khôi phục snapshot của thao tác gần nhất trong phiên |
| F10 | Lưu bền | Tải lại trạng thái từ JSON sau khi khởi động lại |

### 2.4 Yêu cầu phi chức năng

Giao diện tiếng Việt, thích ứng màn hình nhỏ, không phụ thuộc dịch vụ ngoài; dữ liệu mẫu không chứa thông tin thật; lỗi nghiệp vụ được hiển thị rõ; cập nhật tệp JSON theo cách ghi tệp tạm rồi thay thế; dữ liệu được xác thực phía máy chủ. Demo chỉ bind vào `127.0.0.1`. Không có cơ chế xác thực hay kiểm soát truy cập production.

## 3. Dữ liệu mô phỏng

### 3.1 Mô tả dữ liệu

| Trường | Kiểu | Ý nghĩa | Ví dụ |
| --- | --- | --- | --- |
| `member.id` | str | Mã hội viên giả lập | `TV001` |
| `member.name` | str | Tên mẫu, không nhận dạng cá nhân thật | Nguyễn An |
| `transaction.id` | str | Mã giao dịch | `GD0001` |
| `member_id` | str | Khóa hội viên | `TV001` |
| `amount_vnd` | int | Số tiền VND | `1250000` |
| `category` | str | Nhóm chi tiêu | Siêu thị |
| `cashback_vnd` | int | Quyền lợi hoàn tiền | `12500` |
| `points` | int | Điểm phát sinh nếu duyệt | `125` |
| `status` | enum str | `pending` hoặc `approved` | `approved` |
| `refunded` | bool | Đã hoàn giao dịch hay chưa | `false` |
| `created_at` | ISO-8601 | Thời điểm ghi nhận | `2026-10-10T08:30:00+00:00` |

### 3.2 Nguồn dữ liệu

Nhóm tự tạo bộ dữ liệu cố định trong `data/sample_data.json`; dữ liệu không lấy từ khách hàng, ngân hàng hoặc nguồn cá nhân. Khi chạy lần đầu, bản sao làm việc được lưu thành `data/store.json`.

### 3.3 Tiền xử lý và kiểm tra hợp lệ

Mã hội viên/giao dịch được chuẩn hóa chữ hoa khi tra cứu; ID hội viên phải tồn tại; tiền giao dịch phải là số nguyên và nằm trong miền quy định; danh mục không được rỗng, tối đa 40 ký tự. Điểm đổi phải là số nguyên, ít nhất 100, chia hết cho 100 và không vượt số dư. Bản ghi hoàn không được cấp lại phần thưởng. Chỉ giao dịch ở trạng thái đã duyệt mới tham gia tổng tiền hoàn và điểm khả dụng.

### 3.4 Dữ liệu kiểm thử

Kiểm thử tạo trạng thái trống trong thư mục tạm, tránh ghi đè bộ dữ liệu demo; bao gồm giao dịch đúng ngưỡng và cao hơn ngưỡng, hai giao dịch ưu tiên khác giá trị, dữ liệu trống, không tìm thấy mã, số dư thiếu, hoàn lặp, điểm đã sử dụng, sai kiểu/miền và lưu sau khởi động lại.

## 4. Cấu trúc dữ liệu

### 4.1 Các thao tác trọng tâm

Project phân tích bốn thao tác ảnh hưởng trực tiếp đến lựa chọn cấu trúc và hiệu năng: tra cứu giao dịch theo mã, sắp xếp theo số tiền, duyệt FIFO và duyệt giao dịch có số tiền cao nhất. Stack hỗ trợ hoàn tác thao tác gần nhất. Các quy tắc cộng/đổi/hoàn điểm là nghiệp vụ bổ sung, không phải thuật toán trọng tâm.

### 4.2 Lựa chọn

- **List:** lưu danh sách hội viên, giao dịch và lịch sử đổi điểm; dễ duyệt, thêm giao dịch và sắp xếp.
- **Queue:** cài bằng `collections.deque`; lấy giao dịch đến trước bằng `popleft()` trong O(1).
- **Stack:** cài bằng `list`; lưu snapshot trước cập nhật, hỗ trợ hoàn tác bằng thao tác pop.
- **Hash Table:** cài bằng `dict`; `transaction_by_id` và `member_by_id` ánh xạ mã đến bản ghi, tra cứu trung bình O(1).
- **Heap:** cài bằng `heapq`; khóa `(-amount, timestamp, id)` lấy giao dịch số tiền cao nhất trước; timestamp và ID phá hòa ổn định.
- **Insertion Sort và Selection Sort:** hai thuật toán sắp xếp trực tiếp trên List, được cài đặt để so sánh hiệu năng trong Mục 7.3; không phải cấu trúc dữ liệu mới.
- **Merge sort:** thuật toán sắp xếp trên List theo số tiền và ID, O(n log n) ở trường hợp tốt/trung bình/xấu; đây không phải cấu trúc dữ liệu thứ sáu.

Đồ án chỉ chọn năm cấu trúc trong bảng yêu cầu; không cài Trie, AVL hoặc Skip List vì phạm vi demo không cần gợi ý mã theo tiền tố hay cấu trúc tra cứu có thứ tự riêng.

### 4.3 Phương án thay thế

Tra cứu tuyến tính trên List có O(n), nên Hash Table phù hợp hơn khi thường xuyên tìm theo mã. Dùng List để lấy đầu hàng có thể phải dời các phần tử còn lại, còn Queue cài bằng `deque.popleft()` lấy đầu O(1). Heap phù hợp khi cần lấy phần tử ưu tiên, nhưng cần tính cả thời gian heapify. Insertion Sort và Selection Sort được cài để thực nghiệm và so sánh ở Mục 7.3; Merge sort được dùng để sắp xếp trong ứng dụng vì có độ phức tạp O(n log n), phù hợp hơn khi số giao dịch tăng.

### 4.4 Độ phức tạp

Trong bảng, n là số bản ghi; q là số giao dịch đang chờ. Hash Table có độ phức tạp trung bình O(1), nhưng xấu nhất O(n). Ở bản demo, Heap được dựng lại từ danh sách giao dịch chờ mỗi lần bấm duyệt; do đó phải tính cả chi phí heapify.

| Thao tác | Cấu trúc/thuật toán | Tốt nhất | Trung bình | Xấu nhất | Bộ nhớ phụ |
| --- | --- | ---: | ---: | ---: | ---: |
| Duyệt danh sách | List | O(n) | O(n) | O(n) | O(1) |
| Tra cứu mã | Hash Table (`dict`) | O(1) | O(1) | O(n) | O(n) chỉ mục |
| Insertion Sort | List | O(n) | O(n²) | O(n²) | O(n) cho bản sao kết quả |
| Selection Sort | List | O(n²) | O(n²) | O(n²) | O(n) cho bản sao kết quả |
| Sắp xếp giao dịch | Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Dựng Queue từ danh sách giao dịch | Queue (`deque`) | O(n) | O(n) | O(n) | O(q) |
| Lấy giao dịch đầu sau khi dựng Queue | Queue (`deque`) | O(1) | O(1) | O(1) | O(1) |
| Dựng Heap và quét danh sách chờ | Heapify | O(n + q) | O(n + q) | O(n + q) | O(q) |
| Lấy phần tử sau khi dựng Heap | Heap | O(log q) | O(log q) | O(log q) | O(1) |
| Một lần bấm duyệt FIFO hiện tại | Dựng Queue + lấy đầu | O(n) | O(n) | O(n) | O(q) |
| Một lần bấm duyệt ưu tiên hiện tại | Quét + Heapify + lấy phần tử | O(n + q) | O(n + q) | O(n + q) | O(q) |
| Lưu lịch sử hoàn tác | Stack (`list`) | O(1) push/pop | O(1) push/pop | O(1) push/pop | O(n) mỗi snapshot |

Nếu Heap được giữ sẵn và cập nhật giữa các lần duyệt, thao tác lấy phần tử ưu tiên là O(log q). Bản demo quét danh sách giao dịch và dựng lại Heap mỗi lần để đơn giản hóa đồng bộ dữ liệu và hoàn tác; do đó tổng chi phí mỗi lần duyệt hiện tại là O(n + q), thường viết gọn O(n) vì q ≤ n.

## 5. Phân tích và thiết kế giải thuật

### 5.1 Quy trình xử lý

```text
[Nhập giao dịch] → [Kiểm tra đầu vào] ─sai→ [Trả lỗi, không đổi trạng thái]
                          │ đúng
                          ▼
                 [Cấp mã & tính thưởng]
                    ├─ tiền > 5 triệu → [Chờ duyệt]
                    └─ tiền ≤ 5 triệu → [Đã duyệt, cộng thưởng]
                          │
              [FIFO hoặc ưu tiên số tiền lớn]
                          ▼
                   [Lưu trạng thái]
```

### 5.2 Mã giả thuật toán chính

```text
TRA_CỨU(mã):
  chuẩn hóa mã thành chữ hoa
  nếu HashTable có khóa mã: trả về bản ghi
  nếu không: trả về "không tìm thấy"

MERGE_SORT(danh_sách):
  nếu danh sách có ít hơn 2 phần tử: trả về danh sách
  chia danh sách thành nửa_trái và nửa_phải
  sắp xếp đệ quy mỗi nửa
  trộn hai nửa theo (số_tiền, mã_giao_dịch)
  trả về danh sách đã sắp xếp

DUYỆT_FIFO:
  nếu Queue rỗng: trả về "không có giao dịch chờ"
  mã ← lấy phần tử đầu Queue
  chuyển giao dịch mã sang "đã duyệt"

DUYỆT_ƯU_TIÊN:
  tạo danh sách khóa (-số_tiền, mã) cho các giao dịch đang chờ
  Heapify danh sách khóa
  lấy phần tử đầu Heap          # số tiền lớn nhất
  chuyển giao dịch được chọn sang "đã duyệt"
  # Bản demo dựng Heap lại mỗi lần gọi
```

### 5.3 Ví dụ truy vết Heap

Có ba giao dịch chờ: GD01 = 6 triệu, GD02 = 9 triệu, GD03 = 7 triệu đồng. Heap lưu khóa `(-số_tiền, mã)`:

| Giao dịch | Khóa đưa vào Heap |
| --- | ---: |
| GD01 | -6.000.000 |
| GD02 | -9.000.000 |
| GD03 | -7.000.000 |

`heapq` lấy khóa nhỏ nhất. Trong ba số âm này, `-9.000.000` nhỏ nhất, nên GD02 được chọn trước. Dấu âm chỉ dùng để đảo thứ tự ưu tiên, không làm thay đổi số tiền giao dịch.

### 5.4 Lý do chọn thuật toán

Hash Table được dùng vì tra cứu theo mã là thao tác thường xuyên; trung bình O(1) thay vì O(n) khi dò từng phần tử của List. Queue phù hợp chính sách “đến trước xử lý trước” và thao tác lấy đầu O(1); do demo tạo lại Queue từ danh sách giao dịch, tổng một lần duyệt FIFO là O(n). Heap phù hợp để lấy khoản tiền cao nhất mà không cần sắp xếp toàn bộ hàng chờ, nhưng bản demo quét giao dịch và heapify lại mỗi lần bấm nên tổng mỗi yêu cầu là O(n + q). Merge sort minh họa chia để trị, có độ phức tạp O(n log n) ở cả trường hợp tốt, trung bình và xấu.

## 6. Cài đặt chương trình

### 6.1 Công nghệ

Python 3 trên Google Colab/Jupyter Notebook. Dùng thư viện chuẩn `collections.deque` cho Queue và `heapq` cho Heap; các cấu trúc List, Stack và Hash Table dùng `list`, `list` và `dict` của Python. Merge sort được tự cài đặt. Notebook không cần thư viện trực quan hóa hay package bên ngoài.

### 6.2 Tổ chức mã nguồn

Notebook `HeThong_HoanTien_DiemThuong.ipynb` tổ chức theo trình tự: quy tắc, cài đặt cấu trúc và merge sort, minh họa kết quả, thao tác nghiệp vụ, kiểm thử và benchmark. Bản web bổ sung tách quy tắc vào `rewards.py`.

### 6.3 Phần cài đặt liên quan đến thuật toán

Mã giả và phân tích độ phức tạp ở Mục 5 mô tả luồng chính. Khi cài đặt, Hash Table được dựng lại sau cập nhật để tra cứu theo mã; Stack lưu snapshot trước thao tác; số dư được tính từ các giao dịch đã duyệt, chưa hoàn và lịch sử đổi điểm. Các chi tiết giao diện web không ảnh hưởng đến phân tích thuật toán nên không trình bày dài tại đây.

### 6.4 Giao diện hoặc kết quả demo

**Notebook (phù hợp Colab/Jupyter):** mở `HeThong_HoanTien_DiemThuong.ipynb`, chọn Run All; dashboard và bảng kết quả xuất hiện ngay dưới từng cell, không cần khởi động server. Có thể trình diễn tra cứu `GD0001`, sắp xếp, xem hàng chờ FIFO/heap, ghi nhận, đổi điểm, hoàn tác và kết quả kiểm thử.

**Demo web bổ sung:** chạy `python app.py`, mở `http://127.0.0.1:8000`. Dashboard hiển thị số liệu giả lập; nút “Ghi nhận giao dịch” mở biểu mẫu; hàng chờ có hai chiến lược; bộ tìm kiếm nhận mã `GD0001`; khu vực hội viên thể hiện điểm khả dụng; biểu mẫu đổi điểm cho xem giá trị quy đổi trước khi xác nhận. Nút “Hoàn” sẽ hỏi xác nhận và thu hồi thưởng nếu nghiệp vụ cho phép.

## 7. Kiểm thử và kết quả

### 7.1 Kế hoạch kiểm thử

Chạy `python -m unittest discover -s tests -v` từ thư mục project. Trạng thái mỗi ca được khởi tạo tạm, nên test không tác động đến dữ liệu demo. `benchmarks.py` chạy phép đo riêng, không cần phụ thuộc ngoài.

### 7.2 Kết quả chức năng

Tại lần xác minh hiện tại, **13/13 unit test của ứng dụng web đạt**. Notebook có cell tự kiểm tra riêng với 14 trường hợp nghiệp vụ và dữ liệu biên. Các kiểm tra của ứng dụng gồm:

| Ca | Trường hợp | Kết quả thực tế |
| --- | --- | --- |
| TC01 | Số tiền hợp lệ, tính 1% và điểm nguyên | Đạt |
| TC02 | Giao dịch vượt ngưỡng không cộng thưởng trước khi duyệt | Đạt |
| TC03 | Duyệt ưu tiên chọn khoản lớn nhất; FIFO giữ thứ tự | Đạt |
| TC04 | Sắp tăng/giảm, danh sách rỗng và phá hòa theo mã | Đạt |
| TC05 | Tra cứu đúng mã, phân biệt không tìm thấy | Đạt |
| TC06 | Đổi điểm đủ điều kiện và cập nhật số dư | Đạt |
| TC07 | Từ chối điểm thiếu, dưới tối thiểu, sai kiểu | Đạt |
| TC08 | Hoàn giao dịch và ngăn hoàn lần hai | Đạt |
| TC09 | Chặn hoàn khi điểm đã sử dụng | Đạt |
| TC10 | Undo phục hồi state và ghi bền | Đạt |
| TC11 | Dữ liệu vẫn đọc được sau khi tạo instance mới | Đạt |
| TC12 | Từ chối số tiền, hội viên và danh mục không hợp lệ | Đạt |
| TC13 | Hàng chờ rỗng không phát sinh lỗi | Đạt |

### 7.3 Thực nghiệm hiệu năng

Chạy `python benchmarks.py` để so sánh Insertion Sort, Selection Sort, Merge sort và `sorted` của Python trên cùng danh sách giao dịch (sắp xếp theo số tiền tăng dần, mã giao dịch dùng để phá hòa). Script đồng thời so sánh tra cứu tuần tự trên List với tra cứu bằng Hash Table (`dict`). Dữ liệu giả lập dùng seed `20261013`; số lần lặp là 15 lần với 100 bản ghi, 7 lần với 1.000 bản ghi và 1 lần với 10.000 bản ghi để giới hạn thời gian cho hai thuật toán bậc O(n²). Bảng dưới đây là số đo thực tế từ lần chạy trên máy đánh giá:

| Số bản ghi | Insertion Sort (ms) | Selection Sort (ms) | Merge sort (ms) | `sorted`/Timsort (ms) | Quét tuần tự (µs) | Dict (µs) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 0,1645 | 0,2101 | 0,2046 | 0,0103 | 2,0000 | 0,1067 |
| 1.000 | 17,7851 | 18,0385 | 3,4727 | 0,1573 | 11,4715 | 0,1144 |
| 10.000 | 4.722,0065 | 3.287,7295 | 171,3295 | 6,8328 | 374,2999 | 1,2999 |

Insertion Sort có thể chạy nhanh khi dữ liệu đã gần đúng thứ tự, nhưng trung bình và xấu nhất phải dịch nhiều phần tử nên tốn O(n²). Selection Sort luôn tìm phần tử nhỏ nhất trong phần chưa sắp xếp, dẫn đến O(n²) phép so sánh. Số đo tại 10.000 bản ghi cho thấy cả hai chậm hơn rõ rệt so với Merge sort và Timsort; vì vậy chúng được đưa vào để minh họa/đối chiếu thuật toán ở mục thực nghiệm, còn chức năng sắp xếp của ứng dụng vẫn dùng Merge sort. Kết quả thời gian phụ thuộc máy và phiên bản Python; không đại diện tải production.

### 7.4 Đối chiếu mục tiêu

Đã có UI web, API cục bộ, 5 cấu trúc/thuật toán minh họa, tìm và sắp xếp, hai chính sách hàng chờ, dữ liệu mẫu, lưu bền, undo trong phiên và kiểm thử biên. Chưa có triển khai đa người dùng, dữ liệu lớn bền vững hay đo trên hạ tầng ngân hàng; phù hợp phạm vi project học thuật đã công bố.

## 8. Thảo luận

### 8.1 Điểm mạnh

Quy tắc hiển thị rõ trên giao diện; thiết kế ledger tránh cập nhật số dư ở nhiều nơi; ưu tiên/FIFO có thể so sánh trực tiếp; dữ liệu được xác thực ở máy chủ; demo không cần cài framework hoặc dùng mạng ngoài.

### 8.2 Hạn chế

Chính sách thưởng cố định; file JSON không hỗ trợ ghi đồng thời an toàn; mọi phép tổng hợp duyệt ledger O(n); undo chỉ tồn tại trong bộ nhớ của tiến trình và snapshot có chi phí O(n); không đăng nhập/phân quyền, audit trail bất biến hay chống sửa tệp dữ liệu; bộ benchmark nhỏ và phụ thuộc môi trường. Vì vậy không dùng cho giao dịch hoặc quyết định tài chính thật.

### 8.3 Bài học

Heap là min-heap nên cần lưu khóa âm để ưu tiên số tiền lớn; kiểm thử cho phát hiện trường hợp chỉ heapify ở màn hình hiển thị nhưng thiếu heapify khi lấy phần tử duyệt. Đơn vị VND nguyên và điểm nguyên tránh sai số số thực. Nên tính số dư từ ledger để giảm nguy cơ bộ đếm và lịch sử giao dịch không khớp.

### 8.4 Hướng phát triển

Thay JSON bằng cơ sở dữ liệu ACID; thêm nhật ký bút toán chỉ ghi thêm; xác thực và phân quyền; chính sách hoàn/điểm có version và thời hạn; idempotency cho API; kiểm thử tải và cạnh tranh; trực quan hóa heap/merge sort từng bước; bổ sung dashboard và xuất báo cáo.

## 9. Kết luận

Project áp dụng đúng năm cấu trúc trong bảng học phần: List lưu sổ giao dịch, Queue (cài bằng `deque`) xử lý FIFO, Stack (cài bằng `list`) hỗ trợ undo, Hash Table (cài bằng `dict`) tra cứu trung bình O(1), và Heap (`heapq`) ưu tiên giao dịch giá trị cao. Merge sort là thuật toán sắp xếp List với độ phức tạp O(n log n), không phải cấu trúc dữ liệu bổ sung. Quy tắc đổi/hoàn điểm kiểm tra số dư trước khi ghi dữ liệu, còn giao dịch giá trị cao chỉ nhận thưởng sau duyệt. Bộ kiểm thử xác nhận 13 trường hợp nghiệp vụ và biên; Notebook có thêm 14 kiểm tra. Sản phẩm có giá trị học tập về lựa chọn cấu trúc dữ liệu theo thao tác nghiệp vụ, không được xem là hệ thống tài chính dùng thật. Hướng phát triển quan trọng nhất là thay lưu trữ JSON bằng ledger ACID có audit trail và kiểm soát truy cập.

## Tài liệu tham khảo

1. Python Software Foundation. (2026). *Python 3 Documentation: `collections.deque`*. https://docs.python.org/3/library/collections.html#collections.deque
2. Python Software Foundation. (2026). *Python 3 Documentation: `heapq` — Heap queue algorithm*. https://docs.python.org/3/library/heapq.html
3. Python Software Foundation. (2026). *Python 3 Documentation: `json`*. https://docs.python.org/3/library/json.html
4. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.

Các bản ghi dữ liệu và giao diện demo là sản phẩm tự xây dựng; không dùng dữ liệu khách hàng hoặc hình ảnh bên ngoài.

## Phụ lục: hướng dẫn chạy

1. Cài Python 3.10+.
2. Mở terminal ở thư mục `rewards_app`.
3. Chạy `python app.py` và mở `http://127.0.0.1:8000`.
4. Chạy kiểm thử bằng `python -m unittest discover -s tests -v`.
5. Chạy benchmark bằng `python benchmarks.py`.
6. Thay tên thành viên, tỷ lệ đóng góp và điền kết quả đo hiệu năng thực tế trước khi nộp.
