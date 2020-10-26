import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

import os
import objects
from constants import *

#
# Class for creating resizable canvas
#
class ResizingCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        #
        # Calling init of parent
        #
        tk.Canvas.__init__(self, parent, **kwargs)

        #
        # Window configure callback set to self.on_resize method
        #
        self.bind("<Configure>", self.on_resize)

        #
        # Get the width and height requested by the canvas widget
        #  at the time of creating the canvas
        #
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

        # self.image = Image.open("gridlines.png")
        # self.image = self.image.resize((self.width, self.height), Image.ANTIALIAS)
        # self.pimage = ImageTk.PhotoImage(self.image)

        # self.create_image(0, 0, anchor=tk.NW, image=self.pimage, tag="image")

    def on_resize(self, event):
        #
        # Setting scale values to: width or height at the time when resize event was called / width or height at the
        #  beginning (when canvas was created)
        #
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height

        #
        # Set the width and height to those when event was fired
        #
        self.width = event.width
        self.height = event.height

        #
        # Configure the width and height of the canvas
        #
        self.config(width=self.width, height=self.height)
        self.update()

        #
        # Scale "all" objects to the window's scaling
        #
        self.scale("all", 0, 0, wscale, hscale)

        self.create_grid(event)

    def create_grid(self, event=None):
        w = self.winfo_width() # Get current width of canvas
        h = self.winfo_height() # Get current height of canvas
        self.delete('grid_line') # Will only remove the grid_line

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, 100):
            self.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, 100):
            self.create_line([(0, i), (w, i)], tag='grid_line')

class DummyEvent:
    def __init__(self):
        self.x_root = None
        self.y_root = None

