import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Union


class TmxParser(ABC):
    @abstractmethod
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        raise NotImplementedError


class JsonTmxParser(TmxParser):
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


class XmlTmxParser(TmxParser):
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        tree = ET.parse(file_path)
        return self._element_to_dict(tree.getroot())

    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        result = dict(element.attrib)

        for child in element:
            if child.tag in ["layer", "objectgroup"]:
                if "layers" not in result:
                    result["layers"] = []

                layer = self._element_to_dict(child)
                layer["type"] = "tilelayer" if child.tag == "layer" else "objectgroup"
                result["layers"].append(layer)
            elif child.tag == "tileset":
                if "tilesets" not in result:
                    result["tilesets"] = []

                tileset = self._element_to_dict(child)
                tileset["image"] = child.find("image").attrib["source"]
                result["tilesets"].append(tileset)
            elif child.tag == "data":
                for attr, val in child.attrib.items():
                    result[attr] = val
                if "encoding" in result.keys():
                    if result["encoding"] == "base64":
                        result["data"] = child.text.strip()
                    elif result["encoding"] == "csv":
                        result["data"] = child.text.strip().split(",")
                else:  # xml deprecated
                    result["data"] = [
                        dict(gid.items()).get("gid", 0) for gid in child.findall("tile")
                    ]
            elif child.tag == "object":
                if "objects" not in result:
                    result["objects"] = []
                result["objects"].append(self._element_to_dict(child))
            elif child.tag == "properties":
                if "properties" not in result:
                    result["properties"] = []

                properties = child.findall("property")
                for attr in properties:
                    prop = dict(attr.items())
                    if "type" not in prop:
                        prop["type"] = "string"

                    result["properties"].append(prop)

        # Convert relevant string attributes to the expected type
        for attr in ["x", "y"]:
            if attr in result:
                result[attr] = float(result[attr])

        for attr in [
            "width",
            "height",
            "id",
            "tilewidth",
            "tileheight",
            "tilecount",
            "spacing",
            "margin",
            "columns",
            "firstgid",
        ]:
            if attr in result:
                result[attr] = int(result[attr])

        return result
