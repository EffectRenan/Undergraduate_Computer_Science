from model.object import Object
import numpy as np

class Curve(Object):

    def __init__(self) -> None:
        super().__init__("Curve")
        self._mtl_prefix = "l"
        self.__subtype = ""
        self.__subcolor = ""
        self.__step = 0.01
        self.__from_bucubic_surface = False

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
    
    @property
    def from_bucubic_surface(self) -> None:
        return self.__from_bucubic_surface

    @from_bucubic_surface.setter
    def from_bucubic_surface(self, value: bool) -> None:
        self.__from_bucubic_surface = value

    def _check(self, coordinates: list) -> list:

        # Only fix the curve if the object is new.
        if len(coordinates) >= 4 or self.__from_bucubic_surface:
            return coordinates
        elif len(self.coordinates) == 0: 
            if self.__subtype == "Hermite":
                return self.__create_hermite(coordinates)
            else:
                return self.__create_b_spline(coordinates)
        else:
            return None

    def _parsing(self, coordinates: str) -> list:
        return list(self._string_to_tuple(coordinates))

    def clipping(self, window: list) -> None:
        # Clipping by point

        coordinates = []

        for coord in self.coordinates:
            if coord[0] > window[0][0] and coord[0] < window[0][1] \
                and coord[1] > window[1][0] and coord[1] < window[1][1]:

                coordinates.append(coord)

        self.coordinates = coordinates

    def __create_b_spline(self, user_coordinates: list) -> list:
        
        # Mbs
        m = np.array([
            [-1.0, 3.0, -3.0, 1.0], 
            [3.0, -6.0,  3.0, 0.0], 
            [-3.0, 0.0,  3.0, 0.0], 
            [1.0,  4.0,  1.0, 0.0]
        ])

        m *= 1 / 6

        p0 = user_coordinates[0]
        p1 = user_coordinates[1]
        p2 = user_coordinates[2]
        p3 = user_coordinates[3]

        coordinates = self.__b_spline(m, p0, p1, p2, p3)

        # More than 4 points
        for p in user_coordinates[4:]:
            p0 = p1
            p1 = p2
            p2 = p3
            p3 = p

            coordinates += self.__b_spline(m, p0, p1, p2, p3)

        return coordinates 

    def __b_spline(self, m: list, 
        p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> list:

        C = m.dot([
            p0,
            p1,
            p2,
            p3
        ])
       
        delta = self.__step
        n = 1

        D = self.__init_condition_fd(C, delta)
        return self.forward_diferences(n, D)

    def __init_condition_fd(self, C: list, delta: float) -> list:
        delta2 = delta * delta
        delta3 = delta2 * delta

        E = np.array([
            [0         , 0         , 0    , 1],
            [delta3    , delta2    , delta, 0],
            [6 * delta3, 2 * delta2, 0    , 0],
            [6 * delta3, 0         , 0    , 0],
        ])

        return E.dot(C)
    
    def forward_diferences(self, n: int, D: list) -> list:
        # 2D

        f = D[0]
        de1 = D[1]
        de2 = D[2]
        de3 = D[3]

        x = f[0]
        y = f[1]

        i = 0

        coordinates = [(x, y)]

        while i < n:
            i += self.__step
            
            x += de1[0]
            de1[0] += de2[0]
            de2[0] += de3[0]
            
            y += de1[1]
            de1[1] += de2[1]
            de2[1] += de3[1]
            
            # z += de1[2]
            # de1[2] += de2[2]
            # de2[2] += de3[2]

            coordinates.append((float(x), float(y)))

        return coordinates

    # A method for B-splines using blending function
    def __create_b_spline2(self, user_coordinates: list) -> list:
        m = np.array([
            [-1.0, 3.0, -3.0, 1.0], 
            [3.0, -6.0,  3.0, 0.0], 
            [-3.0, 0.0,  3.0, 0.0], 
            [1.0,  4.0,  1.0, 0.0]
        ])

        m *= 1 / 6

        p0 = user_coordinates[0]
        p1 = user_coordinates[1]
        p2 = user_coordinates[2]
        p3 = user_coordinates[3]

        coordinates = self.__all_b_spline_blended(m, p0, p1, p2, p3)

        # More than 4 points
        for p in user_coordinates[4:]:
            p0 = p1
            p1 = p2
            p2 = p3
            p3 = p

            coordinates += self.__all_b_spline_blended(m, p0, p1, p2, p3)

        return coordinates

    def __all_b_spline_blended(self, m: list, 
        p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> list:
        stop = 1
        count = 0
        coordinates = []

        while count <= stop:
            p = self.__b_spline_blending_function(m, count, p0, p1, p2, p3)
            coordinates.append(p)
            count += self.__step

        return coordinates

    def __b_spline_blending_function(self, m: list, i: int, 
        p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> tuple:

        t = np.array([i ** 3, i ** 2, i, 1])
        
        x = t.dot(m).dot(np.array([
            [p0[0]], 
            [p1[0]], 
            [p2[0]], 
            [p3[0]]
        ]))
        
        y = t.dot(m).dot(np.array([
            [p0[1]], 
            [p1[1]], 
            [p2[1]], 
            [p3[1]]
        ]))

        return (float(x), float(y))

    def __create_hermite(self, user_coordinates: list) -> list:

        # Base curve
        p1 = user_coordinates[0]
        r1 = user_coordinates[1]
        p4 = user_coordinates[2]
        r4 = user_coordinates[3]
        all = self.__create_hermite_points(p1, r1, p4, r4)

        others_coordinates = user_coordinates[4:]

        # Link more curves like p4, r4, p7, r7, ... 
        if len(others_coordinates) > 0:
            p_older = p4
            r_older = r4
            for i in range(0, len(others_coordinates), 2):
                p_new = others_coordinates[i]
                r_new = others_coordinates[i + 1] 

                all += self.__create_hermite_points(p_older, r_older, p_new, r_new)

                p_older = p_new
                r_older = r_new

        return all

    def __create_hermite_points(self, p1: tuple, r1: tuple, p4: tuple, r4: tuple) -> list:
        stop = 1
        count = 0
        coordinates = []

        while count <= stop:
            x = self.__hermite_blending_function(0, count, p1, p4, r1, r4)
            y = self.__hermite_blending_function(1, count, p1, p4, r1, r4)
            coordinates.append((x, y))
            count += self.__step

        return coordinates

    def __hermite_blending_function(self, coord: int, t: int, 
        p1: tuple, p4: tuple, r1: tuple, r4: tuple) ->  float:
        
        # Hermite curve

        return  p1[coord] * (2 * (t ** 3) - 3 * (t ** 2) + 1) + \
                p4[coord] * (-2 * (t ** 3) + 3 * (t ** 2)) + \
                r1[coord] * ((t ** 3) - 2 * (t ** 2) + t) + \
                r4[coord] * ((t ** 3) - (t ** 2))
