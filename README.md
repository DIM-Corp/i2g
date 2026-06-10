# i2g — Image to Graph Converter

[![PyPI version](https://img.shields.io/pypi/v/i2g.svg)](https://pypi.org/project/i2g/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/DIM-Corp/i2g/actions/workflows/python-publish.yml/badge.svg)](https://github.com/DIM-Corp/i2g/actions/workflows/python-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Convert grayscale images into graph structures using NetworkX. Each pixel becomes a node connected to its neighbors (4- or 8-connectivity), with pixel intensity stored as a node attribute.

---

## Installation

```bash
pip install i2g
```

Or install from source in editable mode:

```bash
git clone https://github.com/DIM-Corp/i2g.git
cd i2g
pip install -e .[dev]
```

Requires Python 3.10+. Dependencies: `numpy`, `Pillow`, `networkx`.

---

## Usage

```python
from i2g import ImageGraphConverter

converter = ImageGraphConverter("my_image.png", connectivity="8")
graph, img_array = converter.convert()

shape = converter.shape()          # (height, width)
num_nodes, num_edges = converter.info()

print(f"Image shape: {shape}")
print(f"Graph has {num_nodes} nodes and {num_edges} edges.")
```

### Node attributes

Each node is keyed by `(row, col)` and carries two attributes:

| Attribute | Type | Description |
|---|---|---|
| `intensity` | `int` | Grayscale pixel value (0–255) |
| `pos` | `tuple[int, int]` | `(col, -row)` — ready for matplotlib/networkx plotting |

### Connectivity

| Value | Neighbors |
|---|---|
| `"4"` | Up, down, left, right |
| `"8"` (default) | Cardinal + diagonal (8 neighbors) |

### Error handling

| Situation | Exception raised |
|---|---|
| Invalid `connectivity` value | `ValueError` at construction time |
| Image file not found | `FileNotFoundError` from `convert()` |
| File exists but is not a valid image | `OSError` from `convert()` |
| Image exceeds 10 million pixels | `ValueError` from `convert()` |
| `shape()` or `info()` called before `convert()` | `RuntimeError` |

---

## Running tests

```bash
pytest
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contact

info@dimcorp237.com · mdieffi@gmail.com
