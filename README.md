# csvwrangler

A lightweight CLI tool for quick CSV transformations, deduplication, and schema inference — no pandas required.

---

## Installation

```bash
pip install csvwrangler
```

Or install from source:

```bash
git clone https://github.com/yourname/csvwrangler.git
cd csvwrangler
pip install .
```

---

## Usage

```bash
# Infer schema of a CSV file
csvwrangler schema data.csv

# Remove duplicate rows
csvwrangler dedup data.csv --output clean.csv

# Transform: select columns and filter rows
csvwrangler transform data.csv --columns name,email,age --filter "age>30" --output result.csv

# Convert delimiter
csvwrangler transform data.csv --delimiter ";" --output semicolon.csv
```

### Example

```bash
$ csvwrangler schema employees.csv

Column        Type       Nulls
------------  ---------  -----
id            integer    0
name          string     0
email         string     3
hire_date     date       1
salary        float      0
```

---

## Features

- **Schema inference** — detect column types, null counts, and value ranges
- **Deduplication** — remove exact or fuzzy duplicate rows
- **Transformations** — filter, reorder, rename, and format columns
- **No heavy dependencies** — built on Python's standard library

---

## License

MIT © 2024 [yourname](https://github.com/yourname)