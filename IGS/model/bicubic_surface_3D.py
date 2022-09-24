from copy import deepcopy
from numpy.core.multiarray import array
from model.interface_3D import Interface_3D
import numpy as np

class Bicubic_Surface_3D(Interface_3D):

    def __init__(self) -> None:
        super().__init__("Bicubic_Surface_3D")
        self._mtl_prefix = "surf"
        self.__subtype = ""
        self.__subcolor = ""
        self.__step = 0.025

    @property
    def subtype(self) -> None:
        return self.__subtype

    @subtype.setter
    def subtype(self, type: str) -> None:
        self.__subtype = type

    @property
    def subcolor(self) -> None:
        return self.__subcolor

    @subcolor.setter
    def subcolor(self, type: str) -> None:
        self.__subcolor = type
    
    @property
    def coordinates_set(self) -> None:
        return self.__coordinates_set

    def _check(self, coordinates: list) -> list:

        # Only fix the curve if the object is new.
        if len(self.coordinates) == 0 and self.__subtype != "file":
            if self.__subtype == "Bezier": 
                return self.__create_bezier(coordinates)
            else:
                return self.__create_b_spline(coordinates)
        elif len(coordinates) >= 16:
            return coordinates
        else:
            return None

    def _parsing(self, coordinates: str) -> list:
        return list(self._string_to_tuple(coordinates))

    def clipping(self, window: list) -> None:
        # Clipping implemented by an object 2D
        pass


    def __create_bezier(self, user_coordinates: list) -> list:

        # Bezier matrix
        m = np.array([
            [-1, 3 , -3, 1],
            [3 , -6, 3 , 0],
            [-3, 3 , 0 , 0],
            [1 , 0 , 0 , 0]
        ])

        # transpose
        mt = m.transpose()

        # Geometry matrix
        gx = self.__bezier_geometric_matrix(user_coordinates, 0)
        gy = self.__bezier_geometric_matrix(user_coordinates, 1)
        gz = self.__bezier_geometric_matrix(user_coordinates, 2)

        return self.__bezier_blending_function(m, mt, gx, gy, gz)


    def __bezier_geometric_matrix(self, user_coordinates: list, type: int) ->  np.ndarray:
        tmp = []

        for coord in user_coordinates:
            tmp.append(coord[type])

        g = np.array([])
        for i in range(0, len(tmp), 16+1):
            g = np.array([
                [tmp[i] , tmp[i+1] , tmp[i+2] , tmp[i+3]],
                [tmp[i+4] , tmp[i+5] , tmp[i+6] , tmp[i+7]],
                [tmp[i+8] , tmp[i+9] , tmp[i+10], tmp[i+11]],
                [tmp[i+12], tmp[i+13], tmp[i+14], tmp[i+15]],
            ])

        g = g.transpose()

        return g

    def __bezier_blending_function(self, m: np.ndarray, mt: np.ndarray, 
        gx: np.ndarray, gy: np.ndarray, gz: np.ndarray) -> list:

        begin = 0
        stop = 1

        new_coordinates = []

        # First side
        t = begin
        while t < stop:
            Tt = np.array([t ** 3, t ** 2, t, 1]).transpose()

            s = begin
            while s < stop:

                S = np.array([s ** 3, s ** 2, s, 1])

                x = self.concat_matrix([S, m, gx, mt, Tt])
                y = self.concat_matrix([S, m, gy, mt, Tt])
                z = self.concat_matrix([S, m, gz, mt, Tt])
                new_coordinates.append((x, y, z))

                s += self.__step

            t += self.__step

        # Second side
        s = begin
        while s < stop:
            S = np.array([s ** 3, s ** 2, s, 1])

            t = begin
            while t < stop:
                Tt = np.array([t ** 3, t ** 2, t, 1]).transpose()


                x = self.concat_matrix([S, m, gx, mt, Tt])
                y = self.concat_matrix([S, m, gy, mt, Tt])
                z = self.concat_matrix([S, m, gz, mt, Tt])
                new_coordinates.append((x, y, z))

                t += self.__step

            s += self.__step
        
        return new_coordinates

    
    def __create_b_spline(self, user_coordinates: list) -> list:

        # B-Spline
        m = np.array([
            [-1.0, 3.0, -3.0, 1.0], 
            [3.0, -6.0,  3.0, 0.0], 
            [-3.0, 0.0,  3.0, 0.0], 
            [1.0,  4.0,  1.0, 0.0]
        ])

        m *= 1 / 6

        # matrix is represented by an unidimensional array
        # As the matrix  4*ix4*i fo size, lines and columns have the same size 
        lines_columns_qtt = self.__lines_columns_qtt(len(user_coordinates))

        repetitions = lines_columns_qtt - 4 + 1

        coordinates = []

        # S
        for line in range(repetitions):
            for column in range(repetitions):
                gx = self.__b_spline_geometric_matrix(user_coordinates, 0, line, column, lines_columns_qtt)
                cx = m.dot(gx).dot(m.transpose())

                gy = self.__b_spline_geometric_matrix(user_coordinates, 1, line, column, lines_columns_qtt)
                cy = m.dot(gy).dot(m.transpose())

                gz = self.__b_spline_geometric_matrix(user_coordinates, 2, line, column, lines_columns_qtt)
                cz = m.dot(gz).dot(m.transpose())

                coordinates += self.__b_spline_forward_difference(cx, cy, cz, False)

        # T
        for line in range(repetitions):
            for column in range(repetitions):
                gx = self.__b_spline_geometric_matrix(user_coordinates, 0, line, column, lines_columns_qtt)
                cx = m.dot(gx).dot(m.transpose())

                gy = self.__b_spline_geometric_matrix(user_coordinates, 1, line, column, lines_columns_qtt)
                cy = m.dot(gy).dot(m.transpose())

                gz = self.__b_spline_geometric_matrix(user_coordinates, 2, line, column, lines_columns_qtt)
                cz = m.dot(gz).dot(m.transpose())

                coordinates += self.__b_spline_forward_difference(cx, cy, cz, True)

        return coordinates

    def __lines_columns_qtt(self, array_len: int):
        i = 1

        # i <= 5: max matrix size is 20x20
        # So, (4 * 5) ** 2 = 400 = 20 * 20
        while ((4 * i) ** 2 != array_len and i <= 5):
            i += 1

        return (4 * i)

    def __b_spline_geometric_matrix(self, user_coordinates: list, type: int, line: int, column: int, lines_columns_qtt: int):
        tmp = []

        for coord in user_coordinates:
            tmp.append(coord[type])

        # 4x4 
        g = np.identity(4)

        for i in range(0, 4):
            pos = (i * (line + 1)) * lines_columns_qtt  + column
            for j in range(4):
                g[i][j] = tmp[pos + j]

        return g


    def __b_spline_forward_difference(self, cx, cy, cz, is_t: bool):
        E_s = self.__b_spline_initial_condition(self.__step)
        E_t = self.__b_spline_initial_condition(self.__step)

        DD_x = E_s.dot(cx).dot(E_t.transpose())
        DD_y = E_s.dot(cy).dot(E_t.transpose())
        DD_z = E_s.dot(cz).dot(E_t.transpose())

        if is_t:
            DD_x = DD_x.transpose()
            DD_y = DD_y.transpose()
            DD_z = DD_z.transpose()

        coordinates = []

        n = 1
        for i in range(int(n / self.__step)):
            coordinates += self.__forward_diferences(n, DD_x, DD_y, DD_z)

            DD_x = self.__b_spline_update_dd(DD_x)
            DD_y = self.__b_spline_update_dd(DD_y)
            DD_z = self.__b_spline_update_dd(DD_z)

        return coordinates

    
    def __b_spline_update_dd(self, DD_):
        DD = deepcopy(DD_)
        for i in range(0, len(DD) - 1):
            for j in range(len(DD)):
                DD[i][j] += DD[i+1][j]

        return DD

    def __b_spline_initial_condition(self, delta: float):
        delta2 = delta * delta 
        delta3 = delta2 * delta
        
        E = np.array([
            [0         , 0         , 0    , 1],
            [delta3    , delta2    , delta, 0],
            [6 * delta3, 2 * delta2, 0    , 0],
            [6 * delta3, 0         , 0    , 0]
        ])

        return E

    def __forward_diferences(self, n, DD_x, DD_y, DD_z) -> list:

        x = DD_x[0][0]
        y = DD_y[0][0]
        z = DD_z[0][0]

        de1 = [DD_x[0][1], DD_y[0][1], DD_z[0][1]]
        de2 = [DD_x[0][2], DD_y[0][2], DD_z[0][2]]
        de3 = [DD_x[0][3], DD_y[0][3], DD_z[0][3]]

        i = 0

        coordinates = []

        while i < n:
            i += self.__step
            
            x += de1[0]
            de1[0] += de2[0]
            de2[0] += de3[0]
            
            y += de1[1]
            de1[1] += de2[1]
            de2[1] += de3[1]
            
            z += de1[2]
            de1[2] += de2[2]
            de2[2] += de3[2]

            coordinates.append((float(x), float(y), float(z)))

        return coordinates


