from model.bicubic_surface_3D import Bicubic_Surface_3D
from model.object_3D import Object_3D
from model.point_3D import Point_3D
from model.curve import Curve
from model.point import Point
from model.line import Line
from model.wireframe import Wireframe
from model.object import Object
from view.create_view import CreateView

class CreateController:
    
    def __init__(self, dimension: int) -> None:
        self.__create_view = CreateView(self.__create_object_handler, dimension)
        self.__user_content = None

    def start(self) -> Object:
        objects = [Point_3D(), Object_3D(), Bicubic_Surface_3D(), Point(), Line(), Wireframe(), Curve()]
        self.__create_view.start_view([obj.type for obj in objects])

        if self.__user_content != None:
            user_content = self.__user_content
            self.__user_content = None
            return self.__handle_user_content(user_content, objects)
        else:
            return None

    def __handle_user_content(self, user_content: dict, objects: dict) -> Object:
        try:
            object = [obj for obj in objects if obj.type == user_content["type"]][0]
            object.name = user_content["name"]
            
            if object.type == "Curve" or object.type == "Bicubic_Surface_3D":
                object.subtype = user_content["curve_type"]

            object.coordinates = user_content["string_coordinates"]

            if user_content["color"] != None:
                object.color = user_content["color"]

            return object
        except Exception as error:
            self.__create_view.print_error(error)
            return None

    def __create_object_handler(self, user_content: dict) -> None:
        self.__user_content = user_content 
