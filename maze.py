# Notebook compatible version of maze

from IPython.display import display
from ipycanvas import Canvas
import time
from ipycanvas import MultiCanvas


# --------------------------------
# Configuration
# --------------------------------
text=False
graphics=True
step_delay = 0.2  # seconds per move

# Constants
GANG = 0
MUUR = 1
DOEL = 3
TOKEN = 2

# --------------------------------
# Environment
# --------------------------------
class environment:
    blokskes=[]
    doolhof=[]
    start=(0,0)
    s=(0,0)
    e=(0,0)
    cv=None
    w=400
    h=300
    dh=0
    dw=0
    cw=0
    ch=0
    heading=0  # 0=right, 90=up, 180=left, 270=down

env = environment()

# --------------------------------
# Maze loading
# --------------------------------
def lees_doolhof(path):
    doolhof=[]
    s = e = None
    with open(path) as f:
        for rijnr, line in enumerate(f):
            line = line.rstrip("\n")
            if not line: continue
            rij = []
            for kolomnr, x in enumerate(line):
                if x==' ':
                    rij.append(GANG)
                elif x=='S':
                    s = (rijnr, kolomnr)
                    rij.append(TOKEN)
                elif x=='E':
                    e = (rijnr, kolomnr)
                    rij.append(DOEL)
                else:
                    rij.append(MUUR)
            doolhof.append(rij)
    return doolhof, s, e

# --------------------------------
# Drawing
# --------------------------------
def draw_doolhof_once():
    global env
    cv = env.maze_layer
    cv.clear()  # just in case
    cv.fill_style = "black"
    cv.fill_rect(0, 0, env.w, env.h)

    for j, row in enumerate(env.doolhof):
        for i, cell in enumerate(row):
            if cell == MUUR:
                color = "black"
            elif cell == TOKEN:
                color = "red"
            elif cell == DOEL:
                color = "green"
            else:
                color = "white"
            if color!="black":
              cv.fill_style = color
              cv.fill_rect(i*env.cw, j*env.ch, env.cw, env.ch)

def draw_player_smooth(old_pos=None):
    """
    Draw the player as a triangle on the player layer.
    Only erases the previous position by covering it with the maze color.
    """
    global env
    cv = env.player_layer

    cv.clear()

    # Draw new player
    r, c = env.s
    cx = c*env.cw + env.cw/2
    cy = r*env.ch + env.ch/2
    size = min(env.cw, env.ch) * 0.5  # triangle size

    # Determine triangle points based on heading
    if env.heading == 0:       # right
        points = [(cx-size/2, cy-size/2), (cx-size/2, cy+size/2), (cx+size/2, cy)]
    elif env.heading == 90:    # up
        points = [(cx-size/2, cy+size/2), (cx+size/2, cy+size/2), (cx, cy-size/2)]
    elif env.heading == 180:   # left
        points = [(cx+size/2, cy-size/2), (cx+size/2, cy+size/2), (cx-size/2, cy)]
    elif env.heading == 270:   # down
        points = [(cx-size/2, cy-size/2), (cx+size/2, cy-size/2), (cx, cy+size/2)]

    # Draw triangle
    cv.fill_style = "blue"
    cv.begin_path()
    cv.move_to(*points[0])
    cv.line_to(*points[1])
    cv.line_to(*points[2])
    cv.close_path()
    cv.fill()

# --------------------------------
# Movement helpers
# --------------------------------
def move_to(p, delay=True):
    global env
    r, c = p
    if env.doolhof[r][c] == MUUR:
        print("AUCH! Hit the wall!")
        return

    old_pos = env.s
    env.s = (r, c)
    if graphics:
        draw_player_smooth(old_pos)
    if text:
        printCurrent()
    if delay:
        import time
        time.sleep(step_delay)

def move_up(delay=True): move_to((env.s[0]-1, env.s[1]), delay)
def move_down(delay=True): move_to((env.s[0]+1, env.s[1]), delay)
def move_left(delay=True): move_to((env.s[0], env.s[1]-1), delay)
def move_right(delay=True): move_to((env.s[0], env.s[1]+1), delay)

# --------------------------------
# Heading & turning
# --------------------------------
def turn_right(delay=True):
    global env
    env.heading = (env.heading - 90) % 360
    old_pos = env.s
    if graphics:
        draw_player_smooth(old_pos)
    if text:
        printCurrent()
    if delay: time.sleep(step_delay)

