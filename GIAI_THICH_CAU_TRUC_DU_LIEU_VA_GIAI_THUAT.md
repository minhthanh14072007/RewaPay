# Cấu trúc dữ liệu và giải thuật trong RewaPay

Tài liệu này trích một số đoạn code tiêu biểu trong dự án và giải thích bằng ngôn ngữ đơn giản. Mã nguồn đầy đủ nằm trong [`rewards.py`](./rewards.py); dữ liệu minh họa nằm trong [`data/sample_data.json`](./data/sample_data.json).

> RewaPay là ứng dụng mô phỏng phục vụ học tập. Các giao dịch và quy tắc thưởng trong ví dụ không phải dữ liệu hoặc chính sách tài chính thật.

## 1. Dữ liệu được tổ chức như thế nào?

Trong tệp JSON, dữ liệu được chia thành ba danh sách: hội viên, giao dịch và lần đổi điểm. Mỗi phần tử là một `dict` (từ điển) chứa các trường có tên.

```json
{
  "members": [
    {"id": "TV001", "name": "Nguyễn An", "tier": "Bạc"}
  ],
  "transactions": [
    {
      "id": "GD0001",
      "member_id": "TV001",
      "amount_vnd": 1250000,
      "category": "Siêu thị",
      "cashback_vnd": 12500,
      "points": 125,
      "status": "approved",
      "refunded": false
    }
  ],
  "redemptions": [
    {"id": "HT0001", "member_id": "TV001", "points": 100, "value_vnd": 10000}
  ]
}
```

**Hiểu đơn giản:** ba danh sách giống ba bảng nhỏ. Một giao dịch có mã riêng, mã hội viên, số tiền, điểm, tiền hoàn và trạng thái. `member_id` cho biết giao dịch thuộc về hội viên nào.

**Vì sao dùng danh sách và từ điển?** Danh sách tiện để lưu nhiều bản ghi theo thứ tự; từ điển giúp đọc trường rõ ràng, ví dụ `transaction["amount_vnd"]` thay vì phải nhớ vị trí cột.

## 2. Bảng băm (Hash Table) để tra cứu theo mã

Python `dict` là một dạng bảng băm. Ứng dụng tạo các chỉ mục theo mã hội viên và mã giao dịch:

```python
def _reindex(self) -> None:
    self.member_by_id = {item["id"]: item for item in self.data["members"]}
    self.transaction_by_id = {
        item["id"]: item for item in self.data["transactions"]
    }
```

Khi cần tìm một giao dịch:

```python
def find_transaction(self, transaction_id: str) -> dict[str, Any] | None:
    return deepcopy(self.transaction_by_id.get(transaction_id.strip().upper()))
```

**Hiểu đơn giản:** thay vì dò từng giao dịch từ đầu danh sách, chương trình hỏi trực tiếp chỉ mục “mã này ứng với bản ghi nào?”. Vì vậy tìm theo mã thường nhanh, trung bình **O(1)**. Trường hợp xấu nhất của bảng băm có thể là **O(n)**.

`deepcopy` trả về một bản sao để nơi gọi không vô tình sửa bản ghi gốc trong sổ.

## 3. Hàng đợi (Queue) xử lý theo lượt đến trước

Danh sách giao dịch chờ được chuyển thành `deque`, một hàng đợi hai đầu:

```python
def _pending_queue(self) -> deque[str]:
    return deque(
        item["id"]
        for item in self.data["transactions"]
        if item["status"] == "pending"
    )
```

Nếu chọn xử lý theo FIFO (*First In, First Out* — vào trước, ra trước):

```python
if strategy == "fifo":
    transaction_id = queue.popleft()
```

**Hiểu đơn giản:** giống xếp hàng ở quầy. Giao dịch chờ đầu tiên sẽ được lấy ra duyệt trước. Lấy một phần tử ở đầu `deque` tốn **O(1)**; việc tạo hàng đợi ở đây vẫn phải quét danh sách giao dịch, tốn **O(n)**.

## 4. Heap để ưu tiên giao dịch giá trị cao

Để chọn giao dịch chờ có số tiền lớn nhất, chương trình dùng `heapq`. Python cung cấp min-heap, nên số tiền được đổi dấu âm để khoản lớn hơn đứng đầu:

```python
heap = [
    (-item["amount_vnd"], item["created_at"], item["id"])
    for item in self.data["transactions"]
    if item["status"] == "pending"
]
heapq.heapify(heap)
```

Lấy giao dịch ưu tiên cao nhất:

```python
_, _, transaction_id = heapq.heappop(heap)
ordered.append(deepcopy(self.transaction_by_id[transaction_id]))
```

**Hiểu đơn giản:** heap giống danh sách ưu tiên; giao dịch có số tiền cao nhất được đưa lên đầu để xử lý trước. Nếu bằng tiền, thời gian tạo và mã giao dịch giúp xác định thứ tự ổn định.

