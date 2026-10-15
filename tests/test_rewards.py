import json
from pathlib import Path
import tempfile
import unittest

from rewards import (
    RewardsBook,
    RewardsError,
    insertion_sort_transactions,
    merge_sort_transactions,
    selection_sort_transactions,
)


def empty_state():
    return {
        "members": [
            {"id": "TV001", "name": "Nguyễn An", "tier": "Bạc"},
            {"id": "TV002", "name": "Trần Bình", "tier": "Vàng"},
        ],
        "transactions": [],
        "redemptions": [],
    }


class RewardsBookTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.state_path = Path(self.temporary_directory.name) / "store.json"
        self.book = RewardsBook(self.state_path, empty_state())

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_purchase_awards_cashback_and_whole_points(self):
        transaction = self.book.add_transaction("tv001", 125_999, "Siêu thị")
        self.assertEqual(transaction["cashback_vnd"], 1_259)
        self.assertEqual(transaction["points"], 12)
        self.assertEqual(transaction["status"], "approved")
        self.assertEqual(self.book.snapshot()["summary"]["cashback_vnd"], 1_259)

    def test_large_purchase_waits_for_review_before_awarding(self):
        transaction = self.book.add_transaction("TV001", 5_000_001, "Điện tử")
        self.assertEqual(transaction["status"], "pending")
        self.assertEqual(self.book.snapshot()["summary"]["points_available"], 0)
        self.assertEqual(self.book.process_next_review("fifo")["id"], transaction["id"])
        self.assertEqual(self.book.snapshot()["summary"]["points_available"], 500)

    def test_priority_review_processes_largest_pending_transaction(self):
        smaller = self.book.add_transaction("TV001", 6_000_000, "Du lịch")
        larger = self.book.add_transaction("TV002", 9_000_000, "Điện tử")
        self.assertEqual(self.book.process_next_review("priority")["id"], larger["id"])
        self.assertEqual(self.book.process_next_review("fifo")["id"], smaller["id"])

    def test_merge_sort_orders_amount_and_stably_breaks_ties_by_id(self):
        transactions = [
            {"id": "GD0003", "amount_vnd": 100},
            {"id": "GD0002", "amount_vnd": 200},
            {"id": "GD0001", "amount_vnd": 200},
        ]
        self.assertEqual(
            [item["id"] for item in merge_sort_transactions(transactions, "desc")],
            ["GD0001", "GD0002", "GD0003"],
        )
        self.assertEqual(
            [item["id"] for item in merge_sort_transactions(transactions, "asc")],
            ["GD0003", "GD0001", "GD0002"],
        )
        self.assertEqual(merge_sort_transactions([], "asc"), [])

    def test_sort_transactions_by_newest_and_oldest(self):
        older = self.book.add_transaction("TV001", 10_000, "Siêu thị")
        newer = self.book.add_transaction("TV002", 20_000, "Ăn uống")
        self.assertEqual(
            [item["id"] for item in self.book.sort_transactions("newest")],
            [newer["id"], older["id"]],
        )
        self.assertEqual(
            [item["id"] for item in self.book.sort_transactions("oldest")],
            [older["id"], newer["id"]],
        )
        with self.assertRaises(RewardsError):
            self.book.sort_transactions("invalid")

    def test_insertion_and_selection_sort_orders_and_validates(self):
        transactions = [
            {"id": "GD0003", "amount_vnd": 100},
            {"id": "GD0002", "amount_vnd": 200},
            {"id": "GD0001", "amount_vnd": 200},
        ]
        for algorithm in (insertion_sort_transactions, selection_sort_transactions):
            with self.subTest(algorithm=algorithm.__name__):
                self.assertEqual(
                    [item["id"] for item in algorithm(transactions, "desc")],
                    ["GD0001", "GD0002", "GD0003"],
                )
                self.assertEqual(
                    [item["id"] for item in algorithm(transactions, "asc")],
                    ["GD0003", "GD0001", "GD0002"],
                )
                self.assertEqual(algorithm([], "asc"), [])
                with self.assertRaises(RewardsError):
                    algorithm(transactions, "invalid")

    def test_search_is_indexed_and_returns_a_copy(self):
        transaction = self.book.add_transaction("TV001", 10_000, "Ăn uống")
        result = self.book.find_transaction(transaction["id"].lower())
        self.assertEqual(result["id"], transaction["id"])
        result["amount_vnd"] = 1
        self.assertNotEqual(self.book.find_transaction(transaction["id"])["amount_vnd"], 1)
        self.assertIsNone(self.book.find_transaction("GD9999"))

    def test_redemption_debits_points_and_returns_vnd_value(self):
        self.book.add_transaction("TV001", 1_000_000, "Siêu thị")
        redemption = self.book.redeem_points("TV001", 100)
        self.assertEqual(redemption["value_vnd"], 10_000)
        self.assertEqual(self.book.snapshot()["members"][0]["points_balance"], 0)

    def test_redemption_rejects_insufficient_or_invalid_points(self):
        self.book.add_transaction("TV001", 500_000, "Siêu thị")
        with self.assertRaises(RewardsError):
            self.book.redeem_points("TV001", 100)
        with self.assertRaises(RewardsError):
            self.book.redeem_points("TV001", 50)
        with self.assertRaises(RewardsError):
            self.book.redeem_points("TV001", True)

    def test_refund_reverses_rewards_and_prevents_duplicate_refund(self):
        transaction = self.book.add_transaction("TV001", 1_000_000, "Siêu thị")
        refunded = self.book.refund_transaction(transaction["id"])
        self.assertTrue(refunded["refunded"])
        summary = self.book.snapshot()["summary"]
        self.assertEqual(summary["cashback_vnd"], 0)
        self.assertEqual(summary["points_available"], 0)
        with self.assertRaises(RewardsError):
            self.book.refund_transaction(transaction["id"])

    def test_refund_is_blocked_after_awarded_points_are_spent(self):
        transaction = self.book.add_transaction("TV001", 1_000_000, "Siêu thị")
        self.book.redeem_points("TV001", 100)
        with self.assertRaisesRegex(
            RewardsError,
            "(?i)số dư điểm của khách nhỏ hơn số điểm cần hoàn",
        ):
            self.book.refund_transaction(transaction["id"])

    def test_undo_restores_previous_state_and_persists_it(self):
        transaction = self.book.add_transaction("TV001", 1_000_000, "Siêu thị")
        self.assertTrue(self.book.undo())
        self.assertIsNone(self.book.find_transaction(transaction["id"]))
        self.assertFalse(self.book.undo())
        restored = RewardsBook(self.state_path, empty_state())
        self.assertEqual(restored.snapshot()["summary"]["transaction_count"], 0)

    def test_saved_data_survives_restart(self):
        transaction = self.book.add_transaction("TV001", 750_000, "Ăn uống")
        restored = RewardsBook(self.state_path, empty_state())
        self.assertEqual(restored.find_transaction(transaction["id"]), transaction)
        with self.state_path.open("r", encoding="utf-8") as stream:
            self.assertEqual(json.load(stream)["transactions"][0]["id"], transaction["id"])

    def test_rejects_invalid_amount_category_and_member(self):
        for amount in (999, 1_000_000_001, True, 1.5):
            with self.subTest(amount=amount), self.assertRaises(RewardsError):
                self.book.add_transaction("TV001", amount, "Siêu thị")
        with self.assertRaises(RewardsError):
            self.book.add_transaction("TV999", 10_000, "Siêu thị")
        with self.assertRaises(RewardsError):
            self.book.add_transaction("TV001", 10_000, " ")

    def test_pending_queue_can_be_empty(self):
        self.assertIsNone(self.book.process_next_review("fifo"))


if __name__ == "__main__":
    unittest.main()
