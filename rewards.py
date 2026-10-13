"""Core rules and data structures for the simulated rewards application."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from datetime import datetime, timezone
import heapq
import json
from pathlib import Path
from typing import Any


REVIEW_THRESHOLD_VND = 5_000_000
POINTS_PER_VND = 10_000
CASHBACK_BASIS_POINTS = 100
POINT_REDEMPTION_STEP = 100
VND_PER_POINT = 100


class RewardsError(ValueError):
    """An expected business-rule or input validation error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def merge_sort_transactions(
    transactions: list[dict[str, Any]], order: str = "desc"
) -> list[dict[str, Any]]:
    """Sort transactions by amount, then ID, with O(n log n) time."""
    if order not in ("asc", "desc"):
        raise RewardsError("Thứ tự sắp xếp không hợp lệ.")

    def key(item: dict[str, Any]) -> tuple[int, str]:
        amount = int(item["amount_vnd"])
        return (amount if order == "asc" else -amount, str(item["id"]))

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

    return sort(list(transactions))


def insertion_sort_transactions(
    transactions: list[dict[str, Any]], order: str = "desc"
) -> list[dict[str, Any]]:
    """Sort transactions by amount, then ID, using insertion sort."""
    if order not in ("asc", "desc"):
        raise RewardsError("Thứ tự sắp xếp không hợp lệ.")
    sign = 1 if order == "asc" else -1
    result = list(transactions)
    keys = [
        (sign * int(item["amount_vnd"]), str(item["id"]))
        for item in result
    ]
    for index in range(1, len(result)):
        current = result[index]
        current_key = keys[index]
        position = index - 1
        while position >= 0 and keys[position] > current_key:
            keys[position + 1] = keys[position]
            result[position + 1] = result[position]
            position -= 1
        keys[position + 1] = current_key
        result[position + 1] = current
    return result


def selection_sort_transactions(
    transactions: list[dict[str, Any]], order: str = "desc"
) -> list[dict[str, Any]]:
    """Sort transactions by amount, then ID, using selection sort."""
    if order not in ("asc", "desc"):
        raise RewardsError("Thứ tự sắp xếp không hợp lệ.")
    sign = 1 if order == "asc" else -1
    result = list(transactions)
    keys = [
        (sign * int(item["amount_vnd"]), str(item["id"]))
        for item in result
    ]
    for start in range(len(result) - 1):
        best = start
        for index in range(start + 1, len(result)):
            if keys[index] < keys[best]:
                best = index
        result[start], result[best] = result[best], result[start]
        keys[start], keys[best] = keys[best], keys[start]
    return result


