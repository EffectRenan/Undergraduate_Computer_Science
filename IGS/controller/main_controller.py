from model.bicubic_surface_3D import Bicubic_Surface_3D
from model.point_3D import Point_3D
from typing import Generic
from model.curve import Curve
from model.object_3D import Object_3D 
from model.wireframe import Wireframe
from controller.transformation_controller import TransformationController
from view.main_view import MainView
from controller.create_controller import CreateController
from model.object import Object
from model.point import Point
from model.window import Window
from model.descriptor_obj import DescriptorOBJ

from tkinter import Tk
from os import listdir
import copy

class MainController:

    def __init__(self) -> None:
        self.__display_file = {
            "objects": [],
            "normalized_objects": []
        }

        self.__dimension = 2

        root = Tk()
        
        monitor_height = root.winfo_screenheight()
        monitor_width = root.winfo_screenwidth()

        self.__viewport = {
            "xvpMin": 20,
            "yvpMin": 20,
            "xvpMax": monitor_width * 0.75,
            "yvpMax": monitor_height * 0.75,
        }
        
        self.__click_handlers = {
            "create_object": self.__create_object_handler,
            "navigation_in": self.__navigation_in_handler,
            "navigation_out": self.__navigation_out_handler,
            "navigation_up": self.__navigation_up_handler,
            "navigation_down": self.__navigation_down_handler,
            "navigation_left": self.__navigation_left_handler,
            "navigation_right": self.__navigation_right_handler,
            "navigation_camera_in": self.__navigation_camera_in_handler,
            "navigation_camera_out": self.__navigation_camera_out_handler,
            "navigation_camera_up": self.__navigation_camera_up_handler,
            "navigation_camera_down": self.__navigation_camera_down_handler,
            "navigation_camera_left": self.__navigation_camera_left_handler,
            "navigation_camera_right": self.__navigation_camera_right_handler,
            "navigation_rotation_rx": self.__navigation_rotation_rx_handler,
            "navigation_rotation_ry": self.__navigation_rotation_ry_handler,
            "navigation_rotation_rz": self.__navigation_rotation_rz_handler,
            "transformation_handler": self.__transformation_handler,
            "file_load": self.__file_load_handler,
            "file_save": self.__file_save_handler
        }
        
        self.__window = Window()
         
        self.__normalized_window = {
            "xwMin": self.__window.xwMin_normalized,
            "ywMin": self.__window.ywMin_normalized,
            "xwMax": self.__window.xwMax_normalized,
            "ywMax": self.__window.ywMax_normalized
        }

        self.__root_directory = "wavefront_objects"
        self.__descriptor = DescriptorOBJ(self.__root_directory)

        self.__transformations = ["Rotation", "Translation", "Scaling"] 

        self.__main_view = MainView(self.__viewport, root, self.__dimension, self.__root_directory)
        self.__create_controller = CreateController(self.__dimension)

        self.__select_options = [
            "Center of the selected object", 
            "Origin of the coordinate system", 
            "Arbitrary point"
        ]
        
        self.__select_options_3D = [
            "Rx", 
            "Ry", 
            "Rz", 
            "About an arbitrary axis"
        ]

        self.__transformation_controller = None
        self.__step_camera = 10

    def start(self) -> None:
        self.__update_boundary()
        self.__main_view.start_view(self.__click_handlers, self.__get_available_files())

    def __handle_coordinates_3D(self, object: Object_3D, VRP: tuple) -> None:

        # According to VRP, the coordinate (0, 0, 0) is 
        # pointed to the center of the window. 
        # So, it's needed to discount the VRP to match
        # the coordinate (0, 0, 0) to the actual (0, 0, 0).

        new_coords = []
        for coord in object.coordinates:
            new_coords.append(
                (coord[0] - VRP[0], coord[1] - VRP[1], coord[2] - VRP[2])
            )

        return new_coords 

    def __create_object_handler(self) -> None:
        object = self.__create_controller.start()

        if object != None:
            VRP  = self.__window.VRP()

            if self.__is_3D(object):
                object.coordinates = self.__handle_coordinates_3D(object, VRP)

            self.__display_file["objects"].append(object)
            self.__main_view.list_update(object)

            if self.__is_3D(object):
                object.rotate_r(self.__window.degree_rx, VRP, 0)
                object.rotate_r(self.__window.degree_ry, VRP, 1)
                object.rotate_r(self.__window.degree_rz, VRP, 2)

                object = self.__window.parallel_projection(object)
                # object = self.__window.perspective_projection(object)

            normalized_object = self.__window.normalize_object(object)
            clipped_object = self.__clipping(normalized_object)
            self.__display_file["normalized_objects"].append(clipped_object)

            if clipped_object.coordinates != None:
                self.__update_canvas(normalized_object)

    def __clipping(self, object) -> Object:
        new_object = copy.deepcopy(object)
        x = (self.__window.xwMin_normalized, self.__window.xwMax_normalized)
        y = (self.__window.ywMin_normalized, self.__window.ywMax_normalized)
        new_object.clipping([x, y])
        return new_object

    def __update_canvas(self, user_object: Object) -> None:

        all  = user_object.view_transform(self.__normalized_window, self.__viewport)

        if user_object.type == "Point":
            self.__main_view.update_canvas_point(all * 2, user_object.color)
        elif isinstance(user_object, Wireframe) and user_object.subtype != "": 
            triangle = all[:4]
            fill = all[4:]
            self.__main_view.update_canvas_line(triangle, user_object.color)
            self.__main_view.update_canvas_line(fill, user_object.subcolor)
        elif isinstance(user_object, Curve) and user_object.from_bucubic_surface == True:
            # 4 = a curve needs 4 points
            # 10 = blendding function = 1 / 0.1
            # 2 = (x, y)

            qtt = 4 * 10 * 2

            for i in range(0, len(all), qtt):
                curve = [all[i + j] for j in range(qtt)]

                self.__main_view.update_canvas_line(curve, user_object.color)
        else:
            self.__main_view.update_canvas_line(all, user_object.color)

    def __navigation_in_handler(self) -> None:
        self.__window.navigation_in()
        self.__window_restart()

    def __navigation_out_handler(self) -> None:
        self.__window.navigation_out()
        self.__window_restart()

    def __navigation_up_handler(self) -> None:
        self.__window.navigation_up()
        self.__window_restart()
        
    def __navigation_down_handler(self) -> None:
        self.__window.navigation_down()
        self.__window_restart()
    
    def __navigation_left_handler(self) -> None:
        self.__window.navigation_left()
        self.__window_restart()
    
    def __navigation_right_handler(self) -> None:
        self.__window.navigation_right()
        self.__window_restart()
    
    def __navigation_camera_in_handler(self) -> None:
        self.__window.degree_rz += self.__step_camera
        self.__window_restart()

    def __navigation_camera_out_handler(self) -> None:
        self.__window.degree_rz -= self.__step_camera
        self.__window_restart()

    def __navigation_camera_up_handler(self) -> None:
        self.__window.degree_rx -= self.__step_camera
        self.__window_restart()
        
    def __navigation_camera_down_handler(self) -> None:
        self.__window.degree_rx += self.__step_camera
        self.__window_restart()
    
    def __navigation_camera_left_handler(self) -> None:
        self.__window.degree_ry -= self.__step_camera
        self.__window_restart()
    
    def __navigation_camera_right_handler(self) -> None:
        self.__window.degree_ry += self.__step_camera
        self.__window_restart()

    def __navigation_rotation_rx_handler(self, degree: str) -> None:
        if degree != "":
            self.__window.degree_rx += float(degree)
        else:
            self.__window.degree_rx += 10

        self.__window_restart()

    def __navigation_rotation_ry_handler(self, degree: str) -> None:
        if degree != "":
            self.__window.degree_ry += float(degree)
        else:
            self.__window.degree_ry += 10 

        self.__window_restart()
    
    def __navigation_rotation_rz_handler(self, degree: str) -> None:
        if degree != "":
            self.__window.degree_rz += float(degree)
        else:
            self.__window.degree_rz += 10

        self.__window_restart()
    
    def __transformation_handler(self, selected_object: str) -> None:
        if selected_object != None:
            base_object = self.__display_file["objects"][int(selected_object)]
            is_3D = self.__is_3D(base_object)
            if is_3D:
                self.__transformation_controller = TransformationController(
                    self.__dimension, self.__transformations, self.__select_options_3D)
            
                user_content = self.__transformation_controller.start(is_3D)
                if user_content["type"] == self.__transformations[0]:
                    self.__rotation_handler_3D(user_content, selected_object)
                elif user_content["type"] == self.__transformations[1]:
                    self.__translation_handler_3D(user_content, selected_object)
                else:
                    self.__scaling_handler_3D(user_content, selected_object)
            else:
                self.__transformation_controller = TransformationController(
                    self.__dimension, self.__transformations, self.__select_options)
                
                user_content = self.__transformation_controller.start(is_3D)
                if user_content["type"] == self.__transformations[0]:
                    self.__rotation_handler(user_content, selected_object)
                elif user_content["type"] == self.__transformations[1]:
                    self.__translation_handler(user_content, selected_object)
                else:
                    self.__scaling_handler(user_content, selected_object)

            self.__window_restart()
        else:
            self.__main_view.print_msg("An object has not been selected.")
   
    def __rotation_handler(self, user_content: dict, selected_object: str) -> None:
        angle = float(user_content["entries"][0])

        base_object = self.__display_file["objects"][int(selected_object)]
        if user_content["option"] == self.__select_options[0]:
            base_object.rotate(angle, base_object.get_center())
        elif user_content["option"] == self.__select_options[1]:
            base_object.rotate(angle, (0,0))
        else:
            target = Point()
            target.coordinates = user_content["entries"][1]
            base_object.rotate(angle, target.coordinates[0])

    def __translation_handler(self, user_content: dict, selected_object: str) -> None:
        base_object = self.__display_file["objects"][int(selected_object)]
        point = Point()
        point.coordinates = user_content["entries"][0]
        base_object.translate(point.coordinates[0])

    def __scaling_handler(self, user_content: dict, selected_object: str) -> None:
        base_object = self.__display_file["objects"][int(selected_object)]
        point = Point()
        point.coordinates = user_content["entries"][0]
        base_object.scale(point.coordinates[0])
    
    def __rotation_handler_3D(self, user_content: dict, selected_object: str) -> None:
        angle = float(user_content["entries"][0])
        base_object = self.__display_file["objects"][int(selected_object)]

        if user_content["option"] == self.__select_options_3D[0]:
            base_object.rotate_r(angle, (0, 0, 0), 0) # Rx
        elif user_content["option"] == self.__select_options_3D[1]:
            base_object.rotate_r(angle, (0, 0, 0), 1) # Ry
        elif user_content["option"] == self.__select_options_3D[2]:
            base_object.rotate_r(angle, (0, 0, 0), 2) # Rz
        else: # Arbitrary axis
            target = Object_3D()
            target.coordinates = user_content["entries"][1]
            base_object.rotate(angle, target.coordinates)

    def __translation_handler_3D(self, user_content: dict, selected_object: str) -> None:
        base_object = self.__display_file["objects"][int(selected_object)]
        object = Point_3D() 
        object.coordinates = user_content["entries"][0]
        base_object.translate(object.coordinates[0])
    
    def __scaling_handler_3D(self, user_content: dict, selected_object: str) -> None:
        base_object = self.__display_file["objects"][int(selected_object)]
        object = Point_3D() 
        object.coordinates = user_content["entries"][0]
        base_object.scale(object.coordinates[0])

    def __file_load_handler(self, file_name: str) -> None:
        self.__display_file["objects"] = []
        
        result = self.__descriptor.read(file_name)
        
        for obj in result["objects"]:
            self.__display_file["objects"].append(obj)

        if result["window"] != None:
            self.__window = result["window"]
            center = result["window_center"]
            for obj in self.__display_file["objects"]:
                if self.__is_3D:
                    obj.translate((center[0], center[1], center[2]))
                else:
                    obj.translate((center[0], center[1]))
        else:
            self.__window = Window()

        self.__window_restart()
    
    def __file_save_handler(self, file_name: str) -> None:
        self.__descriptor.save(file_name, self.__display_file["objects"], self.__window)
        self.__main_view.file_list_update(self.__get_available_files())
        self.__main_view.print_msg("Saved!")

    def __window_restart(self) -> None:
        self.__main_view.clean()
        self.__update_boundary()

        self.__display_file["normalized_objects"] = []
        self.__window.update_normalizing_matrix()

        for obj in self.__display_file["objects"]:
            _obj = copy.deepcopy(obj)

            if self.__is_3D(_obj):
                VRP = self.__window.VRP()
                _obj.rotate_r(self.__window.degree_rx, VRP, 0)
                _obj.rotate_r(self.__window.degree_ry, VRP, 1)

                # Rz rotation is handled by 2D
                # _obj.rotate_r(self.__window.degree_rz, VRP, 2)
                _obj.translate(self.__window.translation_value)

                _obj = self.__window.parallel_projection(_obj);
                # _obj = self.__window.perspective_projection(_obj)

            normalized_object = self.__window.normalize_object(_obj)
            clipped_object = self.__clipping(normalized_object)
            self.__display_file["normalized_objects"].append(clipped_object)
            
            if clipped_object.coordinates != None:
                self.__update_canvas(clipped_object)

            self.__main_view.list_update(obj)

    def __update_boundary(self) -> None:
        # Save degree value.
        # Border should not rotate.
        degree = self.__window.degree_rz
        self.__window.degree_rz = 0
        self.__window.update_normalizing_matrix()
        
        coordinates = [
            (self.__window.xwMin, self.__window.ywMin),
            (self.__window.xwMin, self.__window.ywMax),
            (self.__window.xwMax, self.__window.ywMax),
            (self.__window.xwMax, self.__window.ywMin)
        ]
        
        boundary = Wireframe()
        boundary.coordinates = str(coordinates)
        boundary.color = "#FF0000"

        boundary = self.__window.normalize_object(boundary)
        self.__update_canvas(boundary)

        # Rocover degree value.
        self.__window.degree_rz = degree
        self.__window.update_normalizing_matrix()

    def __get_available_files(self) -> list:
        files = listdir(self.__root_directory)
        names = []
        for file in files:
            name = file.split('.')
            if name[1] == "obj":
                names.append(name[0])
        
        return names

    def __is_3D(self, object) -> bool:
        return len(object.type.split("3D")) > 1

