from visutil import *
import tkinter as tk
import math
class Robot:
    DEFAULT_RAD=.5
    def __init__(self, in_dict, id):
        self.x_key = in_dict.get('x')
        self.y_key = in_dict.get('y')
        self.r_key = in_dict.get('r')
        self.dx_key = in_dict.get('dx')
        self.dy_key = in_dict.get('dy')
        self.id = id


    def draw(self, state, canvas, ghostid = None, ghostscore = None):
        x = state.get(self.x_key, 0)
        y = state.get(self.y_key, 0)
        r = state.get(self.r_key, self.DEFAULT_RAD)
        if ghostid is not None:
            stip='gray25'
            tt=f'{ghostid}'
            fcolor='gray'
            r *=.85
        else:
            stip=''
            tt=''
            fcolor=COLORS[self.id % len(COLORS)]

        x_c, y_c = get_canvas_location(x, y)
        r_c = r * PIXEL_RATIO

        x0 = x_c - r_c
        x1 = x_c + r_c
        y0 = y_c - r_c
        y1 = y_c + r_c
        

        canvas.create_oval(x0, y0, x1, y1, fill=fcolor, tag="robot")

        dx = state.get(self.dx_key)
        dy = state.get(self.dy_key)
        if dx is not None and dy is not None:
            endx,endy=get_canvas_location(x+1.5*r*dx,y+1.5*r*dy)
            canvas.create_line(x_c,y_c,endx,endy,arrow=tk.LAST,width=4, tag="robot")
        canvas.create_text(x_c,y_c,text=tt,font=('Times',-int(1.5*r_c),'bold'),fill='yellow', tag="robot")
        # if ghostscore is not None:
            # s = f'{ghostid}:{round(ghostscore, 2)}'
            # canvas.create_text(x_c+1.25*r_c,y_c,text=s,font=('Times',-int(r_c)), fill='blue')
    def clicked(self, state, canv_x, canv_y):
        #returns whether the given click is within the robot at position defined by state
        world_x,world_y = get_world_location(canv_x,canv_y)
        x = state.get(self.x_key, 0)
        y = state.get(self.y_key, 0)
        r = state.get(self.r_key, self.DEFAULT_RAD)
        return math.hypot(world_x-x,world_y-y) < r