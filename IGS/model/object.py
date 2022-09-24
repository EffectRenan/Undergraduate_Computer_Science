from abc import abstractclassmethod, abstractmethod

from ast import literal_eval as make_tuple
import re
import numpy as np

class Object:

    def __init__(self, type: str) -> None:
        self.__type = type
        self.__name = ""
        self.__coordinates = []
        self.__color = "#000000"
        self._mtl_prefix = ""

    @property
    def type(self) -> str:
        return self.__type

    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, name) -> None:
        self.__name = name

    @property
    def coordinates(self) -> list:
        return self.__coordinates
    
    @coordinates.setter
    def coordinates(self, coordinates) -> None:
        if isinstance(coordinates, str):
            coordinates = self._parsing(coordinates)
        self.__coordinates = self._check(coordinates)

    @property
    def color(self) -> str:
        return self.__color

    @color.setter
    def color(self, color: str) -> None:
        self.__color = color

    @abstractmethod
    def _check(self, coordinates: list) -> None:
        pass

    @abstractmethod 
    def _parsing(self, string_coordinates: str) -> list:
        pass

    @abstractclassmethod
    def clipping(self) -> bool:
        pass

    def _string_to_tuple(self, string_coordinates: str) -> tuple:
        return make_tuple(self._sanitize(string_coordinates))

    def _sanitize(self, string: str) -> str:
        pattern = re.compile('([0-9\(\)\,\.\-\+e\ ])')
        sanitized = re.findall(pattern, string)
        return ''.join(sanitized)

    def get_center(self) -> tuple:
        x_sum = 0
        y_sum = 0
        for coord in self.__coordinates:
            x_sum += coord[0]
            y_sum += coord[1]

        x_sum = x_sum / len(self.__coordinates)
        y_sum = y_sum / len(self.__coordinates)
        return (x_sum, y_sum)

    def build_translation_matrix(self, Dx: float, Dy: float) -> list: 
        #
        # Build translation matrix as:
        #    [1   0  0]
        #    [0   1  0]
        #    [Dx  Dy 1]
        #

        matrix = np.identity(3)
        matrix[2][0] = Dx
        matrix[2][1] = Dy
        return matrix

    def build_scaling_matrix(self, Sx: float, Sy: float) -> list:
        #
        # Build scaling matrix as:
        #    [Sx0  0]
        #    [0  Sy 0]
        #    [0  0  1]
        #

        matrix = np.identity(3)
        matrix[0][0] = Sx
        matrix[1][1] = Sy
        return matrix

    def build_rotation_matrix(self, degree: float) -> list:
        #
        # Build rotation matrix as:
        #    [cos(O) -sin(O) 0]
        #    [sin(O)  cos(O) 0]
        #    [0       0      1]
        #

        matrix = np.identity(3)
        cos = np.cos(np.deg2rad(degree))
        sin = np.sin(np.deg2rad(degree))
        matrix[0][0] = cos
        matrix[1][1] = cos
        matrix[0][1] = -sin
        matrix[1][0] = sin
        return matrix

    def concat_matrix(self, matrixes: list) -> np.ndarray:
        final = matrixes[0]
        for matrix in matrixes[1:]:
            final = final.dot(matrix)
            
        return final

    #apply XD transform
    def transform(self, points: list, matrix: np.ndarray) -> list:
        new_points = []    
        for p in points:
            m = np.array([p[0], p[1], 1]) #Homogeneous_Coordinates
            o = m.dot(matrix)
            new_points.append((o[0],o[1]))
            
        return new_points

    def rotate(self, degree: float, target: tuple) -> None:
        t_translate = self.build_translation_matrix(-target[0], -target[1]) 
        t_matrix = self.build_rotation_matrix(degree)
        t_origin = self.build_translation_matrix(target[0], target[1])
        
        t_m = self.concat_matrix((t_translate, t_matrix , t_origin))
        self.__coordinates = self.transform(self.__coordinates, t_m)

    def translate(self, vector: tuple) -> None:
        t_matrix = self.build_translation_matrix(vector[0], vector[1])
        t =  self.transform(self.__coordinates, t_matrix) 
        self.__coordinates = t

    def scale(self, scale: tuple) -> None:
        center = self.get_center()

        t_matrix = self.concat_matrix([
            self.build_translation_matrix(-center[0], -center[1]),
            self.build_scaling_matrix(scale[0], scale[1]),
            self.build_translation_matrix(center[0], center[1])
        ])    
        self.__coordinates = self.transform(self.__coordinates, t_matrix)

    def __color_int(self) -> str:
        color = ""
        if len(self.__color) == 7:
            for i in range(1, len(self.__color), 2):
                color += f"{int(self.__color[i]+self.__color[i+1], 16)} "
        else:
            color += f"{int(self.__color[1] + self.__color[1], 16)} " * 3

        return color

    def color_hex(self, color_int: list) -> str:
        color = "#"
        for i in color_int:
            _hex = hex(int(i))[2:]
            if len(_hex) == 1:
                color += "0" + _hex
            else:
                color += _hex

        return color

    def obj_string(self, count: int) -> list:
        part1 = ""
        label = f"color_{count}"
        
        mtl = f"newmtl {label}\n"
        mtl += f"Kd {self.__color_int()}\n"
        
        part2 = f"o {self.__name}\n"
        part2 += f"usemtl {label}\n"
        part2 += self._mtl_prefix + " "

        for coord in self.__coordinates:
            part1 += f"v {coord[0]} {coord[1]} 0.0\n"
            part2 += f"{count} "
            count += 1

        return [part1, part2, mtl, count]

    def view_transform(self, window: dict, viewPort: dict) -> list:
        all = []
        
        for coordinate in self.__coordinates:
            xw = coordinate[0]
            yw = coordinate[1]
            xvp = viewPort["xvpMin"] + (xw - window["xwMin"]) / (window["xwMax"] - window["xwMin"]) \
                * (viewPort["xvpMax"] - viewPort["xvpMin"]*2)

            yvp = viewPort["yvpMin"] + (1 - (yw - window["ywMin"]) / (window["ywMax"] - window["ywMin"])) \
                * (viewPort["yvpMax"] - viewPort["yvpMin"]*2)

            all.append(xvp)
            all.append(yvp)

        return all
