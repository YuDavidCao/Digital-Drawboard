# Digital-Drawboard
A easy-to-use, all time and customizable digital drawboard on PC

## Prerequisite

- pip install tk (if you do not have tkinter) 
- pip install pynput
- pip install pyautogui

## What it does

It is a whiteboard app that works without a separate screen, which means that you can directly write on your screen. The app draws lines when you hold down your mouse (just like other drawboard does!). The control panel or app config can be opened when pressing "left ctrl" + "P", and hidden when pressing "left ctrl" + "O". **Note: the keylogger (pynput) has some issues with key input when holding ctrl or shift which can mess up the stored hotkey if you find the hotkey command not working, press left ctrl and backspace to fix it. Sorry for this inconvenience.** Here are some of the more detailed functions it provides:

###1. Drawing. 
Draw lines on your screen, you can disable/enable it when needed either with the hotkey left ctrl and shift or in the control panel. In the control panel, you can also change line width and color. To enable eraser mode, you can either press "left alt" + "shift" or turn it on/off in the control panel. To clear your whiteboard, you can either press "left alt" + "backspace" or clear in the control panel.

###2. Create shape/text. 
To do that, you will have to open the control panel and go to Action -> Utilities, under that page, you can create click the corresponding button to create an unfilled rectangle, filled rectangle,  unfilled oval, filled oval, textfield, and lines. The very bottom button continous means that if it's currently continous, you will for example always draw lines, otherwise, you will only be able to draw one line or shape and click the button again to draw another line/shape

###3. Hotkey config.
The hotkey config can be found under Action -> hotkey config

###4 Object List.
You can delete objects you've created under Action -> Objects. When you click on one of the object inside the listbox, the according object will be highlighted, you can press enter to delete clicked objects.

## What's next for digital drawboard

1. Make the GUI look better
2. Being able to save the current drawings, objects, and texfields into some kind of file. 
3. Being able to switch between multiple canvases.
4. A better keyboard and mouse monitor considers the keyboard input issue and the fact that I was using two separate modules to achieve this function.

