from pathlib import Path

from PIL import Image
import networkx as nx
import numpy as np

_MAX_PIXELS = 10_000_000

# Forward-only offsets avoid adding each undirected edge twice
_NEIGHBOR_OFFSETS: dict[str, list[tuple[int, int]]] = {
    "4": [(0, 1), (1, 0)],
    "8": [(0, 1), (1, 0), (1, 1), (1, -1)],
}


class ImageGraphConverter:
    def __init__(self, image_path: str | Path, connectivity: str = "8") -> None:
        """
        Initialize the ImageGraphConverter.

        Args:
            image_path: Path to the image file.
            connectivity: '4' for cardinal neighbors, '8' for cardinal + diagonal.

        Raises:
            ValueError: If connectivity is not '4' or '8'.
        """
        if connectivity not in _NEIGHBOR_OFFSETS:
            raise ValueError(f"connectivity must be '4' or '8', got {connectivity!r}")
        self.image_path = str(image_path)
        self.connectivity = connectivity
        self.img_array: np.ndarray | None = None
        self.graph: nx.Graph | None = None

    def convert(self) -> tuple[nx.Graph, np.ndarray]:
        """
        Convert the image into a graph structure.

        Each pixel becomes a node with 'intensity' (0-255) and 'pos' (col, -row)
        attributes. Edges connect adjacent pixels. The graph is undirected and
        unweighted.

        Returns:
            tuple: (networkx.Graph, numpy.ndarray)

        Raises:
            FileNotFoundError: If the image file does not exist.
            OSError: If the file cannot be opened as an image.
            ValueError: If the image exceeds the maximum allowed pixel count.
        """
        try:
            img = Image.open(self.image_path).convert("L")
        except FileNotFoundError:
            raise
        except Exception as e:
            raise OSError(f"Could not open image at {self.image_path!r}: {e}") from e

        self.img_array = np.array(img)
        height, width = self.img_array.shape

        if height * width > _MAX_PIXELS:
            raise ValueError(
                f"Image too large ({width}x{height} = {width * height:,} pixels); "
                f"maximum is {_MAX_PIXELS:,} pixels."
            )

        G = nx.Graph()
        for r in range(height):
            for c in range(width):
                G.add_node((r, c), intensity=int(self.img_array[r, c]), pos=(c, -r))

        offsets = _NEIGHBOR_OFFSETS[self.connectivity]
        for r in range(height):
            for c in range(width):
                for dr, dc in offsets:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        G.add_edge((r, c), (nr, nc))

        self.graph = G
        return self.graph, self.img_array

    def shape(self) -> tuple[int, int]:
        """
        Return the image dimensions as (height, width).

        Raises:
            RuntimeError: If convert() has not been called yet.
        """
        if self.img_array is None:
            raise RuntimeError("No image loaded. Call convert() first.")
        return self.img_array.shape

    def info(self) -> tuple[int, int]:
        """
        Return the number of nodes and edges in the graph.

        Raises:
            RuntimeError: If convert() has not been called yet.
        """
        if self.graph is None:
            raise RuntimeError("Graph not created. Call convert() first.")
        return self.graph.number_of_nodes(), self.graph.number_of_edges()
