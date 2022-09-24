from tkinter import LabelFrame
from tkinter import Toplevel
from tkinter import ttk
from tkinter import Frame
from tkinter import Label
from tkinter import Button
from tkinter import Entry
from tkinter import colorchooser 
from tkinter import StringVar 
from typing import Callable

class CreateView:
    
    def __init__(self, create_object_handler: Callable, dimension: int) -> None:
        self.__create_object_handler = create_object_handler
        self.__dimension = dimension
        self.__create = None 
        self.__entry = None
        self.__tab_control = None
        self.__frames = {}
        self.__font = ("Calibri 10")
        self.__object_color = None
        self.__curve_type = StringVar()

    def start_view(self, types: dict) -> None:
        self.__create = Toplevel()

        self.__create.title("Create")
        self.__tab_control = ttk.Notebook(self.__create)
        self.__prepare_tabs(types)
        self.__prepare_elements()

        self.__create.attributes('-type', 'dialog')
        self.__create.mainloop()

    def __prepare_tabs(self, types: dict) -> None:
        for i in range(len(types)):
            tab = Frame(self.__tab_control, pady=5, padx=10)
            self.__frames[types[i]] = tab

            self.__tab_control.add(tab, text = types[i])
            
            if types[i] == "Point":
                self.__handle_point(tab)
            elif types[i] == "Point_3D":
                self.__handle_point_3D(tab)
            elif types[i] == "Object_3D":
                self.__handle_object_3D(tab)
            elif types[i] == "Bicubic_Surface_3D":
                self.__handle_bicubic_surface_3D(tab)
            elif types[i] == "Line":
                self.__handle_line(tab)
            elif types[i] == "Curve":
                self.__handle_curve(tab)
            else:
                self.__handle_wireframe(tab)

        self.__tab_control.pack(expand = 1, fill ="both")

    def __handle_point(self, tab: Frame) -> None:
        text = "Format: (x0, y0)"

        Label(tab, text = text, font=self.__font).pack(pady=5)
        Entry(tab, width=30, font=self.__font).pack(pady=5)
    
    def __handle_point_3D(self, tab: Frame) -> None:
        text = "Format: (x0, y0, z0)"

        Label(tab, text = text, font=self.__font).pack(pady=5)
        Entry(tab, width=30, font=self.__font).pack(pady=5)
    
    def __handle_object_3D(self, tab: Frame) -> None:
        text = "Format: (x0, y0, z0),(x1,y1,z1),..."

        Label(tab, text = text, font=self.__font).pack(pady=5)
        Entry(tab, width=30, font=self.__font).pack(pady=5)

    def __handle_line(self, tab: Frame) -> None:
        text = "Note: A line requires 2 points.\nFormat: (x0, y0),(x1, y1)"

        Label(tab, text = text, font=self.__font).pack(pady=5)
        Entry(tab, width=30, font=self.__font).pack(pady=5)

    def __handle_wireframe(self, tab: Frame) -> None:
        text = "Note: It is required 2 points at least.\nFormat: (x0, y0),(x1, y1), ..."

        Label(tab, text = text, font=self.__font).pack(pady=5)
        Entry(tab, width=30, font=self.__font).pack(pady=5)
    
    def __handle_curve(self, tab: Frame) -> None:
        text = "Note: It is required 4 points at least.\nFormat: P1, Q1, P4, P4, ..., Pi, Qi"
        
        Label(tab, text = text, font=self.__font).pack(pady=5)
        choices = ["Hermite", "B-Spline"]

        #self.__curve_type.set(choices[0])
        ttk.Combobox(tab, values = choices, textvariable=self.__curve_type, font=self.__font).pack(pady=5)

        Entry(tab, width=30, font=self.__font).pack(pady=5)
        
    def __handle_bicubic_surface_3D(self, tab: Frame) -> None:
        text = "Format: (x0, y0, z0),(x1,y1,z1),...\n\
        Group of 16 points each."

        Label(tab, text = text, font=self.__font).pack(pady=5)
        
        choices = ["Bezier", "B-Spline"]
        #self.__curve_type.set(choices[0])
        ttk.Combobox(tab, values = choices, textvariable=self.__curve_type, font=self.__font).pack(pady=5)

        Entry(tab, width=30, font=self.__font).pack(pady=5)

    def __prepare_elements(self) -> None:
        
        def color() -> None:
            color = colorchooser.askcolor()
            self.__object_color = color[1]

        frame = LabelFrame(self.__create)
        frame.pack(pady=10)

        Label(frame, text="Name:", font=self.__font).grid(pady=5, row=0, column=0)
        
        self.__entry = Entry(frame, width=15, font=self.__font)
        self.__entry.grid(pady=5, padx=10, row=0, column=1)

        Button(frame, text="Set a color", font=self.__font, fg="blue",
            command=color).grid(pady=5, padx=10, row=1, column=0)
        
        self.__object_color = None

        Button(frame, text="Create", font=self.__font, fg="blue",
            command=self.__create_click_event).grid(pady=5, row=1, column=1)

    def print_error(self, error: Exception) -> None:
        print(error)

    def __create_click_event(self) -> None:
        try:
            selected_index = self.__tab_control.index("current")
            selected_type = self.__tab_control.tab(selected_index, 'text')
            children_widgets = self.__frames[selected_type].winfo_children()
            
            user_content = {
                "name": self.__entry.get(),
                "type": selected_type,
                "color": self.__object_color,
                "curve_type": self.__curve_type.get(),
                "string_coordinates": "",
            }

            for child_widget in children_widgets:
                if child_widget.winfo_class() == "Entry":
                    user_content["string_coordinates"] = child_widget.get()
                    break

            print(user_content)
            self.__create_object_handler(user_content)

        except Exception as error:
            print(error)
        finally:
            self.__create.quit()
            self.__create.destroy()
