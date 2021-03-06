import tkinter as tk
from constants import *
import uuid

class Object:
    def __init__(self, obj_type, obj_name, obj_desc):
        self.obj_ids = []
        self.obj_type = obj_type
        self.obj_name = obj_name
        self.obj_desc = obj_desc
        self.obj_text = "Name: %s\nDescription: %s\n" % (self.obj_name, self.obj_desc)
        self.obj_uuid = str(uuid.uuid1())
        self.connected_to = []
        self.connectors = {}
        self.mid_conns = {}
        self.starts = {}
        self.clines = {}

def find_connecting_line(o1, o2):
    for l in o1.clines.keys():
        if o1.clines[l] == o2:
            return l

    return None

def find_connecting_mid_conn(o1, o2):
    for m in o1.mid_conns.keys():
        if o1.mid_conns[m] == o2:
            return m

    return None

def redraw_boundary(canvas, obj, bnode, cur_x, cur_y):
    obj.obj_ids.remove(obj.box)
    obj.obj_ids.remove(obj.text)

    canvas.delete(obj.box)
    canvas.delete(obj.text)

    canvas.coords(bnode, cur_x - OVAL_SIZE, cur_y - OVAL_SIZE, cur_x + OVAL_SIZE, cur_y + OVAL_SIZE)

    (a, b, c, d) = canvas.coords(obj.left)
    xA = (a + c) / 2
    yA = (b + d) / 2
    (a, b, c, d) = canvas.coords(obj.right)
    xB = (a + c) / 2
    yB = (b + d) / 2
    (a, b, c, d) = canvas.coords(obj.mid)
    xC = (a + c) / 2
    yC = (b + d) / 2

    obj.box = canvas.create_line((xA, yA), (xC, yC), (xB, yB), smooth = True, width = 2, tag = "line")

    obj.text = canvas.create_text(xC + 50, yC + 50, text = obj.obj_name, tag = "text")

    obj.obj_ids.append(obj.box)
    obj.obj_ids.append(obj.text)

def redraw_connectors(canvas, obj, dist, x3=None, y3=None, mid_conn=None):
    if mid_conn != None:
        o1 = obj
        o2 = obj.mid_conns[mid_conn]

        canvas.coords(mid_conn, x3 - OVAL_SIZE, y3 - OVAL_SIZE, x3 + OVAL_SIZE, y3 + OVAL_SIZE)

        cline = find_connecting_line(o1, o2)

        if o2.starts[o1]:
            obj = o1
            o1 = o2
            o2 = obj

        canvas.delete(cline)
        del_key = o1.clines.pop(cline)
        del_key = o2.clines.pop(cline)

        (a, b, c, d) = canvas.coords(o1.box)
        x1 = (a + c) / 2
        y1 = (b + d) / 2

        (a, b, c, d) = canvas.coords(o2.box)
        x2 = (a + c) / 2
        y2 = (b + d) / 2

        p1 = (x1, y1)
        p3 = (x3, y3)
        p2 = (x2, y2)

        cline = canvas.create_line(p1, p3, p2, smooth = True, arrow=tk.LAST, width=4, arrowshape = CLINE_ARROW_SHAPE, tag = "cline", fill = CLINE_COLOR)

        o1.clines[cline] = o2
        o2.clines[cline] = o1

        canvas.update()
        add_all_tag(canvas)

        layer_objects(canvas)

        return

    for o in obj.connected_to:
        if o.starts[obj]:
            o1 = o
            o2 = obj
        elif obj.starts[o]:
            o1 = obj
            o2 = o

        mid_conn = find_connecting_mid_conn(o1, o2)

        (a, b, c, d) = canvas.coords(o1.box)
        x1 = (a + c) / 2
        y1 = (b + d) / 2

        (a, b, c, d) = canvas.coords(o2.box)
        x2 = (a + c) / 2
        y2 = (b + d) / 2

        x3 = (x1 + x2) / 2 + dist
        y3 = (y1 + y2) / 2 + dist

        p1 = (x1, y1)
        p3 = (x3, y3)
        p2 = (x2, y2)

        cline = find_connecting_line(o1, o2)
        canvas.delete(cline)
        del_key = o1.clines.pop(cline)
        del_key = o2.clines.pop(cline)

        cline = canvas.create_line(p1, p3, p2, smooth=True, arrow=tk.LAST, width=4, tag = "cline", arrowshape = CLINE_ARROW_SHAPE, fill = CLINE_COLOR)
        o1.clines[cline] = o2
        o2.clines[cline] = o1

        canvas.coords(mid_conn, x3 - OVAL_SIZE, y3 - OVAL_SIZE, x3 + OVAL_SIZE, y3 + OVAL_SIZE)

    canvas.update()
    add_all_tag(canvas)
    layer_objects(canvas)

    return

