from model.bicubic_surface_3D import Bicubic_Surface_3D
from model.object import Object
from model.object_3D import Object_3D
from model.point_3D import Point_3D
from model.window import Window
from model.wireframe import Wireframe
from model.line import Line
from model.point import Point

from math import sqrt

class DescriptorOBJ:
    
    def __init__(self, root: str) -> None:
        self.__root = root
        self.__triangle_step = 0.01
        self.__rgb_max = 255
        self.__transparency = 0.5
    
    def save(self, file_name: str, objects: list, window: Window) -> None:
        count = 1

        part1, part2, count = window.obj_string(count)

        mtl = ""
        for obj in objects:
            part1_, part2_, mtl_, count = obj.obj_string(count)
            part1 += part1_
            part2 += f"{part2_}\n" 
            mtl += f"{mtl_}\n"

        part1 += f"mtllib {file_name}.mtl\n\n"
        self.__write_obj(file_name, part1 + part2)
        self.__write_mtl(file_name, mtl)

    def __write_obj(self, file_name: str, content: str) -> None:
        file = open(f"{self.__root}/{file_name}.obj", 'w+')
        file.write(content)
        file.close()
    
    def __write_mtl(self, file_name: str, content: str) -> None:
        file = open(f"{self.__root}/{file_name}.mtl", 'w+')
        file.write(content)
        file.close()
    
    def read(self, file_name: str) -> dict:
        file = open(f"{self.__root}/{file_name}.obj", 'r+')
        colors = {} 
        objects = []
        vertices = []
        name = ""
        window_center = None

        window = None
        color = ""

        for line in file.readlines():
            data = line.split()
            if (len(line) > 1 and data[0] != "#"): # empty line
                if data[0] == "v": #or data[0] == "vt" or data[0] == "vn":
                    vertice = data[1:]
                    if len(vertice) == 2:
                        vertices.append((float(vertice[0]), float(vertice[1])))
                    else:
                        vertices.append((float(vertice[0]), float(vertice[1]), float(vertice[2])))
                elif data[0] == "mtllib":
                    colors = self.__read_mtl(data[1])
                elif data[0] == "g" or data[0] == "o":
                    if len(data) > 1:
                        name = data[1:]
                    else:
                        name = ""
                elif data[0] == "s":
                    pass
                elif data[0] == "f":
                    vertices_2D = []
                    
                    for i in data[1:]:
                        pos = i.split("/")[0]
                        pos = int(pos) - 1 # pos 1 .. N
                        vertice = vertices[pos]
                        if vertice[2] == 0:
                            vertices_2D.append(vertice)
                        else:
                            vertices_2D = []
                            break

                    object = Object_3D()
                    coordinates = []
                    if len(vertices_2D) > 0:
                        object = Wireframe()
                        coordinates = vertices_2D

                        if (len(coordinates) == 3):
                            object.subtype = "Triangle"

                            object.subcolor = object.color_hex([(self.__rgb_max - colors[color][0]) * self.__transparency,
                                (self.__rgb_max - colors[color][1]) * self.__transparency,
                                (self.__rgb_max - colors[color][2]) * self.__transparency])

                            coordinates = self.__fill_triangle(coordinates)
                    else:
                        for i in data[1:]:
                            pos = i.split("/")[0]
                            pos = int(pos) - 1 # pos 1 .. N

                            coordinates.append(vertices[pos])

                    object.color = object.color_hex(colors[color])
                    object.coordinates = coordinates
                    object.name = name
                    objects.append(object)
                elif data[0] == "p":
                    coord = int(data[1])
                    coordinate = vertices[coord - 1]
                    object = Point_3D()

                    if coordinate[2] == 0:
                        object = Point()
                        object.coordinates = [(float(coordinate[0]), float(coordinate[1]))]
                    else:
                        object.coordinates = [(float(coordinate[0]), float(coordinate[1]), float(coordinate[2]))]

                    object.name = name
                    object.color = color
                elif data[0] == "l":
                    object = None
                    
                    is_3D = False
                    vertices_2D = []
                    vertices_3D = []

                    for i in data[1:]:
                        pos = int(i)
                        coord = vertices[pos - 1]
                        vertices_2D.append((float(coord[0]), float(coord[1])))
                        vertices_3D.append((float(coord[0]), float(coord[1]), float(coord[2])))

                        if coord[2] != 0:
                            is_3D = True

                    if len(vertices_2D) > 2:
                        if is_3D:
                            object = Object_3D()
                        else:
                            object = Wireframe()

                        object.coordinates = vertices_3D
                    else:
                        object = Line()
                        object.coordinates = vertices_2D 

                    object.name = name
                    object.color = object.color_hex(colors[color])
                    objects.append(object)
                elif data[0] == "surf": # Bicubic surface
                    object = Bicubic_Surface_3D()
                    coordinates = []
                    
                    for i in data[1:]:
                        pos = int(i)
                        coord = vertices[pos - 1]
                        coordinates.append((float(coord[0]), float(coord[1]), float(coord[2])))

                    object.name = name
                    object.subtype = "file"
                    object.coordinates = coordinates
                    object.color = object.color_hex(colors[color])
                    objects.append(object)

                elif data[0] == "usemtl":
                    color = data[1]
                elif data[0] == "w": # window
                    window = Window()

                    center = vertices[int(data[1]) - 1]
                    size = vertices[int(data[2]) - 1]   # 2D

                    VPN = vertices[int(data[3]) - 1]
                    
                    # window_center = (center[0] - Asize[0], center[1] - center[0], 0)
                    window_center = (0, 0, 0)

                    # window_center = (-50, 0, 0)

                    window.xwMin = 0
                    window.xwMax = float(size[0])
                    window.ywMin = 0
                    window.ywMax = float(size[1])
                    window.n = float(size[2])
                    window.VPN = VPN
                   
        return {"window": window, "objects": objects, "window_center": window_center}

    def __read_mtl(self, mtl_file: str) -> dict:
        file = open(f"{self.__root}/{mtl_file}", "r+") 

        colors = {}
        key = ""
        
        for line in file.readlines():
            if len(line) > 1:
                data = line.split()
                if data[0] == "newmtl":
                    key = data[1]
                if data[0] == "Kd":
                    colors[key] = tuple(map(float, data[1:]))

        return colors

    def __mount_object(self, obj: Object, name: str, color: tuple, vertices: list, positions: list) -> Object:
        coordinates = ""
        for p in positions:
            coordinates += str(vertices[p - 1]) + "," # First element 1
        coordinates = coordinates[:-1]

        obj.coordinates = str(coordinates)
        obj.name = name
        obj.color = obj.color_hex(color)

        return obj

    def __fill_triangle(self, coordinates: list) -> list:
        x1 = coordinates[0][0]
        y1 = coordinates[0][1]

        x2 = coordinates[1][0]
        y2 = coordinates[1][1]

        x3 = coordinates[2][0]
        y3 = coordinates[2][1]

        # Get length of all sides
        d1 = sqrt(((y2-y1)**2)+((x2-x1)**2))
        d2 = sqrt(((y3-y2)**2)+((x3-x2)**2))
        d3 = sqrt(((y1-y3)**2)+((x1-x3)**2))

        tx ,ty, vx, vy, d = self.__get_shortest(d1, d2, d3, x1, x2, x3, y1, y2, y3)

        coordinates = []
        count = 0
        while(count < d):
            coordinates.append((x3,y3))
            coordinates.append((tx,ty))
            coordinates.append((x3,y3))

            tx = tx + vx * self.__triangle_step
            ty = ty + vy * self.__triangle_step
            count = count + self.__triangle_step
        
        return coordinates

    def __get_shortest(self, d1: float, d2: float, d3: float
        , x1: float, x2: float, x3: float, y1: float, y2: float, y3: float) -> list:

        if ((d1 < d2) or (d1 == d2)) and ((d1 < d2) or( d1 == d2)): # The first side is the shortest
            tx = x1
            ty = y1
            vx = (x2-x1)/d1
            vy = (y2-y1)/d1
            d = d1
        elif ( d2 < d3) or (d2 == d3): # The second side is the shortest
            tx = x2
            ty = y2
            vx = (x3-x2)/d2
            vy = (y3-y2)/d2
            d = d2
        else: # The third side is shortest
            tx = x3
            ty = y3
            vx = (x1-x3)/d3
            vy = (y1-y3)/d3
            d = d3

        return [tx, ty, vx, vy, d]
