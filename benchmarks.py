"""Small reproducible benchmark for the project report."""

from __future__ import annotations

import random
from statistics import fmean
from time import perf_counter

from rewards import (
    insertion_sort_transactions,
    merge_sort_transactions,
    selection_sort_transactions,
)


def average_milliseconds(operation, repeats: int) -> float:
    samples = []
    for _ in range(repeats):
        start = perf_counter()
        operation()
        samples.append((perf_counter() - start) * 1_000)
    return fmean(samples)


def main() -> None:
    randomizer = random.Random(20261013)
    print(
        "n,insertion_sort_ms,selection_sort_ms,merge_sort_ms,"
        "builtin_sort_ms,linear_search_us,dict_search_us"
    )
    for size in (100, 1_000, 10_000):
        # List keeps the generated records; dict below is a hash-table index
        # (average O(1) lookup versus the O(n) scan measured alongside it).
        transactions = [
            {"id": f"GD{index:05d}", "amount_vnd": randomizer.randrange(1_000, 10**9)}
            for index in range(size)
        ]
        randomizer.shuffle(transactions)
        index = {item["id"]: item for item in transactions}
        target = transactions[size // 2]["id"]
        repeats = 15 if size <= 100 else 7 if size <= 1_000 else 1
        insertion_ms = average_milliseconds(
            lambda: insertion_sort_transactions(transactions, "asc"), repeats
        )
        selection_ms = average_milliseconds(
            lambda: selection_sort_transactions(transactions, "asc"), repeats
        )
        merge_ms = average_milliseconds(
            lambda: merge_sort_transactions(transactions, "asc"), repeats
        )
        builtin_ms = average_milliseconds(
            lambda: sorted(
                transactions, key=lambda item: (item["amount_vnd"], item["id"])
            ),
            repeats,
        )
        linear_us = (
            average_milliseconds(
                lambda: next(item for item in transactions if item["id"] == target),
                repeats,
            )
            * 1_000
        )
        dict_us = (
            average_milliseconds(lambda: index[target], repeats) * 1_000
        )
        print(
            f"{size},{insertion_ms:.4f},{selection_ms:.4f},"
            f"{merge_ms:.4f},{builtin_ms:.4f},"
            f"{linear_us:.4f},{dict_us:.4f}"
        )


if __name__ == "__main__":
    main()