Trong đoạn triển khai hiện tại, heap được dựng lại từ các giao dịch đang chờ mỗi lần cần xử lý. Dựng heap từ `n` giao dịch tốn **O(n)**, lấy phần tử đầu tốn **O(log n)**. Nếu lấy và sắp toàn bộ `n` phần tử như `pending_priority`, tổng thời gian là **O(n log n)**.

## 5. Ngăn xếp (Stack) để hoàn tác

Lịch sử hoàn tác dùng `list` như một ngăn xếp:

```python
self._undo_stack: list[dict[str, Any]] = []
```

Khi lưu thay đổi, trạng thái trước đó được đưa lên đỉnh ngăn xếp:

```python
def _commit(self, candidate: dict[str, Any]) -> None:
    self._write(candidate)
    self._undo_stack.append(self.data)
    self.data = candidate
    self._reindex()
```

Hoàn tác lấy trạng thái gần nhất ra:

```python
def undo(self) -> bool:
    if not self._undo_stack:
        return False
    previous = self._undo_stack[-1]
    self._write(previous)
    self._undo_stack.pop()
    self.data = previous
    self._reindex()
    return True
```

**Hiểu đơn giản:** giống chồng đĩa — thao tác mới nhất được lấy ra trước (*Last In, First Out*). `append` và `pop` ở cuối danh sách thường tốn **O(1)**. Tuy nhiên, mỗi trạng thái lưu là một bản dữ liệu, nên sao chép/lưu trạng thái có chi phí tăng theo kích thước dữ liệu.

## 6. Merge sort để sắp xếp giao dịch

Merge sort chia danh sách thành hai nửa, sắp xếp từng nửa, rồi ghép hai nửa đã sắp xếp:

```python
def sort(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(items) < 2:
        return items
    middle = len(items) // 2
    left = sort(items[:middle])
    right = sort(items[middle:])
    merged: list[dict[str, Any]] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
```

Khóa sắp xếp kết hợp số tiền và mã giao dịch:

```python
def key(item: dict[str, Any]) -> tuple[int, str]:
    amount = int(item["amount_vnd"])
    return (amount if order == "asc" else -amount, str(item["id"]))
```

**Hiểu đơn giản:** chia để trị. Ví dụ muốn sắp 8 giao dịch, chương trình chia thành các nhóm nhỏ, sắp các nhóm rồi ghép lại. Cách này cần khoảng **O(n log n)** thời gian và **O(n)** bộ nhớ phụ. Mã giao dịch là tiêu chí phụ để các giao dịch cùng số tiền có thứ tự nhất quán.

## 7. Quy tắc duyệt và tính thưởng

Hằng số nghiệp vụ được khai báo tập trung:

```python
REVIEW_THRESHOLD_VND = 5_000_000
POINTS_PER_VND = 10_000
CASHBACK_BASIS_POINTS = 100
POINT_REDEMPTION_STEP = 100
VND_PER_POINT = 100
```

Khi tạo giao dịch, chương trình tính quyền lợi và trạng thái:

```python
cashback = amount_vnd * CASHBACK_BASIS_POINTS // 10_000
transaction = {
    "id": self._next_id(),
    "member_id": normalized_member,
    "amount_vnd": amount_vnd,
    "cashback_vnd": cashback,
    "points": amount_vnd // POINTS_PER_VND,
    "status": (
        "pending"
        if amount_vnd > REVIEW_THRESHOLD_VND
        else "approved"
    ),
    "refunded": False,
    "created_at": utc_now(),
}
```

**Hiểu đơn giản:** giao dịch **trên 5.000.000 ₫** cần chờ duyệt; giao dịch bằng hoặc thấp hơn ngưỡng được duyệt ngay. Phép chia nguyên `//` làm tròn xuống phần lẻ. Giao dịch chờ chưa được cộng thưởng cho đến khi được duyệt.

## 8. Tóm tắt nhanh

| Cấu trúc/giải thuật | Dùng ở đâu? | Mục đích | Độ phức tạp chính |
| --- | --- | --- | --- |
| `list` + `dict` | Sổ giao dịch dạng JSON | Lưu danh sách bản ghi có trường rõ ràng | Duyệt danh sách: O(n) |
| Bảng băm (`dict`) | `transaction_by_id` | Tìm giao dịch theo mã | Trung bình O(1) |
| Hàng đợi (`deque`) | Duyệt FIFO | Xử lý giao dịch chờ theo thứ tự đến | Lấy đầu O(1) |
| Heap (`heapq`) | Duyệt ưu tiên | Chọn giao dịch có số tiền cao nhất | Lấy phần tử đầu O(log n) |
| Ngăn xếp (`list`) | `_undo_stack` | Hoàn tác thao tác gần nhất | Thêm/lấy ở cuối O(1) |
| Merge sort | Sắp xếp danh sách | Sắp tăng/giảm theo số tiền | O(n log n) |

Độ phức tạp trong bảng là chi phí của thao tác cấu trúc chính; một số bước xung quanh như dựng chỉ mục hoặc quét danh sách vẫn cần đọc nhiều bản ghi.
