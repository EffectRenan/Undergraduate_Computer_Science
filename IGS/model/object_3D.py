from model.interface_3D import Interface_3D
from math import isclose
from enum import Enum, auto

class _Type(Enum):
    ORIGINAL = auto()
    ENTERING = auto()
    EXITING = auto()

class Object_3D(Interface_3D):

    def __init__(self) -> None:
        super().__init__("Object_3D")
        self._mtl_prefix = "l"
        self.__subtype = ""
        self.__subcolor = ""

    @property
    def subtype(self) -> str:
        return self.__subtype

    @subtype.setter
    def subtype(self, type: str) -> None:
        self.__subtype = type

    @property
    def subcolor(self) -> str:
        return self.__subcolor

    @subcolor.setter
    def subcolor(self, type: str) -> None:
        self.__subcolor = type

    def _check(self, coordinates: list) -> list:
        if coordinates != None:
            if len(coordinates) < 2 or \
                not isinstance(coordinates[0], tuple):

                raise Exception("Object_3D error: The format must be (x0, y0, z0),(x1, y1, z1), ...")

        return coordinates

    def _parsing(self, _coordinates) -> list:
        coordinates = list(self._string_to_tuple(_coordinates))

        # It's necessary to link the last point with the first one.
        if len(coordinates) > 2:
            coordinates.append(coordinates[0])

        return coordinates

    def clipping(self, window: list) -> None:
        # Clipping implemented by an object 2D
        pass
