
from model.object import Object
from numbers import Number

class Point(Object):

    def __init__(self) -> None:
        super().__init__("Point")
        self._mtl_prefix = "p"

    def _check(self, coordinates: list) -> list:
        if coordinates != None:
            if len(coordinates) != 1 or \
                not isinstance(coordinates[0][0], Number) or \
                not isinstance(coordinates[0], tuple) or \
                len(coordinates[0]) != 2:
                
                raise Exception("Point error: The format must be (x, y).")

        return coordinates

    def _parsing(self, string_coordinates: str) -> list:
        return [self._string_to_tuple(string_coordinates)]

    def clipping(self, window: list) -> None:
        # window:
        # [0] (xMim, xMax)
        # [1] (ymin, yMax)

        x = self.coordinates[0][0]
        y = self.coordinates[0][1]

        if x >= window[0][0] and x <= window[0][1] and \
            y >= window[1][0] and y <= window[1][1]:
            pass
        else:
            self.coordinates = None
