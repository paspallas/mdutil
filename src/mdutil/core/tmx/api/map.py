from mdutil.core.tmx.model import TmxMap


class MapApi:
    def __init__(self, tmx_map: TmxMap) -> None:
        self._map = tmx_map
