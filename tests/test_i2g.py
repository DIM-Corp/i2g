import pytest
import numpy as np
import networkx as nx
from PIL import Image
from i2g import ImageGraphConverter


@pytest.fixture
def sample_image(tmp_path):
    img_array = np.array(
        [[100, 150, 200], [50, 100, 150], [0, 50, 100]],
        dtype=np.uint8,
    )
    img_path = tmp_path / "test_image.png"
    Image.fromarray(img_array).save(img_path)
    return img_path, img_array


def test_4_connectivity(sample_image):
    img_path, _ = sample_image
    converter = ImageGraphConverter(str(img_path), connectivity="4")
    G, img_loaded = converter.convert()

    assert isinstance(G, nx.Graph)
    assert img_loaded.shape == (3, 3)

    num_nodes, num_edges = converter.info()
    assert num_nodes == 9
    assert num_edges == 12  # rows*(cols-1) + (rows-1)*cols = 6+6


def test_8_connectivity(sample_image):
    img_path, _ = sample_image
    converter = ImageGraphConverter(str(img_path), connectivity="8")
    G, img_loaded = converter.convert()

    assert isinstance(G, nx.Graph)
    num_nodes, num_edges = converter.info()
    assert num_nodes == 9
    assert num_edges == 20  # 12 cardinal + 8 diagonal


def test_node_attributes(sample_image):
    img_path, _ = sample_image
    converter = ImageGraphConverter(str(img_path), connectivity="4")
    G, _ = converter.convert()

    assert G.nodes[(0, 0)]["intensity"] == 100
    assert G.nodes[(0, 0)]["pos"] == (0, 0)
    assert G.nodes[(0, 2)]["intensity"] == 200
    assert G.nodes[(0, 2)]["pos"] == (2, 0)
    assert G.nodes[(2, 0)]["intensity"] == 0
    assert G.nodes[(2, 0)]["pos"] == (0, -2)


def test_shape(sample_image):
    img_path, _ = sample_image
    converter = ImageGraphConverter(str(img_path))
    converter.convert()
    assert converter.shape() == (3, 3)


def test_non_square_image(tmp_path):
    img_array = np.zeros((2, 5), dtype=np.uint8)
    img_path = tmp_path / "wide.png"
    Image.fromarray(img_array).save(img_path)

    converter = ImageGraphConverter(str(img_path), connectivity="4")
    G, img_loaded = converter.convert()
    assert img_loaded.shape == (2, 5)
    num_nodes, num_edges = converter.info()
    assert num_nodes == 10
    assert num_edges == 13  # 2*(5-1) + (2-1)*5 = 8+5


def test_single_pixel_image(tmp_path):
    img_array = np.array([[128]], dtype=np.uint8)
    img_path = tmp_path / "single.png"
    Image.fromarray(img_array).save(img_path)

    converter = ImageGraphConverter(str(img_path), connectivity="8")
    G, _ = converter.convert()
    num_nodes, num_edges = converter.info()
    assert num_nodes == 1
    assert num_edges == 0


def test_pathlib_path(sample_image):
    img_path, _ = sample_image
    converter = ImageGraphConverter(img_path)  # Path object, not string
    G, img_loaded = converter.convert()
    assert isinstance(G, nx.Graph)
    assert img_loaded.shape == (3, 3)


def test_invalid_connectivity():
    with pytest.raises(ValueError, match="connectivity must be '4' or '8'"):
        ImageGraphConverter("any.png", connectivity="5")


def test_file_not_found(tmp_path):
    converter = ImageGraphConverter(str(tmp_path / "nonexistent.png"))
    with pytest.raises(FileNotFoundError):
        converter.convert()


def test_shape_before_convert(tmp_path):
    converter = ImageGraphConverter(str(tmp_path / "any.png"))
    with pytest.raises(RuntimeError, match="convert"):
        converter.shape()


def test_info_before_convert(tmp_path):
    converter = ImageGraphConverter(str(tmp_path / "any.png"))
    with pytest.raises(RuntimeError, match="convert"):
        converter.info()
