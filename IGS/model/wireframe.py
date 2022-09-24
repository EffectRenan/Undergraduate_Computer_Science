from model.object import Object

class Wireframe(Object):

    def __init__(self) -> None:
        super().__init__("Wireframe")
        self._mtl_prefix = "l"
        self.__subtype = ""
        self.__subcolor = ""
        self.__from_object_3D = False

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
    
    @property
    def from_object_3D(self) -> bool:
        return self.__from_object_3D

    @from_object_3D.setter
    def from_object_3D(self, value: str) -> None:
        self.__from_object_3D = value

    def _check(self, coordinates: list) -> list:
        if coordinates != None:
            if len(coordinates) < 2 or \
                not isinstance(coordinates[0], tuple):

                raise Exception("Wireframe error: The format must be (x0, y0),(x1, y1), ...")

        return coordinates

    def _parsing(self, _coordinates) -> list:
        coordinates = list(self._string_to_tuple(_coordinates))

        # It's necessary to link the last point with the first one.
        if len(coordinates) > 2:
            coordinates.append(coordinates[0])

        return coordinates

    def clipping(self, window: list) -> None:
        if self.__from_object_3D == False:
            self.__sutherland_hodgeman(window)  

    def __line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
           raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return (x, y)

    def __sutherland_hodgeman_left(self, window: list, user_coordinates: list) -> list:
        window_x_min = window[0][0]
        window_x_max = window[0][1]

        window_y_min = window[1][0]
        window_y_max = window[1][1]

        x = 0
        y = 1

        coordinates = []

        prev = user_coordinates[0]
        i = 1
        while i < len(user_coordinates):

            current = user_coordinates[i]

            window_side1 = (window_x_min, window_y_min)
            window_side2 = (window_x_min, window_y_max)
            window_line = (window_side1, window_side2)

            if prev[x] < window_x_min and current[x] >= window_x_min:
            
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = intersection 
                p2 = current 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[x] >= window_x_min and current[x] < window_x_min:
            
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = prev 
                p2 = intersection 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[x] < window_x_min and current[x] < window_x_min:
                if (i + 1) < len(self.coordinates):
                    i += 1
                    current = self.coordinates[i]
            elif prev[x] >= window_x_min and current[x] >= window_x_min:
                coordinates.append(prev)
                coordinates.append(current)
            
            prev = current
            i += 1

        return coordinates

    def __sutherland_hodgeman_right(self, window: list, user_coordinates: list) -> list:
        window_x_min = window[0][0]
        window_x_max = window[0][1]

        window_y_min = window[1][0]
        window_y_max = window[1][1]

        x = 0
        y = 1

        coordinates = []

        prev = user_coordinates[0]
        i = 1
        while i < len(user_coordinates):

            current = user_coordinates[i]

            window_side1 = (window_x_max, window_y_min)
            window_side2 = (window_x_max, window_y_max)
            window_line = (window_side1, window_side2)

            if prev[x] > window_x_max and current[x] <= window_x_max:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = intersection 
                p2 = current 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[x] <= window_x_max and current[x] > window_x_max:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = prev 
                p2 = intersection 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[x] > window_x_max and current[x] > window_x_max:
                if (i + 1) < len(self.coordinates):
                    i += 1
                    current = self.coordinates[i]
            elif prev[x] <= window_x_max and current[x] <= window_x_max:
                coordinates.append(prev)
                coordinates.append(current)
            
            prev = current
            i += 1

        return coordinates

    def __sutherland_hodgeman_bottom(self, window: list, user_coordinates: list) -> list:
        window_x_min = window[0][0]
        window_x_max = window[0][1]

        window_y_min = window[1][0]
        window_y_max = window[1][1]

        x = 0
        y = 1

        coordinates = []

        prev = user_coordinates[0]
        i = 1
        while i < len(user_coordinates):

            current = user_coordinates[i]

            window_side1 = (window_x_min, window_y_min)
            window_side2 = (window_x_max, window_y_min)
            window_line = (window_side1, window_side2)

            if prev[y] < window_y_min and current[y] >= window_y_min:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = intersection 
                p2 = current 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[y] >= window_y_min and current[y] < window_y_min:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = prev 
                p2 = intersection 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[y] < window_y_min and current[y] < window_y_min:
                if (i + 1) < len(self.coordinates):
                    i += 1
                    current = self.coordinates[i]
            elif prev[y] >= window_y_min and current[y] >= window_y_min:
                coordinates.append(prev)
                coordinates.append(current)
            
            prev = current
            i += 1

        return coordinates
    
    def __sutherland_hodgeman_top(self, window: list, user_coordinates: list) -> list:
        window_x_min = window[0][0]
        window_x_max = window[0][1]

        window_y_min = window[1][0]
        window_y_max = window[1][1]

        x = 0
        y = 1

        coordinates = []

        prev = user_coordinates[0]
        i = 1
        while i < len(user_coordinates):

            current = user_coordinates[i]

            window_side1 = (window_x_min, window_y_max)
            window_side2 = (window_x_max, window_y_max)
            window_line = (window_side1, window_side2)

            if prev[y] > window_y_max and current[y] <= window_y_max:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = intersection 
                p2 = current 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[y] <= window_y_max and current[x] > window_y_max:
                current_line = (prev, current)
                intersection = self.__line_intersection(current_line, window_line)

                p1 = prev 
                p2 = intersection 
                coordinates.append(p1)
                coordinates.append(p2)
            elif prev[y] > window_y_max and current[y] > window_y_max:
                if (i + 1) < len(self.coordinates):
                    i += 1
                    current = self.coordinates[i]
            elif prev[y] <= window_y_max and current[y] <= window_y_max:
                coordinates.append(prev)
                coordinates.append(current)
            
            prev = current
            i += 1

        return coordinates

    def __sutherland_hodgeman(self, window):
        coordinates = self.__sutherland_hodgeman_left(window, self.coordinates)
        coordinates = self.__sutherland_hodgeman_top(window, coordinates)
        coordinates = self.__sutherland_hodgeman_right(window, coordinates)
        coordinates = self.__sutherland_hodgeman_bottom(window, coordinates)
        self.coordinates = coordinates
