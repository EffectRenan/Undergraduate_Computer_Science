from model.interface_3D import Interface_3D
from numbers import Number

class Point_3D(Interface_3D):

    def __init__(self) -> None:
        super().__init__("Point_3D")
        self._mtl_prefix = "p"

    def _check(self, coordinates: list) -> list:
        if coordinates != None:
            if len(coordinates) != 1 or \
                not isinstance(coordinates[0][0], Number) or \
                not isinstance(coordinates[0], tuple) or \
                len(coordinates[0]) != 3:
                
                raise Exception("Point error: The format must be (x, y, z).")

        return coordinates

    def _parsing(self, string_coordinates: str) -> list:
        return [self._string_to_tuple(string_coordinates)]

    def clipping(self, window: list) -> None:
        # Clipping implemented by a point 2D
        pass