class Window(tk.Frame):
    def __init__(self, parent = None):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        #
        # Canvas and context menu (cmenu) are part of the window's object
        #
        self.canvas = None
        self.cmenu = None

        #
        # Canvas width and height initially
        #
        self.cwidth = 500
        self.cheight = 500
        self.objects = []

        #
        # Object that was right under the mouse pointer when right click / left click was fired
        #
        self.rc_obj = None
        self.lc_obj = None

        #
        # The first and the second objects to be joined
        #
        self.j_obj1 = None
        self.j_obj2 = None
        self.l1 = None

        #
        # Draw the initial window
        #
        self.init_window()

    #
    # Returns the object to which the element belongs
    #
    def elem_to_obj(self, elem):
        for obj in self.objects:
            for sub_obj in obj.obj_ids:
                if elem == sub_obj:
                    return obj

        return None

    #
    # Returns the element closest to the pointer when an event is fired
    #
    def get_closest_elems(self, event):
        x, y = self.event_to_canvas_coords(event)
        elems = self.canvas.find_overlapping(x - 50, y - 50, x + 50, y + 50)

        return elems

    #
    # Returns the object closest to the pointer when an event is fired
    #
    def get_closest_obj(self, event):
        elems = self.get_closest_elems(event)

        obj_dict = {}
        for elem in elems:
            obj = self.elem_to_obj(elem)
            if obj == None:
                continue
            try:
                obj_dict[obj] += 1
            except:
                obj_dict[obj] = 1

        if len(obj_dict.values()) == 0:
            return None

        min_val = min(obj_dict.values())

        for key in obj_dict.keys():
            if obj_dict[key] == min_val:
                return key

        return None

    #
    # Converts the co-ordinates at which an event is fired, to the canvas co-ordinates
    #
    def event_to_canvas_coords(self, event):
        return (self.canvas.canvasx(event.x_root), self.canvas.canvasx(event.y_root))

    #
    # Shows a message box
    #
    def show(self, what):
        tk.messagebox.showinfo("Object details", what, icon = "info")

    #
    # Save command callback for edit popup window
    #
    def popup_save_command(self, o, e):
        #
        # Get the text in the edit ScrolledText window
        #
        data = e.get('1.0', tk.END+'-1c')

        data_dict = {}

        #
        # Get the name and description in order to save it in the object
        # NOTE: Using ":" to split lines
        #
        name = desc = ""
        for line in data.split("\n"):
            line_list = line.split(":")
            try:
                left = line_list[0].strip()
                right = line_list[1].strip()
            except:
                pass
            if "name" in left.lower():
                name = right
            if "desc" in left.lower():
                desc = right

        #
        # Set obj_text attribute to the entire data on the edit textpad
        # Set the obj_name to name in the edit_textpad when save event is fired
        # Set the obj_desc to the description in the edit_textpad when save event is fired
        #
        o.obj_text = data
        o.obj_name = name
        o.obj_desc = desc

        #
        # Configure the text of the text item in the object
        #
        self.canvas.itemconfig(o.text, text= "%s..." % (o.obj_name[:16]))

        #
        # Update canvas
        #
        self.canvas.update()

    #
    # Quit popup callback
    #
    def popup_quit_command(self, e):
        e.destroy()

    #
    # Method to draw edit popup window
    #
    def draw_edit_window(self, o):
        #
        # Child of root
        #
        popup_window = tk.Toplevel(self.parent)

        #
        # Set the title
        #
        popup_window.title("Edit Object")

        #
        # Set the size (width x height)
        #
        popup_window.geometry("800x800")

        #
        # Create a menu bar
        #
        menu_bar = tk.Menu(popup_window)
        popup_window.config(menu=menu_bar)

        #
        # Create a file menu under the menu bar
        #
        file_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label="File", menu=file_menu)

        #
        # Text editing area under the edit window
        #
        edit_textpad = ScrolledText(popup_window, width=100, height=80)

        #
        # Populate the text editing area with what is in the attribute obj_text of an object
        #
        edit_textpad.insert(tk.INSERT, o.obj_text)
        edit_textpad.pack()

        #
        # Set callbacks for save menu item and quit menu item
        #
        file_menu.add_command(label="Save", command = lambda obj = o, args = edit_textpad: self.popup_save_command(obj, args))
        file_menu.add_command(label="Quit", command = lambda obj = edit_textpad: self.popup_quit_command(obj))

    #
    # Debug method to show the object's contents
    #
    def show_obj(self):
        obj = self.get_closest_obj(self.event)
        if obj:
            self.draw_edit_window(obj)
            # self.show(obj.__dict__)

    #
    # Right click callback
    #
    def do_rc(self, event):
        try:
            self.cmenu.tk_popup(event.x_root, event.y_root)

            #
            # Set the self.event and object under the mouse when right button was clicked
            #
            self.event = event
            self.rc_obj = self.get_closest_obj(self.event)
        finally:
            self.cmenu.grab_release()

    #
    # Left click callback
    #
    def do_lc(self, event):
        self.event = event
        self.elems_at_event = self.get_closest_elems(self.event)
        self.elems_at_event = [x for x in self.elems_at_event if "grid_line" not in self.canvas.itemcget(x, "tags")]

        self.obj_at_event = self.get_closest_obj(event)
        self.elem_is_bnode = False
        self.elem_is_mid_conn = False

        for elem in self.elems_at_event:
            elem_tags = self.canvas.itemcget(elem, "tags")

            if "bnode" in elem_tags:
                self.elem_is_bnode = True
                self.bnode = elem
                break
            elif "mid_conn" in elem_tags:
                self.elem_is_mid_conn = True
                self.mid_conn_elem = elem
                break

        x, y = self.event_to_canvas_coords(event)

        self.move_start_x = x
        self.move_start_y = y

    def init_window(self):
        self.parent.title("Threat Modeling Tool")
        self.pack(fill=tk.BOTH, expand=1)

        self.parent.update()
        self.cwidth = self.parent.winfo_width()
        self.cheight = self.parent.winfo_height()

        self.canvas = ResizingCanvas(self.parent, width=self.cwidth, height=self.cheight, bg="white", highlightthickness=0)

        self.canvas.pack()

        self.menu_bar = tk.Menu(self.parent)
        self.parent.config(menu = self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar)
        self.file_menu.add_command(label = "New", command = self.new_threat_model)

        self.menu_bar.add_cascade(label = "File", menu = self.file_menu)

        self.obj_menu = tk.Menu(self.parent)
        self.obj_menu.add_command(label = "Add Process", command = self.add_process)
        self.obj_menu.add_command(label = "Add Storage", command = self.add_storage)
        self.obj_menu.add_command(label = "Add Boundary", command = self.add_boundary)

        self.menu_bar.add_cascade(label = "Objects", menu = self.obj_menu)

        self.create_context_menu()
        self.parent.bind("<Button-3>", self.do_rc)
        self.parent.bind("<Button-1>", self.do_lc)
        self.parent.bind("<B1-Motion>", self.move)

    def mid_conn_to_obj(self, mid):
        for obj in self.objects:
            if mid in obj.mid_conns.keys():
                return obj
        return None

    def move(self, event):
        if len(self.elems_at_event) == 0:
            return

        cur_x, cur_y = self.event_to_canvas_coords(event)

        if self.elem_is_bnode:
            conn_obj = self.elem_to_obj(self.bnode)
            objects.redraw_boundary(self.canvas, conn_obj, self.bnode, cur_x, cur_y)
            return

        if self.obj_at_event != None:
            diff_x = cur_x - self.move_start_x
            diff_y = cur_y - self.move_start_y

            self.move_start_x = cur_x
            self.move_start_y = cur_y

            for elem in self.obj_at_event.obj_ids:
                self.canvas.move(elem, diff_x, diff_y)

            objects.redraw_connectors(self.canvas, self.obj_at_event, 10)
            return

        if self.elem_is_mid_conn:
            conn_obj = self.mid_conn_to_obj(self.mid_conn_elem)
            objects.redraw_connectors(self.canvas, conn_obj, 10, x3 = cur_x, y3 = cur_y, mid_conn = self.mid_conn_elem)
            return

        return

    def move_stop(self, event):
        cur_x, cur_y = self.event_to_canvas_coords(event)
        self.move_stop_x = cur_x
        self.move_stop_y = cur_y

    def join(self):
        if self.j_obj1 == None:
            self.j_obj1 = self.rc_obj
            (a, b, c, d) = self.canvas.coords(self.j_obj1.box)
            self.xA = (a + c) / 2
            self.yA = (b + d) / 2
            return

        if self.j_obj2 == None:
            if self.j_obj1 == None:
                return
            self.j_obj2 = self.rc_obj

            if self.j_obj1.obj_uuid == self.j_obj2.obj_uuid:
                self.j_obj1 = None
                self.j_obj2 = None
                return

            (a, b, c, d) = self.canvas.coords(self.j_obj2.box)
            self.xB = (a + c) / 2
            self.yB = (b + d) / 2

            objects.create_connector(self.canvas, (self.xA, self.yA, self.xB, self.yB, None, None), self.j_obj1, self.j_obj2, 10)

            self.j_obj1 = None
            self.j_obj2 = None

            return


    def create_context_menu(self):
        self.cmenu = tk.Menu(self.parent, tearoff = 0)
        self.cmenu.add_command(label ="Cut")
        self.cmenu.add_command(label ="Copy")
        self.cmenu.add_command(label ="Paste")
        self.cmenu.add_command(label ="Reload")
        self.cmenu.add_separator()
        self.cmenu.add_command(label ="Rename")
        self.cmenu.add_command(label = "Info", command = self.show_obj)
        self.cmenu.add_command(label = "Join", command = self.join)
        self.cmenu.add_command(label = "Clear canvas", command = self.clear_canvas)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_grid()

        return

    def add_process(self):
        proc = objects.Object("Process", "New Process", "New Process Description")
        objects.add_process(self.canvas, proc)
        self.objects.append(proc)

    def add_storage(self):
        store = objects.Object("Storage", "New Storage Object", "New Storage Object Description")
        objects.add_storage(self.canvas, store)
        self.objects.append(store)

    def add_boundary(self):
        boundary = objects.Object("Boundary", "New Threat Boundary", "New Threat Boundary Description")
        objects.add_boundary(self.canvas, boundary)
        self.objects.append(boundary)

    def new_threat_model(self):
        msg = tk.messagebox.askquestion("Save Changes ?", "Changes made to the current threat model are not saved, save it?", icon = "warning")
        if msg == "no":
            self.canvas.delete("all")
            return
        else:
            file_name = tk.filedialog.askopenfilename(  initialdir = "C:\\",
                                                        title = "Select a File name to save as",
                                                        filetypes = (("JSON Files", "*.json"), ("All files", "*.*")))
            if os.path.isfile(file_name):
                msg_ow = tk.messagebox.askquestion( "File exists", "File al-ready exists, overwrite?", icon = "warning")
                if msg_ow == "yes":
                    try:
                        ofd = open(file_name, "w+")
                        #
                        # Create an JSON of items, and save it
                        #
                        ofd.close()
                    except:
                        tk.messagebox.showinfo("Save error", "Error while saving file", icon = "warning")
                    return
                else:
                    return

            try:
                ofd = open(file_name, "w")
                #
                # Create an JSON of items, and save it
                #
                ofd.close()
            except:
                tk.messagebox.showinfo("Save error", "Error while saving file", icon = "warning")

            return
    def client_exit(self):
        exit()


if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.geometry("400x400")

    app = Window(root)

    root.mainloop()
