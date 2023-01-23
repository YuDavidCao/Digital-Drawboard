from pynput import keyboard
from pynput import mouse
import pyautogui

from tkinter import Tk, Label, Button, Canvas, Scale, Toplevel, Menu, Frame, NSEW, HORIZONTAL, Entry, Listbox, Scrollbar, Text, END, StringVar, LEFT
from concurrent import futures
from tkinter import ttk
import json
import time

class Drawboard():

    def __init__(self) -> None:
        self.root = Tk()
        self.keypressed = set()
        self.pool = futures.ThreadPoolExecutor(max_workers=10)
        self.t1 = self.pool.submit(self.start)
        self.root.geometry("1920x1080")
        self.canvas = Canvas(self.root, bg="white", width="1920", height="1080")
        self.canvas.grid()
        self.clicked = False
        self.pause = False
        self.typing = False
        self.erasing = False
        self.terminate = False
        self.ultilities = 0    
        self.textfield = None
        self.option = None
        self.ml = None
        self.kl = None
        self.prev_x = -1
        self.prev_y = -1
        self.original_text = ""
        self.text_object_container = []
        self.rectangle_object_container = []
        self.oval_object_container = []
        self.eraser = self.canvas.create_oval(10,10,20,20,width=3, outline="")
        self.root.attributes('-topmost', True) 
        self.root.attributes("-transparentcolor", "white")        
        self.root.attributes('-alpha',1)
        self.root.overrideredirect(True)
        self.initialize_pop_up()
        self.t2 = self.pool.submit(self.on_move)     
        self.root.mainloop()
        return

    def initialize_pop_up(self):
        self.option = Toplevel()
        self.option.attributes('-alpha',0)
        self.frames = [Frame(self.option),Frame(self.option),Frame(self.option),Frame(self.option)]
        self.frames[0].grid(row = 0,column = 0,sticky = NSEW,padx = 10,pady = 10)
        self.frames[1].grid(row = 0,column = 0,sticky = NSEW,padx = 10,pady = 10)
        self.frames[2].grid(row = 0,column = 0,sticky = NSEW,padx = 10,pady = 10)
        self.frames[3].grid(row = 0,column = 0,sticky = NSEW,padx = 10,pady = 10)
        self.frames[0].tkraise()
        self.gridmap = [[[0 for x in range(20)] for x in range(20)] for y in range(len(self.frames))]
        self.varmap  = [[[0 for x in range(20)] for x in range(20)] for y in range(len(self.frames))]
        self.menubar = Menu(self.root)
        self.Actions = Menu(self.menubar, tearoff = 0)
        self.Actions.add_command(label ='Option',command = lambda: self.show_frame(0))
        self.Actions.add_command(label ='Hotkey config',command = lambda: self.show_frame(1))  
        self.Actions.add_command(label ='Utilities',command = lambda: self.show_frame(2))
        self.Actions.add_command(label ='Objects',command = lambda: self.show_frame(3))
        self.Actions.add_separator()       
        self.Actions.add_command(label ='Exit',command = self.option.destroy)
        self.Actions.add_command(label ='Reboot',command = self.reboot)      
        self.menubar.add_cascade(label ="Actions", menu = self.Actions)
        self.option.config(menu = self.menubar)
        self.addlabel(0,0,0,"     Configure your drawboard here!     ")
        self.addbutton(0,1,0,"Enable drawboard", self.enable_drawboard)
        self.addbutton(0,2,0,"Disable drawboard", self.disable_drawboard)
        self.addbutton(0,3,0,"Clear drawboard", self.clear_drawboard)
        self.addbutton(0,4,0,"Clear hotkey", self.clear_hotkey)
        self.addscale(0,5,0,self.change_line_width, text=f"Change line width, current {canvas_line_width}",f=1,t=30,horizontal=True)
        self.addscale(0,6,0,self.change_rgb_r, text=f"Change rgb red, current {rgb_r}", f=0,t=255,horizontal=True)
        self.addscale(0,7,0,self.change_rgb_g, text=f"Change rgb green, current {rgb_g}", f=0,t=255,horizontal=True)
        self.addscale(0,8,0,self.change_rgb_b, text=f"Change rgb blue, current {rgb_b}", f=0,t=255,horizontal=True)
        self.addbutton(0,9,0,"",None)
        self.addbutton(0,10,0,"eraser mode (color white)", self.erase_mode)
        self.addbutton(0,11,0,"close eraser mode", self.close_erase_mode)
        self.addlabel(1,0,0,"Hotkey config")
        self.addlabel(1,1,0,f"enable/disable canvas: {hotkey_canvas_pause}")
        self.addlabel(1,2,0,f"clear canvas: {hotkey_erase_all}")
        self.addlabel(1,3,0,f"clear stored: {hotkey_clear_hotkey}")
        self.addlabel(1,4,0,f"open option: {hotkey_open_popup}")
        self.addlabel(1,5,0,f"hide option: {hotkey_close_popup}")
        self.addlabel(1,6,0,f"Terminate app: {hotkey_delete}")
        self.addlabel(1,7,0,f"Erase: {hotkey_eraser_mode}")
        self.addlabel(1,8,0,f"\\x0f is key O, \\x10 is key P")       
        self.addlabel(2,0,0,"                      Ultilities:                      ")
        self.addonepbutton(2,1,0,"draw a rectangle (no fill)", self.draw_ultilities, 1)
        self.addonepbutton(2,2,0,"draw a rectangle (fill)", self.draw_ultilities, 2)
        self.addonepbutton(2,3,0,"draw an oval (no fill)", self.draw_ultilities, 3)
        self.addonepbutton(2,4,0,"draw an oval (fill)", self.draw_ultilities, 4)
        self.addonepbutton(2,5,0,"draw a textfield", self.draw_ultilities, 5)
        self.addonepbutton(2,6,0,"draw a line", self.draw_ultilities, 6)
        self.addbutton(2,7,0,f"current continuity -> {continuous}", self.change_continuity)
        self.addlabel(3,0,0,"                      Object list                      ")
        self.addscrollbar(3,1,1)
        self.addlistbox(3,1,0)
        self.gridmap[3][1][0].bind("<Return>",lambda event :self.delete_object(event))
        self.gridmap[3][1][0].bind("<Button-1>",lambda event :self.high_light(event))
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
        self.option.attributes('-topmost', True)          

    def config_listboix(self):
        self.gridmap[3][1][0].delete(0, END)
        for i in range(len(self.rectangle_object_container)):
            self.gridmap[3][1][0].insert(END,f"rectangle {i+1}")
        for i in range(len(self.oval_object_container)):
            self.gridmap[3][1][0].insert(END,f"oval {i+1}")
        for i in range(len(self.text_object_container)):
            self.gridmap[3][1][0].insert(END,f"textfield {i+1}")
        
    def high_light(self, event):
        for i in range(len(self.gridmap[3][1][0].get(0, 'end'))):
            if(i not in self.gridmap[3][1][0].curselection()):
                wl = self.gridmap[3][1][0].get(i).split()
                if(wl[0]=="rectangle"):
                    self.canvas.itemconfig(self.rectangle_object_container[int(wl[1])-1],outline = "black")
                elif(wl[0]=="oval"):
                    self.canvas.itemconfig(self.oval_object_container[int(wl[1])-1],outline = "black")
            else:
                wl = self.gridmap[3][1][0].get(i).split()
                if(wl[0]=="rectangle"):
                    self.canvas.itemconfig(self.rectangle_object_container[int(wl[1])-1],outline = "yellow")
                elif(wl[0]=="oval"):
                    self.canvas.itemconfig(self.oval_object_container[int(wl[1])-1],outline = "yellow")
        self.config_listboix()        

    def delete_object(self, event):
        for i in self.gridmap[3][1][0].curselection():
            wl = self.gridmap[3][1][0].get(i).split()
            if(wl[0]=="rectangle"):
                self.canvas.delete(self.rectangle_object_container[int(wl[1])-1])
                self.rectangle_object_container.pop(int(wl[1])-1)
            elif(wl[0]=="oval"):
                self.canvas.delete(self.oval_object_container[int(wl[1])-1])
                self.oval_object_container.pop(int(wl[1])-1)
        self.config_listboix()

    def change_continuity(self):
        global continuous
        continuous = not continuous
        self.addbutton(2,7,0,f"current continuity -> {continuous}", self.change_continuity)

    def close_erase_mode(self):
        global rgb_r
        global rgb_g
        global rgb_b
        rgb_r = 0
        rgb_g = 0
        rgb_b = 0
        self.erasing = False
        self.gridmap[0][6][0].config(label = f"Change rgb red, current {rgb_r}")
        self.gridmap[0][7][0].config(label = f"Change rgb green, current {rgb_g}")
        self.gridmap[0][8][0].config(label = f"Change rgb blue, current {rgb_b}")
        self.gridmap[0][6][0].set(rgb_r)
        self.gridmap[0][7][0].set(rgb_g)
        self.gridmap[0][8][0].set(rgb_b)
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))        

    def erase_mode(self):
        global rgb_r
        global rgb_g
        global rgb_b
        rgb_r = 255
        rgb_g = 255
        rgb_b = 255
        self.erasing = True
        self.gridmap[0][6][0].config(label = f"Change rgb red, current {rgb_r}")
        self.gridmap[0][7][0].config(label = f"Change rgb green, current {rgb_g}")
        self.gridmap[0][8][0].config(label = f"Change rgb blue, current {rgb_b}")
        self.gridmap[0][6][0].set(rgb_r)
        self.gridmap[0][7][0].set(rgb_g)
        self.gridmap[0][8][0].set(rgb_b)
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r-1,rgb_g,rgb_b)))

    def stop_drawboard(self):
        self.root.destroy()
        return

    def draw_ultilities(self, tp):
        self.ultilities = tp

    def on_move(self):
        while True:
            time.sleep(0.02)
            if(self.terminate):
                self.ml.stop()
                self.kl.stop()
                self.root.after(1,self.stop_drawboard)
                return                     
            else:        
                x, y = pyautogui.position()
                x1 = x-15-canvas_line_width/2
                y1 = y-15-canvas_line_width/2
                x2 = x+15+canvas_line_width/2     
                y2 = y+15+canvas_line_width/2
                if(self.erasing):
                    self.canvas.lift(self.eraser)
                    self.canvas.coords(self.eraser,x1,y1,x2,y2)                
                    self.canvas.itemconfig(self.eraser,outline = "black")
                else:
                    self.canvas.itemconfig(self.eraser,outline="")
                if(self.clicked):
                    if(not self.pause and not self.ultilities):
                        if(abs(self.prev_x-x)>=canvas_line_width/2 or abs(self.prev_y-y)>=canvas_line_width/2):
                            if(self.erasing):
                                self.canvas.create_line(self.prev_x,self.prev_y,x,y,width=canvas_line_width+30, fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                            else:
                                self.canvas.create_line(self.prev_x,self.prev_y,x,y,width=canvas_line_width, fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                        else:
                            if(self.erasing):
                                self.canvas.create_oval(x1+3,y1+3,x2-3,y2-3,outline = "",fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                            else:                    
                                self.canvas.create_rectangle(x,y,x+canvas_line_width/10,y+canvas_line_width/10,width=canvas_line_width, outline = self.rgb_to_hex((rgb_r,rgb_g,rgb_b)),fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                                #self.canvas.create_rectangle(x-canvas_line_width/2,y-canvas_line_width/2,x+canvas_line_width/2,y+canvas_line_width/2, fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                        self.prev_x = x
                        self.prev_y = y                             

    def open_pop_up(self):
        self.option.attributes('-alpha',1)
       

    def close_pop_up(self):
        self.option.attributes('-alpha',0)

    def rgb_to_hex(self,rgb):
        return '#'+'%02x%02x%02x' % rgb

    def change_rgb_r(self,event):
        global rgb_r
        rgb_r = self.gridmap[0][6][0].get()
        self.gridmap[0][6][0].config(label = f"Change rgb red, current {rgb_r}")
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))

    def change_rgb_g(self,event):
        global rgb_g
        rgb_g = self.gridmap[0][7][0].get()
        self.gridmap[0][7][0].config(label = f"Change rgb green, current {rgb_g}")
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))

    def change_rgb_b(self,event):
        global rgb_b
        rgb_b = self.gridmap[0][8][0].get()
        self.gridmap[0][8][0].config(label = f"Change rgb blue, current {rgb_b}")
        self.gridmap[0][9][0].config(bg=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))

    def change_line_width(self, event):
        global canvas_line_width 
        canvas_line_width = self.gridmap[0][5][0].get()
        self.gridmap[0][5][0].config(label = f"Change line width, current {canvas_line_width}")

    def clear_hotkey(self):
        self.keypressed = set()

    def clear_drawboard(self):
        self.canvas.delete("all")
        self.rectangle_object_container = []
        self.oval_object_container = []
        self.text_object_container = []
        self.eraser = self.canvas.create_oval(10,10,20,20,width=3, outline="")

    def enable_drawboard(self):
        self.pause = False

    def disable_drawboard(self):
        self.pause = True

    def start(self):

        def on_press(key):
            k = str(key).replace("Key.","").replace("'",'').replace("\\\\",'\\')
            if(self.typing):
                if(k=="space"):
                    self.original_text+=" "
                elif(k=="enter"):
                    self.original_text+="\n"
                elif(k=="backspace"):
                    self.original_text = self.original_text[:-1]
                else:
                    self.original_text += k
                self.canvas.itemconfig(self.textfield, text=self.original_text)
            self.keypressed.add(k)
            print(self.keypressed)           
            if(self.keypressed == hotkey_delete):
                self.terminate = True
            elif(self.keypressed == hotkey_erase_all):
                self.clear_drawboard()
            elif(self.keypressed == hotkey_canvas_pause):
                self.pause = not self.pause
            elif(self.keypressed == hotkey_open_popup):
                self.open_pop_up()
            elif(self.keypressed == hotkey_close_popup):
                self.close_pop_up()
            elif(self.keypressed == hotkey_eraser_mode):                
                if(rgb_b!=255 or rgb_g!=255 or rgb_r!=255):
                    self.erase_mode()
                else:
                    self.close_erase_mode()
            if(hotkey_clear_hotkey.issubset(self.keypressed)):
                self.keypressed = set()                   

        def on_release(key):
            k = str(key).replace("Key.","").replace("'",'').replace("\\\\",'\\')
            self.keypressed.discard(k)            

        def on_click(x,y,button,pressed):  
            if(pressed):
                self.prev_x = x
                self.prev_y = y                 
                self.clicked = True
            else:
                self.typing = False
                if(self.textfield is not None):
                    self.canvas.delete(self.textfield)
                    self.textfield = None
                if(self.ultilities != 0):
                    if(abs(self.prev_x-x)>7 and abs(self.prev_y-y)>7):
                        if(self.ultilities == 1):
                            self.rectangle_object_container.append(self.canvas.create_rectangle(self.prev_x,self.prev_y,x,y,width = canvas_line_width))
                        elif(self.ultilities == 2):
                            self.rectangle_object_container.append(self.canvas.create_rectangle(self.prev_x,self.prev_y,x,y,width = canvas_line_width,fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b))))
                        elif(self.ultilities == 3):
                            self.oval_object_container.append(self.canvas.create_oval(self.prev_x,self.prev_y,x,y,width = canvas_line_width))
                        elif(self.ultilities == 4):
                            self.oval_object_container.append(self.canvas.create_oval(self.prev_x,self.prev_y,x,y,width = canvas_line_width,fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b))))
                        elif(self.ultilities == 5):
                            self.original_text = ""
                            self.textfield = self.canvas.create_text(x, y, text=self.original_text, fill="black")
                            self.typing = True                        
                        elif(self.ultilities == 6):
                            self.canvas.create_line(self.prev_x,self.prev_y,x,y,width = canvas_line_width,fill=self.rgb_to_hex((rgb_r,rgb_g,rgb_b)))
                        self.config_listboix()
                if(not continuous):
                    self.ultilities = 0
                self.prev_x = -1
                self.prev_y = -1                
                self.clicked = False

        self.kl = keyboard.Listener(on_press=on_press,on_release=on_release)
        self.ml = mouse.Listener(on_click=on_click)
        self.kl.start()
        self.ml.start()
        self.kl.join()
        self.ml.join()
        return

    def reboot(self):
        self.option.destroy()
        self.option = None
        self.open_pop_up()

    def show_frame(self,frame):
        """raise the selected frame from self.frames"""
        self.frames[frame].tkraise()

    def refresh(original_function):
        """wrapper function for every "add" functions, clear the existing widget"""
        def wrapper_function(*args,**kwargs):
            self,frame,row,column = args[0:4]
            if  self.gridmap[frame][row][column]:
                self.gridmap[frame][row][column].grid_remove()
            self.gridmap[frame][row][column] = None
            original_function(*args,**kwargs)
        return wrapper_function  

    def refresh_widget(self,frame,row,column):
        """refresh selected tkinter widget"""
        if self.gridmap[frame][row][column]:
            self.gridmap[frame][row][column].grid_remove()
        self.gridmap[frame][row][column] = None  

    @refresh
    def addscale(self,frame,row,column,command,text = "",rspan = 1,cspan = 1, horizontal = False, f = 0, t = 100):
        if(horizontal):
            self.gridmap[frame][row][column] = Scale(self.frames[frame], orient=HORIZONTAL, from_=f, to=t, label=text, command=command)
        else:
            self.gridmap[frame][row][column] = Scale(self.frames[frame], from_=f, to=t, label=text, command=command)
        self.gridmap[frame][row][column].grid(row = row, column = column, padx = 2, pady = 2, sticky = NSEW, rowspan = rspan, columnspan = cspan)

    @refresh
    def addtext(self,frame,row,column, width = 0, height = 0, rspan = 1, cspan = 1):
        """add a tkinter Text widget"""
        self.gridmap[frame][row][column] = Text(self.frames[frame])
        self.gridmap[frame][row][column].grid(row = row, column = column, padx = 2, pady = 2, sticky = NSEW, rowspan = rspan, columnspan = cspan)
        if width:
            self.gridmap[frame][row][column].config(width = width)
        if height:
            self.gridmap[frame][row][column].config(height = height)

    @refresh
    def addlabel(self,frame,row,column,text,cspan = 1,rspan = 1, img = None):
        """add a tkinter label"""
        self.gridmap[frame][row][column] = Label(self.frames[frame],text = text, image = img, compound = LEFT)
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2,pady = 2, sticky = NSEW, columnspan = cspan, rowspan = rspan)
        
    @refresh
    def addbutton(self,frame,row,column,text,command,cspan = 1,rspan = 1):
        """add a tkinter button"""
        self.gridmap[frame][row][column] = Button(self.frames[frame],text = text,command = command)
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2,pady = 2, sticky = NSEW, columnspan = cspan, rowspan = rspan)        

    @refresh
    def addonepbutton(self,frame,row,column,text,command,p1,cspan = 1,rspan = 1):
        """add a tkinter button with one parameter"""
        self.gridmap[frame][row][column] = Button(self.frames[frame],text = text, command = lambda:command(p1))
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2,pady = 2, sticky = NSEW, columnspan = cspan, rowspan = rspan)         

    @refresh
    def addtwopbutton(self,frame,row,column,text,command,p1,p2,cspan = 1,rspan = 1):
        """add a tkinter button with two parameter"""
        self.gridmap[frame][row][column] = Button(self.frames[frame],text = text,command = lambda:command(p1,p2))
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2,pady = 2, sticky = NSEW, columnspan = cspan, rowspan = rspan)         

    @refresh
    def addentry(self,frame,row,column,key1,key2,command1,command2,cspan = 1,rspan = 1, default = ""):
        """add a tkinter entry"""
        self.gridmap[frame][row][column] = Entry(self.frames[frame])
        self.gridmap[frame][row][column].insert(END, default)
        if command1:
            self.gridmap[frame][row][column].bind(key1,command1)
        if command2:
            self.gridmap[frame][row][column].bind(key2,command2)
        self.gridmap[frame][row][column].grid(row = row, column = column, padx = 2,pady = 2, sticky=NSEW, columnspan = cspan, rowspan = rspan)    

    @refresh
    def addcombobox(self,frame,row,column,options,command): 
        """add a tkinter combobox, also generates a tkinter.StringVar() object"""
        self.varmap[frame][row][column] = StringVar()
        self.gridmap[frame][row][column] = ttk.ComboBox(self.frames[frame],values = options, variable=self.varmap[frame][row][column], command = command)
        self.gridmap[frame][row][column].grid(row = row, column = column, padx = 2,pady = 2, sticky=NSEW)  

    @refresh
    def addlistbox(self,frame,row,column, height = 10, rspan = 1, cspan = 1):
        """add a tkinter listbox"""
        self.gridmap[frame][row][column] = Listbox(self.frames[frame],height=height,yscrollcommand = self.gridmap[frame][row][column+1].set)
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2, pady = 2, sticky=NSEW, rowspan = rspan, columnspan = cspan)
        self.gridmap[frame][row][column].config(highlightbackground="#0b5162", highlightcolor="#0b5162", highlightthickness=2, relief="solid")

    @refresh
    def addscrollbar(self,frame,row,column, rspan = 1, cspan = 1):
        """add a tkinter scrollbar"""
        self.gridmap[frame][row][column] = Scrollbar(self.frames[frame])
        self.gridmap[frame][row][column].grid(row = row,column = column, padx = 2, pady = 2, sticky=NSEW, rowspan = rspan, columnspan = cspan)

if __name__ == "__main__":
    with open("Settings.json","r") as r:
        setting = json.load(r)    
    rgb_r = setting["rgb_r"]
    rgb_g = setting["rgb_g"]
    rgb_b = setting["rgb_b"]
    canvas_line_width = setting["canvas_line_width"]
    hotkey_delete = set(setting["hotkey_delete"])
    hotkey_erase_all = set(setting["hotkey_erase_all"])
    hotkey_canvas_pause = set(setting["hotkey_canvas_pause"])
    hotkey_clear_hotkey = set(setting["hotkey_clear_hotkey"])
    hotkey_open_popup = set(setting["hotkey_open_popup"])
    hotkey_close_popup = set(setting["hotkey_close_popup"])
    hotkey_eraser_mode = set(setting["hotkey_eraser_mode"])
    continuous = setting["continuous"]
    Drawboard()
