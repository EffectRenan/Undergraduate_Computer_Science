from tkinter import Tk
from tkinter import Toplevel
from tkinter import LabelFrame
from tkinter import Button
from tkinter import Canvas
from tkinter import Listbox
from tkinter import Event
from tkinter import LabelFrame
from tkinter import Label
from tkinter import ttk
from tkinter import Entry
from tkinter.constants import END

class MainView:

    def __init__(self, viewport: dict, root: Tk, dimension: int, root_directory: str) -> None:
        self.__dimension = dimension
        self.__root = root 
        self.__root.title("Main")
        self.__font = ("Calibri 10")
        self.__root_directory = root_directory

        self.__viewport_frame = LabelFrame(self.__root, text="Viewport", padx=10, pady=10)

        self.__canvas = Canvas(
            self.__viewport_frame,
            bg="white",
            width = viewport["xvpMax"],
            height = viewport["yvpMax"] 
        )

        self.__rotation_options = ["Rx", "Ry", "Rz"]
        
        self.__vertical_frame = LabelFrame(self.__root, text="Tab", padx=10, pady=5)
        self.__vertical_frame.grid(row=0, column=0)
        self.__list_box = None
        self.__selected_object = None
        self.__rotation_entry = None
        self.__file_entry = None
        self.__file_box = None

    def start_view(self, click_handlers: dict, available_files: list) -> None:

        objectButton = Button(self.__vertical_frame, text="Create an object",
            command=click_handlers["create_object"], fg="blue", font=self.__font)
        objectButton.grid(row=0, column=0, pady=10)

        self.__prepare_navigation(click_handlers)
        self.__prepare_transformation(click_handlers, self.__vertical_frame)
        self.__prepare_listbox()
        self.__prepare_file(click_handlers, self.__vertical_frame, available_files)

        self.__viewport_frame.grid(row=0, column=1)
        self.__canvas.pack()

        self.__root.attributes('-type', 'dialog')
        self.__root.mainloop()  

    def __prepare_navigation(self, click_handlers: dict) -> None:

        def click_rotation_rx() -> None:
            click_handlers["navigation_rotation_rx"](self.__rotation_entry.get())
        
        def click_rotation_ry() -> None:
            click_handlers["navigation_rotation_ry"](self.__rotation_entry.get())

        def click_rotation_rz() -> None:
            click_handlers["navigation_rotation_rz"](self.__rotation_entry.get())

        navigation_frame = LabelFrame(self.__vertical_frame, text="Window", pady=3)
        navigation_frame.grid(row=2, column=0)
        
        buttons_frame = LabelFrame(navigation_frame, text="Navigation", pady=3)
        buttons_frame.grid(row=2, column=0, pady=5, padx=50)

        tmp = Button(buttons_frame, text="Up", command=click_handlers["navigation_up"], 
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=0, column=0)
        tmp = Button(buttons_frame, text="Down", command=click_handlers["navigation_down"],
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=0, column=1)
        tmp = Button(buttons_frame, text="Left", command=click_handlers["navigation_left"], 
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=1, column=0)
        tmp = Button(buttons_frame, text="Right", command=click_handlers["navigation_right"], 
            fg="blue", font=self.__font, width = 5)
        tmp.grid(row=1, column=1)

        tmp = Button(buttons_frame, text="In", command=click_handlers["navigation_in"], 
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=2, column=0)
        tmp = Button(buttons_frame, text="Out", command=click_handlers["navigation_out"],
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=2, column=1)

        camera_frame = LabelFrame(navigation_frame, text="Camera", pady=3)
        camera_frame.grid(row=3, column=0, pady=5, padx=50)

        tmp = Button(camera_frame, text="Up", command=click_handlers["navigation_camera_up"], 
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=0, column=0)
        tmp = Button(camera_frame, text="Down", command=click_handlers["navigation_camera_down"],
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=0, column=1)
        tmp = Button(camera_frame, text="Left", command=click_handlers["navigation_camera_left"], 
            fg="blue", font=self.__font, width=5)
        tmp.grid(row=1, column=0)
        tmp = Button(camera_frame, text="Right", command=click_handlers["navigation_camera_right"], 
            fg="blue", font=self.__font, width = 5)
        tmp.grid(row=1, column=1)

        # tmp = Button(camera_frame, text="In", command=click_handlers["navigation_camera_in"], 
        #     fg="blue", font=self.__font, width=5)
        # tmp.grid(row=2, column=0)
        # tmp = Button(camera_frame, text="Out", command=click_handlers["navigation_camera_out"],
        #     fg="blue", font=self.__font, width=5)
        # tmp.grid(row=2, column=1)

        rotation_frame =  LabelFrame(navigation_frame, text="Rotation °", padx=3)
        rotation_frame.grid(row=4, column=0, padx=5, pady=10)

        self.__rotation_entry = Entry(rotation_frame, width=5, font=self.__font)
        self.__rotation_entry.insert(END, "10")
        self.__rotation_entry.grid(row=0, column=0, pady=5, padx=10)

        tmp = Button(rotation_frame, text="Rx", command=click_rotation_rx, fg="blue", font=self.__font)
        tmp.grid(row=0, column=1, pady=10)
        tmp = Button(rotation_frame, text="Ry", command=click_rotation_ry, fg="blue", font=self.__font)
        tmp.grid(row=0, column=2, pady=10)
        tmp = Button(rotation_frame, text="Rz", command=click_rotation_rz, fg="blue", font=self.__font)
        tmp.grid(row=0, column=3, pady=10)
        


    def __prepare_transformation(self, click_handlers: dict, frame: LabelFrame) -> None:

        def transformation_click() -> None:
            click_handlers["transformation_handler"](self.__selected_object)

        a = Button(frame, text="Transformations", command=transformation_click, fg="blue", font=self.__font)
        a.grid(row=5, column=0, pady=10)
        
    def __prepare_listbox(self) -> None:
        
        def click_select(event: Event) -> None:
            try:
                widget = event.widget
                self.__selected_object = widget.curselection()[0]
            except:
                pass

        self.__list_box = Listbox(self.__vertical_frame, width=30, font=self.__font)
        self.__list_box.grid(row=1, column=0, pady=10)
        self.__list_box.bind("<<ListboxSelect>>", click_select)

    def __prepare_file(self, click_handlers: dict, frame: LabelFrame, available_files: list) -> None:
        
        def click_load() -> None:
            if (self.__file_box.get() != ""):
                click_handlers["file_load"](self.__file_box.get())
        
        def click_save() -> None:
            if (self.__file_entry.get() != ""):
                click_handlers["file_save"](self.__file_entry.get())

        file_trame = LabelFrame(frame, text=f"Files | Root: {self.__root_directory}", padx=10, pady=10)
        file_trame.grid(row=6, column=0)
        
        self.__file_box = ttk.Combobox(file_trame, values=available_files, font=self.__font, width=15)
        self.__file_box.grid(row=0, column=0, padx=5, pady=5)
        tmp = Button(file_trame, text="Load", command=click_load, fg="blue", font=self.__font)
        tmp.grid(row=0, column=1)

        self.__file_entry = Entry(file_trame, width=15, font=self.__font)
        self.__file_entry.grid(row=1, column=0)
        tmp = Button(file_trame, text="Save", command=click_save, fg="blue", font=self.__font)
        tmp.grid(row=1, column=1)

    def clean(self) -> None:
        self.__canvas.delete("all")
        self.__list_box.delete(0,'end')

    def file_list_update(self, available_files: list) -> None:
        self.__file_box["values"] = available_files
        self.__file_box.set("")

    def update_canvas_point(self, all: list, color: str) -> None:
        # create_line in some versions accept the format [(x,y), (x,y)] (tested on ArchLinux 5.10.76-1-lts)
        # Most versions only accept [(x,y), (x+1,y+1)] (tested on Ubuntu 20.04 LTS)
        for i in range(self.__dimension, self.__dimension * 2):
            all[i] += 1 

        self.__canvas.create_line(all, fill=color)

    def update_canvas_line(self, all: list, color: str) -> None:
        self.__canvas.create_line(all, fill=color)

    def list_update(self, userObject: dict) -> None:
        template = f"{userObject.type} - {userObject.name}"
        self.__list_box.insert("end", template)

    def print_msg(self, msg: str) -> None:
        error = Toplevel(self.__root)
        
        def click() -> None:
            error.quit()
            error.destroy()

        Label(error, text = msg, font=self.__font).pack(pady=5)

        Button(error, text="Ok",
            command=click, fg="blue", font=self.__font).pack(pady=5)

        error.attributes('-type', 'dialog')
        error.mainloop()  