class RewardsBook:
    """In-memory indexed rewards ledger with atomic JSON persistence."""

    def __init__(self, state_path: Path, initial_state: dict[str, Any]) -> None:
        self.state_path = state_path
        self.data = self._load(initial_state)
        self._undo_stack: list[dict[str, Any]] = []
        self.member_by_id: dict[str, dict[str, Any]] = {}
        self.transaction_by_id: dict[str, dict[str, Any]] = {}
        self._reindex()

    def _load(self, initial_state: dict[str, Any]) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                with self.state_path.open("r", encoding="utf-8") as stream:
                    state = json.load(stream)
            except (OSError, json.JSONDecodeError) as error:
                raise RuntimeError(
                    f"Không thể đọc dữ liệu tại {self.state_path}: {error}"
                ) from error
        else:
            state = deepcopy(initial_state)
            self._write(state)
        if not isinstance(state, dict) or not all(
            isinstance(state.get(key), list)
            for key in ("members", "transactions", "redemptions")
        ):
            raise RuntimeError("Tệp dữ liệu không đúng định dạng.")
        return state

    def _write(self, state: dict[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        try:
            with temporary.open("w", encoding="utf-8", newline="\n") as stream:
                json.dump(state, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
            temporary.replace(self.state_path)
        except OSError as error:
            raise RuntimeError(
                f"Không thể lưu dữ liệu tại {self.state_path}: {error}"
            ) from error

    def _reindex(self) -> None:
        self.member_by_id = {item["id"]: item for item in self.data["members"]}
        self.transaction_by_id = {
            item["id"]: item for item in self.data["transactions"]
        }

    def _commit(self, candidate: dict[str, Any]) -> None:
        self._write(candidate)
        self._undo_stack.append(self.data)
        self.data = candidate
        self._reindex()

    def _member(self, member_id: str) -> dict[str, Any]:
        member = self.member_by_id.get(member_id.strip().upper())
        if member is None:
            raise RewardsError("Không tìm thấy hội viên.")
        return member

    def _next_id(self) -> str:
        numbers = [
            int(item["id"][2:])
            for item in self.data["transactions"]
            if item.get("id", "").startswith("GD")
            and item["id"][2:].isdigit()
        ]
        return f"GD{max(numbers, default=0) + 1:04d}"

    @staticmethod
    def _earned_totals(transactions: list[dict[str, Any]], member_id: str) -> tuple[int, int]:
        eligible = (
            item
            for item in transactions
            if item["member_id"] == member_id
            and item["status"] == "approved"
            and not item.get("refunded", False)
        )
        return (
            sum(item["cashback_vnd"] for item in eligible),
            sum(
                item["points"]
                for item in transactions
                if item["member_id"] == member_id
                and item["status"] == "approved"
                and not item.get("refunded", False)
            ),
        )

    def _point_balance(self, member_id: str, state: dict[str, Any] | None = None) -> int:
        ledger = state or self.data
        earned = sum(
            item["points"]
            for item in ledger["transactions"]
            if item["member_id"] == member_id
            and item["status"] == "approved"
            and not item.get("refunded", False)
        )
        redeemed = sum(
            item["points"]
            for item in ledger["redemptions"]
            if item["member_id"] == member_id
        )
        return earned - redeemed

    def add_transaction(
        self, member_id: str, amount_vnd: int, category: str
    ) -> dict[str, Any]:
        normalized_member = member_id.strip().upper()
        self._member(normalized_member)
        if isinstance(amount_vnd, bool) or not isinstance(amount_vnd, int):
            raise RewardsError("Số tiền phải là số nguyên VND.")
        if amount_vnd < 1_000 or amount_vnd > 1_000_000_000:
            raise RewardsError("Số tiền phải từ 1.000 đến 1.000.000.000 VND.")
        clean_category = category.strip()
        if not clean_category or len(clean_category) > 40:
            raise RewardsError("Danh mục giao dịch không hợp lệ.")

        cashback = amount_vnd * CASHBACK_BASIS_POINTS // 10_000
        candidate = deepcopy(self.data)
        transaction = {
            "id": self._next_id(),
            "member_id": normalized_member,
            "amount_vnd": amount_vnd,
            "category": clean_category,
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
        candidate["transactions"].append(transaction)
        self._commit(candidate)
        return deepcopy(transaction)

    def find_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        return deepcopy(self.transaction_by_id.get(transaction_id.strip().upper()))

    def sort_transactions(self, order: str = "desc") -> list[dict[str, Any]]:
        return merge_sort_transactions(self.data["transactions"], order)

    def _pending_queue(self) -> deque[str]:
        return deque(
            item["id"]
            for item in self.data["transactions"]
            if item["status"] == "pending"
        )

    def pending_priority(self) -> list[dict[str, Any]]:
        heap = [
            (-item["amount_vnd"], item["created_at"], item["id"])
            for item in self.data["transactions"]
            if item["status"] == "pending"
        ]
        heapq.heapify(heap)
        ordered: list[dict[str, Any]] = []
        while heap:
            _, _, transaction_id = heapq.heappop(heap)
            ordered.append(deepcopy(self.transaction_by_id[transaction_id]))
        return ordered

    def process_next_review(self, strategy: str = "priority") -> dict[str, Any] | None:
        if strategy not in ("priority", "fifo"):
            raise RewardsError("Cách xử lý hàng chờ không hợp lệ.")
        queue = self._pending_queue()
        if not queue:
            return None
        if strategy == "fifo":
            transaction_id = queue.popleft()
        else:
            heap = [
                (-item["amount_vnd"], item["created_at"], item["id"])
                for item in self.data["transactions"]
                if item["status"] == "pending"
            ]
            heapq.heapify(heap)
            transaction_id = heapq.heappop(heap)[2]

        candidate = deepcopy(self.data)
        next(item for item in candidate["transactions"] if item["id"] == transaction_id)[
            "status"
        ] = "approved"
        self._commit(candidate)
        return deepcopy(self.transaction_by_id[transaction_id])

    def redeem_points(self, member_id: str, points: int) -> dict[str, Any]:
        member = self._member(member_id)
        if isinstance(points, bool) or not isinstance(points, int):
            raise RewardsError("Điểm đổi phải là số nguyên.")
        if points < POINT_REDEMPTION_STEP or points % POINT_REDEMPTION_STEP:
            raise RewardsError("Số điểm đổi tối thiểu 100 và phải chia hết cho 100.")
        member_id = member["id"]
        if points > self._point_balance(member_id):
            raise RewardsError("Số điểm khả dụng không đủ.")
        candidate = deepcopy(self.data)
        redemption = {
            "id": f"HT{len(candidate['redemptions']) + 1:04d}",
            "member_id": member_id,
            "points": points,
            "value_vnd": points * VND_PER_POINT,
            "created_at": utc_now(),
        }
        candidate["redemptions"].append(redemption)
        self._commit(candidate)
        return deepcopy(redemption)

    def refund_transaction(self, transaction_id: str) -> dict[str, Any]:
        normalized_id = transaction_id.strip().upper()
        existing = self.transaction_by_id.get(normalized_id)
        if existing is None:
            raise RewardsError("Không tìm thấy giao dịch.")
        if existing["status"] != "approved" or existing.get("refunded", False):
            raise RewardsError("Chỉ có thể hoàn giao dịch đã duyệt và chưa hoàn.")
        if (
            self._point_balance(existing["member_id"])
            - existing["points"]
            < 0
        ):
            raise RewardsError(
                "Không thể hoàn: hội viên đã sử dụng số điểm từ giao dịch này."
            )
        candidate = deepcopy(self.data)
        next(item for item in candidate["transactions"] if item["id"] == normalized_id)[
            "refunded"
        ] = True
        self._commit(candidate)
        return deepcopy(self.transaction_by_id[normalized_id])

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        previous = self._undo_stack[-1]
        self._write(previous)
        self._undo_stack.pop()
        self.data = previous
        self._reindex()
        return True

    def snapshot(self) -> dict[str, Any]:
        members = []
        for member in self.data["members"]:
            cashback, points_earned = self._earned_totals(
                self.data["transactions"], member["id"]
            )
            members.append(
                {
                    **member,
                    "points_earned": points_earned,
                    "points_balance": self._point_balance(member["id"]),
                    "cashback_vnd": cashback,
                }
            )
        approved = [
            item for item in self.data["transactions"] if item["status"] == "approved"
        ]
        pending = [
            item for item in self.data["transactions"] if item["status"] == "pending"
        ]
        return {
            "members": members,
            "transactions": self.sort_transactions("desc"),
            "pending_fifo": [self.transaction_by_id[key] for key in self._pending_queue()],
            "pending_priority": self.pending_priority(),
            "redemptions": list(reversed(self.data["redemptions"])),
            "summary": {
                "member_count": len(members),
                "transaction_count": len(self.data["transactions"]),
                "pending_count": len(pending),
                "cashback_vnd": sum(
                    item["cashback_vnd"]
                    for item in approved
                    if not item.get("refunded", False)
                ),
                "points_available": sum(
                    self._point_balance(member["id"]) for member in members
                ),
                "redeemed_vnd": sum(
                    item["value_vnd"] for item in self.data["redemptions"]
                ),
                "can_undo": bool(self._undo_stack),
            },
        }
