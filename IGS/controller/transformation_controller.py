from view.transformation_view import TransformationView

class TransformationController:
    
    def __init__(self, dimension: int, transformations: list, select_options: list) -> None:
        self.__transformation_view = TransformationView(self.__transformation_object_handler, 
            dimension, select_options)

        self.__transformations = transformations
        self.__user_content = None

    def start(self, is_3D: bool) -> dict:
        try:
            self.__user_content = None
            self.__transformation_view.start_view(self.__transformations, is_3D)
        except Exception as error:
            self.__transformation_view.print_error(error)
        finally:
            return self.__user_content

    def __transformation_object_handler(self, user_content: dict) -> None:
        self.__user_content = user_content 