def create_connector(canvas, points, o1, o2, d):
    (xA, yA, xB, yB, xC, yC) = points

    oval_a = canvas.create_oval(xA - OVAL_SIZE, yA - OVAL_SIZE, xA + OVAL_SIZE, yA + OVAL_SIZE, outline = "blue", fill = "blue", tag = "oval")
    oval_b = canvas.create_oval(xB - OVAL_SIZE, yB - OVAL_SIZE, xB + OVAL_SIZE, yB + OVAL_SIZE, outline = "blue", fill = "blue", tag = "oval")

    if xC == None:
        xC = (xA + xB)/2 + d
    if yC == None:
        yC = (yA + yB)/2 - d

    oval_c = canvas.create_oval(xC - OVAL_SIZE, yC - OVAL_SIZE, xC + OVAL_SIZE, yC + OVAL_SIZE, outline = "blue", fill = "blue", tag=["mid_conn", "oval"])
    line = canvas.create_line((xA, yA), (xC, yC), (xB, yB), smooth = True, arrow = tk.LAST, width = 4, arrowshape = CLINE_ARROW_SHAPE,
                                        tag = "cline", fill = CLINE_COLOR)

    o1.obj_ids.append(oval_a)
    o2.obj_ids.append(oval_b)

    o1.connectors[oval_a] = o2
    o2.connectors[oval_b] = o1

    o1.mid_conns[oval_c] = o2
    o2.mid_conns[oval_c] = o1

    o1.starts[o2] = True
    o2.starts[o1] = False

    o1.clines[line] = o2
    o2.clines[line] = o1

    o1.connected_to.append(o2)
    o2.connected_to.append(o1)

    add_all_tag(canvas)
    canvas.update()

    layer_objects(canvas)


def layer_objects(canvas):
    try:
        canvas.tag_raise("rectangle", "oval")
        canvas.tag_raise("circle", "oval")
        canvas.tag_lower("image", "all")
        canvas.tag_raise("text", "all")
    except:
        pass

    return

def add_all_tag(canvas):
    canvas.addtag_all("all")

def add_process(canvas, obj):
    obj.box_init_x = INIT_RECT_X
    obj.box_init_y = INIT_RECT_Y
    obj.box_init_width = INIT_RECT_WIDTH
    obj.box_init_height = INIT_RECT_HEIGHT

    obj.text_init_x = obj.box_init_x + 75
    obj.text_init_y = obj.box_init_y + 25

    obj.box = canvas.create_rectangle(obj.box_init_x, obj.box_init_y,
                        obj.box_init_width, obj.box_init_height, tag = "rectangle",
                        fill = "yellow", activefill='cyan')
    obj.text = canvas.create_text(obj.text_init_x, obj.text_init_y, text = obj.obj_name, tag = "text", font = PROC_FONT, fill = PROC_TEXT_COLOR)

    obj.obj_ids.append(obj.box)
    obj.obj_ids.append(obj.text)

    canvas.update()
    add_all_tag(canvas)

def add_storage(canvas, obj):
    obj.box_init_x = INIT_CRC_X
    obj.box_init_y = INIT_CRC_Y

    obj.box_init_r = INIT_CRC_RADIUS
    obj.box_init_width = (obj.box_init_x - obj.box_init_r) - (obj.box_init_x + obj.box_init_r)
    obj.box_init_width = (obj.box_init_y - obj.box_init_r) - (obj.box_init_y + obj.box_init_r)

    obj.text_init_x = obj.box_init_x
    obj.text_init_y = obj.box_init_y

    obj.box = canvas.create_oval(obj.box_init_x - obj.box_init_r, obj.box_init_y - obj.box_init_r,
                                                obj.box_init_x + obj.box_init_r, obj.box_init_y + obj.box_init_r,
                                                tag = "circle", activefill='cyan',
                                                fill = "yellow")

    obj.text = canvas.create_text(obj.text_init_x, obj.text_init_y, text = obj.obj_name, tag = "text", font = STOR_FONT, fill = STOR_TEXT_COLOR)

    obj.obj_ids.append(obj.box)
    obj.obj_ids.append(obj.text)

    canvas.update()
    add_all_tag(canvas)

def add_boundary(canvas, obj):
    obj.box_init_x = INIT_BDR_X
    obj.box_init_y = INIT_BDR_Y
    obj.box_init_width = INIT_BDR_WIDTH
    obj.box_init_height = INIT_BDR_HEIGHT

    d = 5

    obj.text_init_x = obj.box_init_x + 50
    obj.text_init_y = obj.box_init_y + 50

    (xA, yA, xB, yB) = (obj.box_init_x, obj.box_init_y, obj.box_init_x + INIT_BDR_LENGTH, obj.box_init_y + INIT_BDR_LENGTH)

    oval_a = canvas.create_oval(xA - OVAL_SIZE, yA - OVAL_SIZE, xA + OVAL_SIZE, yA + OVAL_SIZE, outline = "blue", fill = "blue", tag = ("oval", "bnode", "left"))
    oval_b = canvas.create_oval(xB - OVAL_SIZE, yB - OVAL_SIZE, xB + OVAL_SIZE, yB + OVAL_SIZE, outline = "blue", fill = "blue", tag = ("oval", "bnode", "right"))

    xC = (xA + xB)/2 + d
    yC = (yA + yB)/2 - d

    oval_c = canvas.create_oval(xC - OVAL_SIZE, yC - OVAL_SIZE, xC + OVAL_SIZE, yC + OVAL_SIZE, outline = "blue", fill = "blue", tag= ("oval", "bnode", "mid"))

    obj.left = oval_a
    obj.right = oval_b
    obj.mid = oval_c

    obj.box = canvas.create_line((xA, yA), (xC, yC), (xB, yB), smooth = True, width = 2, tag = "line")
    obj.text = canvas.create_text(obj.text_init_x, obj.text_init_y, text = obj.obj_name, tag = "text")

    obj.obj_ids.append(obj.box)
    obj.obj_ids.append(obj.text)
    obj.obj_ids.append(oval_a)
    obj.obj_ids.append(oval_b)
    obj.obj_ids.append(oval_c)

    canvas.update()
    add_all_tag(canvas)
