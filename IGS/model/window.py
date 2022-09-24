from model.curve import Curve
from model.point import Point
from model.object_3D import Object_3D
from model.wireframe import Wireframe
from model.interface_3D import Interface_3D
from model.object import Object
import copy
import numpy as np

class Window:

    def __init__(self) -> None:

        self.__xwMin = 0
        self.__ywMin = 0
        self.__xwMax = 250
        self.__ywMax = 250
        self.__n = 250

        self.__xwMin_normalized = -1
        self.__ywMin_normalized = -1
        self.__xwMax_normalized = 1
        self.__ywMax_normalized = 1

        self.__zoom_times = 1

        self.__degree_rx = 0
        self.__degree_ry = 0
        self.__degree_rz = 0

        self.__VPN = None
        self.__COP = None

        self.__translation_value = (0, 0, 0)

        self.__normalizing_matrix = None
        self.__object = Object("Generic")
        self.__interface_3D = Interface_3D("Generic")
        self.update_normalizing_matrix()

    @property
    def xwMin(self) -> int:
        return self.__xwMin
    
    @xwMin.setter
    def xwMin(self, xwMin) -> None:
        self.__xwMin = xwMin

    @property
    def ywMin(self) -> int:
        return self.__ywMin
    
    @ywMin.setter
    def ywMin(self, ywMin) -> None:
        self.__ywMin = ywMin
    
    @property
    def xwMax(self) -> int:
        return self.__xwMax
    
    @xwMax.setter
    def xwMax(self, xwMax) -> None:
        self.__xwMax = xwMax
    
    @property
    def ywMax(self) -> int:
        return self.__ywMax
    
    @ywMax.setter
    def ywMax(self, ywMax) -> None:
        self.__ywMax = ywMax

    @property
    def xwMin_normalized(self) -> int:
        return self.__xwMin_normalized
    
    @property
    def ywMin_normalized(self) -> int:
        return self.__ywMin_normalized
    
    @property
    def xwMax_normalized(self) -> int:
        return self.__xwMax_normalized
    
    @property
    def ywMax_normalized(self) -> int:
        return self.__ywMax_normalized

    @property
    def degree_rx(self) -> float:
        return self.__degree_rx
    
    @property
    def degree_ry(self) -> float:
        return self.__degree_ry
    
    @property
    def degree_rz(self) -> float:
        return self.__degree_rz

    @property
    def n(self) -> float:
        return self.__n
   
    @n.setter
    def n(self, n: float) -> None:
        self.__n = n
    
    @property
    def VPN(self) -> list:
        return self.__VPN
   
    @VPN.setter
    def VPN(self, vpn: list) -> None:
        self.__VPN = vpn
    
    @property
    def translation_value(self) -> float:
        return self.__translation_value

    @translation_value.setter
    def translation_value(self, v: tuple) -> float:
        a = self.__translation_value[0] + v[0]
        b = self.__translation_value[1] + v[1]
        c = self.__translation_value[2] + v[2]

        self.__translation_value = (a, b, c)

    @degree_rx.setter
    def degree_rx(self, degree) -> None:
        self.__degree_rx = degree
    
    @degree_ry.setter
    def degree_ry(self, degree) -> None:
        self.__degree_ry = degree
    
    @degree_rz.setter
    def degree_rz(self, degree) -> None:
        self.__degree_rz = degree

    def navigation_in(self) -> None:
        self.__xwMin += self.__zoom_times
        self.__ywMin += self.__zoom_times
        self.__xwMax -= self.__zoom_times
        self.__ywMax -= self.__zoom_times
    
    def navigation_out(self) -> None:
        self.__xwMin -= self.__zoom_times
        self.__ywMin -= self.__zoom_times
        self.__xwMax += self.__zoom_times
        self.__ywMax += self.__zoom_times

    def navigation_up(self) -> None:
        self.__ywMin -= 1
        self.__ywMax -= 1

    def navigation_down(self) -> None:
        self.__ywMin += 1
        self.__ywMax += 1

    def navigation_left(self) -> None:
        self.__xwMin += 1
        self.__xwMax += 1

    def navigation_right(self) -> None:
        self.__xwMin -= 1
        self.__xwMax -= 1
    
    def navigation_rotate_rx(self, degree: float) -> None:
        self.__degree_rx += degree
    
    def navigation_rotate_ry(self, degree: float) -> None:
        self.__degree_ry += degree
    
    def navigation_rotate_rz(self, degree: float) -> None:
        self.__degree_rz += degree
    
    def center(self) -> tuple:
        xw = (self.__xwMax - self.__xwMin) / 2
        yw = (self.__ywMax - self.__ywMin) / 2
        return (xw, yw)

    def VRP(self) -> tuple:
        # View Reference point

        xw = (self.__xwMax - self.__xwMin) / 2
        yw = (self.__ywMax - self.__ywMin) / 2
      
        # zw is the length of the VPN line segment
        VPN_x = (self.__VPN[1][0] - self.__VPN[0][0]) ** 2
        VPN_y = (self.__VPN[1][1] - self.__VPN[0][1]) ** 2
        VPN_z = (self.__VPN[1][2] - self.__VPN[0][2]) ** 2
        zw = (VPN_x + VPN_y + VPN_z) ** (1 / 2)

        return (xw, yw, zw)

    def parallel_projection(self, object: Object_3D) -> Object:
        # translate VRP to the origin
        VRP = self.VRP()
        
        t_matrix = self.__interface_3D.build_translation_matrix(VRP[0], VRP[1], VRP[2])

        teta = self.__interface_3D.rotation_degree_rx(self.__VPN[1])
        type = 0 # Rx
        rx_matrix = self.__interface_3D.build_rotation_matrix(teta, type)

        teta = self.__interface_3D.rotation_degree_ry(self.__VPN[1])
        type = 1 # Ry
        ry_matrix = self.__interface_3D.build_rotation_matrix(teta, type)

        t_m = self.__interface_3D.concat_matrix([t_matrix, rx_matrix, ry_matrix])
        coordinates = self.__interface_3D.transform(object.coordinates, t_m) 

        object_2D = Point()
        if self.__is_object(object):
            object_2D = Wireframe()
            object_2D.from_object_3D = True
        elif self.__is_surface(object):
            object_2D = Curve()
            object_2D.from_bucubic_surface = True

        new_coordinates = []

        # Ignore z
        for coord in coordinates:
            new_coordinates.append((coord[0], coord[1]))

        object_2D.coordinates = new_coordinates
        object_2D.name = object.name
        object_2D.color = object.color


        return object_2D

    def __build_perspective_matrix(self) -> None:
        matrix = np.identity(4)
        matrix[0][3] = 0
        matrix[0][2] = self.__perspective_distance()
        return matrix

    def __perspective_distance(self) -> tuple:
        COP_x = (self.__COP[1][0] - self.__COP[0][0]) ** 2
        COP_y = (self.__COP[1][1] - self.__COP[0][1]) ** 2
        COP_z = (self.__COP[1][2] - self.__COP[0][2]) ** 2
        return (COP_x + COP_y + COP_z) ** (1 / 2)
     
    def perspective_projection(self, object) -> Object:
        COP = self.__COP[0]
        
        t_matrix = self.__interface_3D.build_translation_matrix(COP[0], COP[1], COP[2])

        teta = self.__interface_3D.rotation_degree_rx(self.__VPN[1])
        type = 0 # Rx
        rx_matrix = self.__interface_3D.build_rotation_matrix(teta, type)

        teta = self.__interface_3D.rotation_degree_ry(self.__VPN[1])
        type = 1 # Ry
        ry_matrix = self.__interface_3D.build_rotation_matrix(teta, type)

        per_matrix = self.__build_perspective_matrix()

        t_m = self.__interface_3D.concat_matrix([t_matrix, rx_matrix, ry_matrix, per_matrix])
        coordinates = self.__interface_3D.transform(object.coordinates, t_m) 

        object_2D = Point()
        if self.__is_object(object):
            object_2D = Wireframe()
            object_2D.from_object_3D = True
        elif self.__is_surface(object):
            object_2D = Curve()
            object_2D.from_bucubic_surface = True

        new_coordinates = []

        # Ignore z
        for coord in coordinates:
            new_coordinates.append((coord[0], coord[1]))

        object_2D.coordinates = new_coordinates
        object_2D.name = object.name
        object_2D.color = object.color

        return object_2D       


    def __is_object(self, object) -> bool:
        return len(object.type.split("Object")) > 1
            
    
    def __is_surface(self, object) -> bool:
        return  len(object.type.split("Surface")) > 1


    def __VPN_COP_update(self) -> None:
        n = self.__n
        self.__VPN = [(n, n, n), (n / 4, n / 4, n)]

        self.__COP = [(self.__VPN[0][0], self.__VPN[0][1], n / 2), self.__VPN[1]]


    def __normalization_center(self) -> tuple:
        xw = (self.__xwMin + self.__xwMax) / 2
        yw = (self.__ywMin + self.__ywMax) / 2
        return (-xw, -yw)

    def __scale(self) -> tuple:
        center = self.center()
        return (1 / center[0], 1 / center[1])

    def update_normalizing_matrix(self) -> None:
        self.__VPN_COP_update()

        center = self.__normalization_center()
        scale = self.__scale()

        t_matrix = self.__object.build_translation_matrix(center[0], center[1])
        r_matrix = self.__object.build_rotation_matrix(self.__degree_rz)
        s_matrix = self.__object.build_scaling_matrix(scale[0], scale[1])
        self.__normalizing_matrix = self.__object.concat_matrix([t_matrix, r_matrix, s_matrix])

    def normalize_object(self, user_object: Object) -> Object:
        obj = copy.deepcopy(user_object)
        
        obj.coordinates = obj.transform(obj.coordinates, self.__normalizing_matrix)
        return obj

    def obj_string(self, count: int) -> list:
        center = self.VRP()
        part1 = f"v {center[0]} {center[1]} {center[2]}\n"

        part1 += f"v {self.__xwMax - self.__xwMin} {self.__ywMax - self.__ywMin} {self.__n}\n"
        part1 += f"v {self.__VPN[0][0] - self.__VPN[1][0]} {self.__VPN[0][1] - self.__VPN[1][1]} {self.__VPN[0][2] - self.__VPN[1][2]}\n"

        part2 = f"o window\n"
        part2 += f"w {count} {count + 1} {count + 2}\n"

        return [part1, part2, count + 3]
