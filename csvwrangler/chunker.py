"""Split CSV rows into fixed-size chunks, yielding one chunk at a time."""

from typing import Iterator, List, Dict


def chunk_rows(
    rows: List[Dict[str, str]],
    size: int,
) -> Iterator[List[Dict[str, str]]]:
    """Yield successive chunks of *size* rows from *rows*.

    Parameters
    ----------
    rows:
        Input rows as dicts.
    size:
        Maximum number of rows per chunk.  Must be >= 1.

    Yields
    ------
    list of dicts
        Each yielded list contains at most *size* rows.

    Raises
    ------
    ValueError
        If *size* is less than 1.
    """
    if size < 1:
        raise ValueError(f"chunk size must be >= 1, got {size}")

    chunk: List[Dict[str, str]] = []
    for row in rows:
        chunk.append(row)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def chunk_file(
    reader,
    writer,
    size: int,
    chunk_index: int,
) -> None:
    """Write a single chunk (0-based *chunk_index*) from *reader* to *writer*.

    Parameters
    ----------
    reader:
        An iterable of row dicts (e.g. ``csv.DictReader``).
    writer:
        A ``csv.DictWriter``-compatible object with ``writeheader`` /
        ``writerow`` methods.
    size:
        Rows per chunk.
    chunk_index:
        Which chunk to output (0-based).
    """
    rows = list(reader)
    chunks = list(chunk_rows(rows, size))
    if chunk_index >= len(chunks):
        writer.writeheader()
        return
    writer.writeheader()
    for row in chunks[chunk_index]:
        writer.writerow(row)
