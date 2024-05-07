"""
Helpers to read and write shapely polygons
"""
import zipfile
from pathlib import Path

import fiona
from ecodev_core import logger_get
from fiona.io import MemoryFile
from fiona.io import ZipMemoryFile
from shapely.geometry import mapping
from shapely.geometry import Point
from shapely.geometry import Polygon
from typing_extensions import TypeAlias

from ecodev_cloud.constants import SHP_EXT
from ecodev_cloud.constants import ZIP_EXT

log = logger_get(__name__)

CordexShape: TypeAlias = Polygon | list[Polygon] | list[Point]
CordexPoint: TypeAlias = Point


def save_polygon(file_path: Path, polygon: Polygon):
    """
    Store the passed polygon at file_path location
    """
    with fiona.open(file_path, 'w', 'ESRI Shapefile', {'geometry': 'Polygon'}) as c:
        c.write({'geometry': mapping(polygon)})


def load_shp(file_path: Path) -> CordexShape:
    """
    Retrieve a list of Polygons stored at file_path location
    """
    with fiona.open(file_path) as shape:
        parsed_shape = list(shape)
    return parsed_shape


def load_zipped_shp(zipped_data: bytes) -> CordexShape:
    """
    Retrieve a list of Polygons stored at file_path location
    """
    with ZipMemoryFile(zipped_data) as zip_memory_file:
        with zip_memory_file.open() as shape:
            parsed_shape = list(shape)
    return parsed_shape


def load_memory_gpkg(zipped_data: bytes) -> CordexShape:
    """
    Retrieve a list of Polygons stored at file_path location
    """
    with MemoryFile(zipped_data) as memory_file:
        with memory_file.open() as shape:
            parsed_shape = list(shape)
    return parsed_shape


def load_points(shape: list[dict]) -> list[Point]:
    """
    Retrieve a list of Points stored at file_path location
    """
    points = [Point(point['geometry']['coordinates'][1], point['geometry']['coordinates'][0])
              for point in shape]
    del shape
    return points


def load_polygon(shape: list[dict]) -> CordexShape:
    """
    Retrieve a Polygon or a list of Polygon stored at file_path location
    """
    coords = shape[0]['geometry']['coordinates']
    if shape[0]['geometry']['type'] == 'Polygon':
        polygon = Polygon(coords[0])
        del shape
        return polygon
    if shape[0]['geometry']['type'] == 'MultiPolygon':
        polygons = [Polygon(coords[i][0]) for i in range(len(coords))]
        del shape
        return polygons
    raise AttributeError('only Polygons can be loaded with this method')


def load_polygons(shape: list[dict]) -> CordexShape:
    """
    Retrieve a list of Polygons stored at file_path location
    """
    polygons = [Polygon(coords['geometry']['coordinates'][0]) for coords in shape]
    del shape
    return polygons


def save_shp(file_path: Path, data: CordexShape):
    """
    Save a shapely data on a s3 (a zip of the 4 files)
    """
    save_polygon(file_path, data)
    with zipfile.ZipFile(file_path.with_suffix(ZIP_EXT), mode='w') as f:
        for extension in [SHP_EXT, '.cpg', '.shx', '.dbf']:
            f.write(file_path.with_suffix(extension))
