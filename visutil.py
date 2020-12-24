PIXEL_RATIO = 50  # Num pixels/unit
CANVAS_HEIGHT = 1000 # pixels
CANVAS_WIDTH = 1000 # pixels
COLORS = ["blue", "orange", "red", "green", "cyan", "brown", "magenta"]

def get_canvas_location(x, y):
    x = x * PIXEL_RATIO
    y = y * PIXEL_RATIO
    x = CANVAS_WIDTH/2 + x
    y = CANVAS_HEIGHT/2 - y
    return x, y

def get_world_location(canv_x,canv_y):
	x = canv_x - CANVAS_WIDTH/2
	y = CANVAS_HEIGHT/2 - canv_y
	return x/PIXEL_RATIO,y/PIXEL_RATIO