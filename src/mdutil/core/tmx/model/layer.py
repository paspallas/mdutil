import gzip
import io
import zlib
from abc import ABC, abstractmethod
from base64 import b64decode
from enum import Enum, auto
from typing import Any, Dict, List

import numpy as np
import zstandard as zstd

from mdutil.core.exceptions import TileLayerError
from mdutil.core.util import smart_repr

from .object import Object
from .property import CustomProperty


class LayerType(Enum):
    TILE = auto()
    OBJECT = auto()


class BaseLayer(ABC):
    def __init__(
        self,
        layer_type: LayerType,
        name: str,
        id_: int,
        width: int,
        height: int,
        properties: List[CustomProperty] = None,
    ) -> None:
        self.type = layer_type
        self.id = id_
        self.name = name
        self.width = width
        self.height = height
        self.properties = properties or []

    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]):
        pass


class TileLayerIterator:
    def __init__(self, data: List[int]):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration

        value = self.data[self.index]
        self.index += 1

        return value


class TileLayer(BaseLayer):
    def __init__(
        self,
        tile_data: List[int],
        name: str,
        id_: int,
        width: int,
        height: int,
        properties: List[CustomProperty] = None,
    ) -> None:
        super().__init__(LayerType.TILE, name, id_, width, height, properties)
        self.tile_data = tile_data

    def __iter__(self) -> TileLayerIterator:
        return TileLayerIterator(self.tile_data)

    def __len__(self) -> int:
        return len(self.tile_data)

    def __repr__(self) -> str:
        description = [smart_repr(self, exclude=("properties", "type", "tile_data"))]
        for prop in self.properties:
            description.append(f"   *{str(prop)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "TileLayer":
        encoding = data.get("encoding", "csv")

        if encoding == "csv":
            tile_data = TileData.from_csv(data.get("data", []))
        elif encoding == "base64":

            tiles = data.get("data", "")
            compression = data.get("compression", None)

            match compression:
                case None:
                    tile_data = TileData.from_base64(tiles)
                case "zlib":
                    tile_data = TileData.from_base64_zlib(tiles)
                case "gzip":
                    tile_data = TileData.from_base64_gzip(tiles)
                case "zstd":
                    tile_data = TileData.from_base64_zstd(tiles)
                case _:
                    raise TileLayerError(
                        f"Unsupported tile layer compression: {compression}"
                    )
        else:
            raise TileLayerError(f"Unsupported tile layer encoding: {encoding}")

        properties = [
            CustomProperty.from_dict(prop) for prop in data.get("properties", [])
        ]

        return cls(
            tile_data=tile_data,
            name=data.get("name", ""),
            id_=data.get("id", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            properties=properties,
        )


class TileData:
    @staticmethod
    def from_base64(tile_data: str) -> List[int]:
        return np.frombuffer(b64decode(tile_data), dtype=np.uint32).tolist()

    @staticmethod
    def from_base64_zlib(tile_data: str) -> List[int]:
        return np.frombuffer(
            zlib.decompress(b64decode(tile_data)), dtype=np.uint32
        ).tolist()

    @staticmethod
    def from_base64_gzip(tile_data: str) -> List[int]:
        with gzip.GzipFile(fileobj=io.BytesIO(b64decode(tile_data))) as f:
            return np.frombuffer(f.read(), dtype=np.uint32).tolist()

    @staticmethod
    def from_base64_zstd(tile_data: str) -> List[int]:
        decomp = zstd.ZstdDecompressor()
        return np.frombuffer(
            decomp.decompress(b64decode(tile_data)), dtype=np.uint32
        ).tolist()

    @staticmethod
    def from_csv(tile_data: List[str]) -> List[int]:
        return [int(tile) for tile in tile_data]


class ObjectLayerIterator:
    def __init__(self, data: List[int]):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration

        value = self.data[self.index]
        self.index += 1

        return value


class ObjectLayer(BaseLayer):
    def __init__(
        self,
        objects: List[Object],
        name: str,
        id_: int,
        width: int,
        height: int,
        properties: List[CustomProperty] = None,
    ) -> None:
        super().__init__(LayerType.OBJECT, name, id_, width, height, properties)
        self.objects = objects

    def __iter__(self) -> ObjectLayerIterator:
        return ObjectLayerIterator(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def __repr__(self) -> str:
        description = [smart_repr(self, exclude=("objects", "properties", "type"))]

        for prop in self.properties:
            description.append(f"   *{str(prop)}")

        for obj in self.objects:
            description.append(f"   +{str(obj)}")

        return "\n".join(description)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectLayer":
        objects = [Object.from_dict(obj) for obj in data.get("objects", [])]
        properties = [
            CustomProperty.from_dict(prop) for prop in data.get("properties", [])
        ]

        return cls(
            objects=objects,
            name=data.get("name", ""),
            id_=data.get("id", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            properties=properties,
        )