def turn_left(delay=True):
    global env
    env.heading = (env.heading + 90) % 360
    old_pos = env.s
    if graphics:
        draw_player_smooth(old_pos)
    if text:
        printCurrent()
    if delay: time.sleep(step_delay)

def go_forward(delay=True):
    if env.heading==0: move_right(delay)
    elif env.heading==90: move_up(delay)
    elif env.heading==180: move_left(delay)
    elif env.heading==270: move_down(delay)

# --------------------------------
# Direction helpers
# --------------------------------
def ahead():
    if env.heading==0: return (0,1)
    elif env.heading==90: return (-1,0)
    elif env.heading==180: return (0,-1)
    elif env.heading==270: return (1,0)

def dirright():
    if env.heading==0: return (1,0)
    elif env.heading==90: return (0,1)
    elif env.heading==180: return (-1,0)
    elif env.heading==270: return (0,-1)

def dirleft():
    if env.heading==0: return (-1,0)
    elif env.heading==90: return (0,-1)
    elif env.heading==180: return (1,0)
    elif env.heading==270: return (0,1)

def free_forward(): 
    delta = ahead()
    ns = (env.s[0]+delta[0], env.s[1]+delta[1])
    return env.doolhof[ns[0]][ns[1]] != MUUR

def free_right():
    delta = dirright()
    ns = (env.s[0]+delta[0], env.s[1]+delta[1])
    return env.doolhof[ns[0]][ns[1]] != MUUR

def free_left():
    delta = dirleft()
    ns = (env.s[0]+delta[0], env.s[1]+delta[1])
    return env.doolhof[ns[0]][ns[1]] != MUUR

def found_exit():
    r,c = env.s
    return env.doolhof[r][c]==DOEL

# --------------------------------
# Printing
# --------------------------------
def printCurrent():
    global env
    for r,row in enumerate(env.doolhof):
        line=""
        for c,cell in enumerate(row):
            if (r,c)==env.s:
                if env.heading==0: line+=">"
                elif env.heading==90: line+="^"
                elif env.heading==180: line+="<"
                elif env.heading==270: line+="V"
            else:
                if cell==TOKEN: line+="S"
                elif cell==DOEL: line+="E"
                elif cell==MUUR: line+=u"\u2588"
                else: line+=" "
        print(line)
    print()

# --------------------------------
# Load maze
# --------------------------------
def laad_doolhof(path="doolhof.txt"):
    global env

    env.doolhof, env.s, env.e = lees_doolhof(path)
    env.start = env.s
    env.dh = len(env.doolhof)
    env.dw = len(env.doolhof[0])
    env.w = 400
    env.h = 300
    env.cw = env.w / env.dw
    env.ch = env.h / env.dh
    env.heading = 0

    # Create MultiCanvas: 0 = maze, 1 = player
    env.cv = MultiCanvas(2, width=env.w, height=env.h)
    env.maze_layer = env.cv[0]
    env.player_layer = env.cv[1]

    display(env.cv)

    draw_doolhof_once()   # draw maze once
    draw_player_smooth()  # draw player on top

# --------------------------------
# Keep original API aliases
# --------------------------------
turnright=turnRight=Turnright=TurnRight=turn_Right=Turn_right=Turn_right=turn_right
turnleft=turnLeft=Turnleft=TurnLeft=turn_Left=Turn_left=Turn_Left=turn_left
goforward=Goforward=goForward=GoForward=go_forward
laaddoolhof=Laaddoolhof=laadDoolhof=LaadDoolhof=Laad_doolhof=laad_Doolhof=Laad_Doolhof=laad_doolhof
loadmaze=loadMaze=LoadMaze=Loadmaze=load_maze=load_Maze=Load_Maze=load_maze=laaddoolhof
foundexit=Foundexit=FoundExit=foundExit=Found_exit=Found_Exit=found_Exit=found_exit
freeforward=freeForward=Freeforward=FreeForward=free_Forward=Free_forward=Free_Forward=free_forward
Freeright=freeRight=FreeRight=freeright=Free_right=free_Right=Free_Right=free_right
FreeLeft=freeLeft=Freeleft=freeleft=Free_left=free_Left=Free_Left=free_left