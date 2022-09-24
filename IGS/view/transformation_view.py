from tkinter import LabelFrame, Tk, Toplevel, font
from tkinter import ttk
from tkinter import Frame
from tkinter import Label
from tkinter import Button
from tkinter import Entry
from tkinter import IntVar
from tkinter import Radiobutton
from typing import Callable


class TransformationView:
    
    def __init__(self, top_level_handler: Callable, dimension: int, select_options: list) -> None:
        self.__top_level_object_handler = top_level_handler
        self.__dimension = dimension
        self.__top_level = None 
        self.__tab_control = None
        self.__frames = {}
        self.__font = ("Calibri 10")

        self.__selected_object = IntVar()
        self.__objects_frame = None

        self.__select_options = select_options
    def start_view(self, types: dict, is_3D: bool) -> None:
        self.__top_level = Toplevel()
        self.__top_level.title("Transformations")

        self.__tab_control = ttk.Notebook(self.__top_level)

        if is_3D:
            self.__prepare_tabs_3D(types)
        else:
            self.__prepare_tabs(types)

        self.__prepare_elements()
        self.__selected_object.set(0)

        self.__top_level.attributes('-type', 'dialog')
        self.__top_level.mainloop()

    def __prepare_tabs(self, types: dict) -> None:
        for i in range(len(types)):
            tab = Frame(self.__tab_control, pady=5, padx=5)
            self.__frames[types[i]] = tab

            self.__tab_control.add(tab, text = types[i])
            
            if types[i] == "Rotation":
                self.__handle_rotation(tab)
            elif types[i] == "Translation":
                self.__handle_translation(tab)
            else:
                self.__handle_scaling(tab)
    
    def __prepare_tabs_3D(self, types: dict) -> None:
        for i in range(len(types)):
            tab = Frame(self.__tab_control, pady=5, padx=5)
            self.__frames[types[i]] = tab

            self.__tab_control.add(tab, text = types[i])
            
            if types[i] == "Rotation":
                self.__handle_rotation_3D(tab)
            elif types[i] == "Translation":
                self.__handle_translation_3D(tab)
            else:
                self.__handle_scaling_3D(tab)

    def __handle_rotation(self, tab: Frame) -> None:
        angle = LabelFrame(tab, padx=5, pady=10)
        angle.grid(row=0, column=0)

        Label(angle, text = "Angle °:", font=self.__font).grid(row=0, column=0)

        Entry(angle, width=5, 
            font=self.__font).grid(row=0, column=1, padx=5)

        radio_frame = LabelFrame(tab, text="Around the:", padx=10, pady=10)
        radio_frame.grid(row=1, column=0, pady=5, padx=5)

        for i in range(len(self.__select_options)):
            Radiobutton(radio_frame, text=self.__select_options[i], 
                variable=self.__selected_object, value=i, command=self.__radio_click,
                font=self.__font).pack()

        self.__objects_frame = LabelFrame(tab, padx=0, pady=10)

        Label(self.__objects_frame, text = "Point (x, y):", 
            font=self.__font).grid(row=0, column=0, pady=5, padx=10)

        Entry(self.__objects_frame, width=5, font=self.__font).grid(row=0, column=1, padx=10)

    def __handle_rotation_3D(self, tab: Frame) -> None:
        angle = LabelFrame(tab, padx=5, pady=10)
        angle.grid(row=0, column=0)

        Label(angle, text = "Angle °:", font=self.__font).grid(row=0, column=0)

        Entry(angle, width=5, 
            font=self.__font).grid(row=0, column=1, padx=5)

        radio_frame = LabelFrame(tab, text="About the:", padx=10, pady=10)
        radio_frame.grid(row=1, column=0, pady=5, padx=5)

        for i in range(len(self.__select_options)):
            Radiobutton(radio_frame, text=self.__select_options[i], 
                variable=self.__selected_object, value=i, command=self.__radio_click,
                font=self.__font).pack()

        self.__objects_frame = LabelFrame(tab, padx=0, pady=10)

        Label(self.__objects_frame, text = "Axis: (x0, y0, z0),(x1, y1, z1)", 
            font=self.__font).grid(row=0, column=0, pady=5, padx=10)

        Entry(self.__objects_frame, width=15, font=self.__font).grid(row=0, column=1, padx=10)


    def __radio_click(self) -> None:
        selected = self.__select_options[self.__selected_object.get()]
        if selected == self.__select_options[3]:
            self.__objects_frame.grid(row=2, column=0)
        else:
            self.__objects_frame.grid_forget()


    def __handle_translation(self, tab: Frame) -> None:
        frame = LabelFrame(tab)
        frame.pack(pady=50)

        Label(frame, text = "Vector (Dx, Dy):", font=self.__font).grid(row=0, column=0)

        Entry(frame, width=10,
            font=self.__font).grid(row=0, column=1, padx=5, pady=5)
    
    def __handle_translation_3D(self, tab: Frame) -> None:
        frame = LabelFrame(tab)
        frame.pack(pady=50)

        Label(frame, text = "Vector (Dx, Dy, Dz):", font=self.__font).grid(row=0, column=0)

        Entry(frame, width=10,
            font=self.__font).grid(row=0, column=1, padx=5, pady=5)

    def __handle_scaling(self, tab: Frame) -> None:
        frame = LabelFrame(tab)
        frame.pack(pady=50)

        Label(frame, text = "Scale (Sx, Sy):", font=self.__font).grid(row=0, column=0)
        Entry(frame, width=10,
            font=self.__font).grid(row=0, column=1, padx=5, pady=5)
    
    def __handle_scaling_3D(self, tab: Frame) -> None:
        frame = LabelFrame(tab)
        frame.pack(pady=50)

        Label(frame, text = "Scale (Sx, Sy, Sz):", font=self.__font).grid(row=0, column=0)
        Entry(frame, width=10,
            font=self.__font).grid(row=0, column=1, padx=5, pady=5)
        
    def __prepare_elements(self) -> None:
        self.__tab_control.pack(expand = 1, fill ="both")
        
        Button(self.__top_level, text="Transform", font=self.__font, fg="blue",
            command=self.__top_level_click_event).pack(pady=5)

    def print_error(self, error: Exception) -> None:
        print(error)

    def __top_level_click_event(self) -> None:
        try:
            selected_index = self.__tab_control.index("current")
            selected_type = self.__tab_control.tab(selected_index, 'text')
            children_widgets = self.__frames[selected_type].winfo_children()
            
            user_content = {
                "type": selected_type,
                "option": self.__select_options[self.__selected_object.get()],
                "entries": []
            }

            for label_frame in children_widgets:
                if label_frame.winfo_class() == "Labelframe":
                    for child in label_frame.winfo_children():
                        if child.winfo_class() == "Entry":
                            user_content["entries"].append(child.get())

            self.__top_level_object_handler(user_content)

        except Exception as error:
            print(error)
        finally:
            self.__top_level.quit()
            self.__top_level.destroy()
