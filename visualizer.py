from kparser import parse
import time
from tkinter import *
from syntax import *
import random
from visutil import * 
import numpy as np
def prof(fun,*args):
    import cProfile, pstats, io
    pr = cProfile.Profile()
    pr.enable()
    res=fun(*args)
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    return res
class Sim:
    def __init__(self, input_string):
        state, precon, postcon, tree, robots = parse(input_string)
        print("Preconditions\n")
        precon.print()
        print("\nPostconditions")
        postcon.print()

        print("\nBelow is the tree parsed from your file",end="\n\n")
        tree.print()
        # TODO: have user verify if tree ok

        self.state = state # State object
        print()
        for k in self.state.vars():
            if self.state.get(k) is None:
                print(f"Warning: variable {k} is not defined and might cause a crash during execution.")
        print()
        self.precon = precon # Formula
        try:
            self.precon.eval(self.state)
        except:
            print("Warning, the given start start doesn't pass preconditions")
        self.postcon = postcon # Formula
        self.robots = robots # List of Robot
        self.tree = tree 
        self.window = Tk()

        # Create buttons
        self.buttons = {
            'auto': Button(self.window, text="Auto", command=self.run_auto, anchor="center"),
            'manual': Button(self.window, text="Manual", command=self.start_manual, anchor="center"),
        }

        self.buttons['auto'].pack()
        self.buttons['manual'].pack()

        self.labelText = StringVar()
        self.label = Label(self.window, textvariable=self.labelText, justify=LEFT)

        self.labelText.set("KeYmeara X Simulator")
        self.label.pack()

        self.canvas = Canvas(self.window, height=CANVAS_HEIGHT, width=CANVAS_WIDTH, bg="white")
        self.canvas.pack()
        self.canvas.focus_set()
        self.window.mainloop()

   

    '''
    Auto
    '''
    def choose_trace(self):
        ntraces = self.tree.expand(self.state)
        #filter out ode with 0
        traces=[]
        for choices,end in ntraces:
            if 0 in choices:continue
            traces.append((choices,end))
        hs = [self.postcon.get_heuristic(end_state) for _, end_state in traces]
        min_h = np.inf
        min_i = None
        for i, h in enumerate(hs):
            if h is not None and h < min_h:
                min_h = h
                min_i = i
        if min_i is None:
            trace = random.choice(traces)
        else:
            trace = traces[min_i]

        self.run_trace(trace)

    def run_auto(self):
        self.canvas.delete(ALL)
        self.hideButtons()
        self.labelText.set("Running Auto")
        # Check if top level is loop
        if isinstance(self.tree, Loop):
            self.tree = self.tree.arg
            while(True):
                self.choose_trace()

        else:
            self.choose_trace()

    '''
    Manual
    '''
    def start_manual(self):
        self.canvas.delete(ALL)
        self.hideButtons()
        self.labelText.set("Manual Mode")
        self.choosing=False
        if isinstance(self.tree, Loop):
             # If loop, strip off top level, go to choose_trace
            self.tree = self.tree.arg 
            self.window.bind("<Button-1>",lambda e:self.onClick(e,True))
            self.draw_traces(True)
        else:
            # If not loop, go to choose_trace
            self.window.bind("<Button-1>",lambda e:self.onClick(e,False))
            self.draw_traces(False)

    def onClick(self,event,loop):
        if not self.choosing:return
        for i in range(len(self.traces)):
            _,end_state = self.traces[i]
            for r in self.robots:
                if r.clicked(end_state,event.x,event.y):
                    self.choosing=False
                    self.run_manual(self.traces[i],loop)
                    return

    def draw_traces(self, loop):
        # Show ghost robots. User clicks to select trace
        self.traces=self.tree.expand(self.state)
        for r in self.robots:
            r.draw(self.state,self.canvas)
        for i in range(len(self.traces)):
            _,end_state = self.traces[i]
            for r in self.robots:
                h = self.postcon.get_heuristic(end_state)
                r.draw(end_state,self.canvas,i,h)
        self.choosing=True

    def run_manual(self, trace, loop):
        # Runs trace.
        self.run_trace(trace)
        # When finished, goes back to choose_trace if loop, otherwise, sim is finished.
        if loop:
            self.canvas.delete("robot")
            self.draw_traces(loop)
            self.canvas.update()

    '''
    Both
    '''
    def run_trace(self, trace):
        # Runs 1 step of the program. I.e., carries out all choices in trace and shows updated robots
        choices, end_state = trace
        print("Running trace {}".format(choices))
        label, c = self.tree.toString(choices, 0)
        states,_ = self.tree.eval(self.state, choices)
        # Update drawing
        for state in states:
            self.redraw(state, label)
            # self.label.pack()
            time.sleep(0.001)
        self.state=end_state

    def redraw(self, state, label=""):
        self.canvas.delete(ALL)
        for r in self.robots:
            r.draw(state,self.canvas)

        self.canvas.create_text(50,100,text= "Chosen branch: \n" + label + "\n \nState:\n" + str(state.vars_round()),font=('Arial',12,'bold'),fill='black',justify=LEFT, anchor=W, width=CANVAS_WIDTH-50)
        self.canvas.update()

    def hideButtons(self):
        self.buttons['auto'].pack_forget()
        self.buttons['manual'].p1ack_forget()

if __name__ =='__main__':
    # Change the file name to run a different model
    text=open('example_model.kyxpp').read()
    Sim(text)

