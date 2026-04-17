"""Row sampling utilities for CSV files."""

import csv
import random
from typing import List, Dict, Optional


def sample_rows(
    rows: List[Dict[str, str]],
    n: int,
    mode: str = "random",
    seed: Optional[int] = None,
) -> List[Dict[str, str]]:
    """Sample rows from a list of row dicts.

    Args:
        rows: Input rows as list of dicts.
        n: Number of rows to return.
        mode: Sampling mode — 'random', 'first', or 'last'.
        seed: Optional random seed for reproducibility.

    Returns:
        Sampled list of row dicts.

    Raises:
        ValueError: If mode is unknown or n is negative.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    if mode not in ("random", "first", "last"):
        raise ValueError(f"Unknown sampling mode: {mode!r}. Choose 'random', 'first', or 'last'.")

    if mode == "first":
        return rows[:n]
    if mode == "last":
        return rows[-n:] if n > 0 else []

    # random
    rng = random.Random(seed)
    k = min(n, len(rows))
    return rng.sample(rows, k)


def sample_file(
    input_path: str,
    output_path: str,
    n: int,
    mode: str = "random",
    seed: Optional[int] = None,
) -> int:
    """Sample rows from a CSV file and write to output.

    Args:
        input_path: Path to the input CSV file.
        output_path: Path to write the sampled CSV output.
        n: Number of rows to sample.
        mode: Sampling mode — 'random', 'first', or 'last'.
        seed: Optional random seed for reproducibility.

    Returns:
        Number of rows written.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: Propagated from sample_rows for invalid arguments.
    """
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    sampled = sample_rows(rows, n, mode=mode, seed=seed)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sampled)

    return len(sampled)
