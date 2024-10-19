from typing import List

import numpy as np
from PIL import Image


class Palette:
    def __init__(self, image_path: str) -> None:
        self.palette = self._load(image_path)

    def _load(self, path: str) -> np.ndarray:
        with Image.open(path).convert("P") as img:
            # Generate an extended 192 color palette
            raw_pal = np.array(img.getpalette()).reshape(-1, 3)
            extended_pal = np.tile(raw_pal[:64], (3, 1)).flatten()

            return extended_pal

    def as_list(self) -> List[int]:
        return self.palette.tolist()

    def get_index_for_tile(self, tile: np.ndarray) -> List[int]:
        return np.unique(tile // 16).tolist()
