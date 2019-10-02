# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/   

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from tkinter import *
from tkinter import ttk


LARGE_FONT= ("Verdana", 12)
style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)


def animate(i):
    pullData = open("sampleText.txt","r").read()
    dataList = pullData.split('\n')
    xList = []
    yList = []
    for eachLine in dataList:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xList.append(int(x))
            yList.append(int(y))

    a.clear()
    a.plot(xList, yList)

    
            

class Lelitxipawe():


    def __init__(self, root): #Se inicia la ventana con sus caracteristicas predeterminadas
        self.root = root
        self.root.config(background='white')#Color de fondo
        self.root.update_idletasks()
        #self.w, self.h = root.winfo_screenwidth(), root.winfo_screenheight()
        self.w,self.h = 1280,720

        self.root.geometry("%dx%d+0+0" % (self.w, self.h))
        self.root.minsize(self.w, self.h)#Tamaño minimo de la ventana
        #self.root.maxsize(self.w, self.h)#Tamaño minimo de la ventana
        self.root.attributes('-zoomed', True)
#       self.root.overrideredirect(True) 
        self.root.title("simPEATC") ##Titulo de la ventana

        self.frame_contenido = Frame(bd=1, bg="white",relief="sunken").pack()
        Button(self.frame_contenido, text="hola").pack()
        Button(self.frame_contenido, text="lola").pack()
        
        

        canvas = FigureCanvasTkAgg(f, master=self.frame_contenido)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.frame_contenido)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)



if __name__ == '__main__':

    root = Tk()

    my_gui = Lelitxipawe(root)
    ani = animation.FuncAnimation(f, animate, interval=1000)

    root.mainloop()