"""How documentation states dataset sizes.

Country and blocktype counts are stated exactly; they change rarely. The intblock count
is stated rounded down to the hundred and written as ``N+`` (1304 -> ``1300+``), so a pull
request that adds records does not rewrite the documentation and the committed dataset
card, and two such pull requests do not conflict, until the count crosses a hundred.
"""

from __future__ import annotations


def intblocks_floor(count: int) -> int:
    """The intblock count rounded down to the hundred."""
    return count // 100 * 100


def documented_count(dataset: str, count: int) -> str:
    """``count`` as documentation and the dataset card state it."""
    return f"{intblocks_floor(count)}+" if dataset == "intblocks" else str(count)
