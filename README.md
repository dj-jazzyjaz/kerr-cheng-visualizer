Welcome to the KERR-CHENG visualizer!
To run it, you need python3 installed with numpy.


To change the model file, open visualizer.py and change the name of the '.kyxpp' file at the bottom of the code.

Please read our [course paper](https://lfcps.org/course/lfcps20/projects/jacheng_jkerr.pdf) to learn more about the visualizer and valid model syntax. 
Model variables must be annotated. We suggest using time-based models instead of event based due to numerical error. 

To run, just run the visualizer.py file.
```
cd {path}/KerrChengVisualizer
python visualizer.py
```

### Videos 
We have included a few video demos. Here is a brief description of each video clip.
1. `auto_lab3_1.mp4`: An auto run of lab 3, which is a robot on a circular track with a static obstacle.
2. `auto_lab3_1_broken.mp4`: An auto run of lab 3, except the controller's condition for acceleration is unsafe leading to collision.
3. `auto_lab4_2.mp4`: An auto run of lab 4, where the robot follows differential drive while avoiding a static obstacle.
4. `auto_lab4_2_broken.mp4`: An auto run of lab 4, where the controller doesn't account for the obstacle leading to collision.
5. `manual_lab4_1_broken.mp4`: A differential drive model from lab 4, but the model is incorrect. We show manual mode, where the user chooses the option on each iteration.
6. `manual_lab4_2.mp4`: Manual mode using the corrected differential drive model from lab 4, as well as collision-safe controller. 
