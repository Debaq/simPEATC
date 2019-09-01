# http://effbot.org/tkinterbook/
from tkinter import *
from tkinter import ttk
from random import randint
from PIL import ImageTk, Image

# these two imports are important
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
from matplotlib.text import OffsetFrom
from matplotlib.gridspec import GridSpec

import numpy as np
import csv

import time
import threading
##Variables de forma del grafico
Y_ampl = 18
X_time = 10
average = 2000
niveldb = 80

fonticksmini = {'fontsize': 6}

GridTrue = True


continuePlotting = False

def change_state():
    global continuePlotting
    print(2)

    if continuePlotting == True:
        continuePlotting = False
    else:
        continuePlotting = True
    
 
def data_points():
    a = []
    b = []

    with open('curva.txt','r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        for row in plots:
            a.append(float(row[0]))
            b.append(float(row[1]))

    return a,b
 

def averageTick(average):
    ticksAverage = average/13
    ticks =[0]
    i = 0
    while i < 13:
        i = i+1
        suma = ticksAverage * i
        ticks.append(suma)
    return ticks


def graph():
    
    fig = plt.figure(num="TUG", figsize=(3,3))
    t = np.arange(0, 3, .01)
    gs1 = GridSpec(9, 8)
    gs1.update(left=0.05, right=0.95, wspace=0.5, hspace=1, top=0.98, bottom=0.08)

    ax1 = plt.subplot(gs1[0:1,0:2])
    ax1.grid(GridTrue)
    ax1.set_xlim(0,1)
    ax1.set_ylim(0,3)
    ax1.set_yticks([1,2])
    ax1.set_xticks([0,1])
    ax1.xaxis.set_major_formatter(plt.NullFormatter()) 

    ax1.set_yticklabels(['D','I'],fontdict=fonticksmini,horizontalalignment='left')

    ax2 = plt.subplot(gs1[0:1, 3:8])
    #ax2.yaxis.set_major_formatter(plt.NullFormatter()) 
    ax2.grid(GridTrue)
    ax2.set_xlim(0,average)
    ax2.set_ylim(0,200)
    tiks_X = averageTick(average)
    ax2.set_yticks([0,40, 150, 200])
    ax2.set_xticks(tiks_X)
    ax2.set_yticklabels(['',40,'',200],fontdict=fonticksmini) 
    ax2.set_xticklabels([0,'','','','','','','','','','','','',average],fontdict=fonticksmini) 

    ax3 = plt.subplot(gs1[1:, 0:4])
    ax3.yaxis.set_major_formatter(plt.NullFormatter()) 
    ax3.grid(GridTrue, linestyle='--')
    ax3.set_xticks(np.arange(X_time+1))
    ax3.set_yticks(np.arange(Y_ampl+1))
    ax3.set_xlim(0,X_time)
    ax3.set_ylim(0,Y_ampl)


    ax4 = plt.subplot(gs1[1:, 4:8])
    ax4.yaxis.set_major_formatter(plt.NullFormatter()) 
    ax4.grid(GridTrue, linestyle='--')
    ax4.set_xlim(0,X_time)
    ax4.set_ylim(0,Y_ampl)
    ax4.set_yticks(np.arange(Y_ampl+1))
    ax4.set_xticks(np.arange(X_time+1))

    return fig

def OD_plotter():
    L1 = ax3.plot([1,2,3,4,5,6,7,8,9,10],[5,5,5,5,5,5,5,5,5,5])
    pass




def app():
    # initialise a window.
    root = Tk()
    root.config(background='white')
    root.geometry("1000x700")
    
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    geometry_X =  int(screen_width/2) - int(1280/2)
    geometry_Y = int(screen_height/2) - int(720/2)
    size="1280x720+"+str(geometry_X)+"+"+str(geometry_Y)
    root.geometry(size)
    root.minsize(1280, 720)
    root.call('wm', 'iconphoto', root._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))
    root.title("simPEATC") ##Titulo de la ventana
    root.title("simPEATC") ##Titulo de la ventana
    frame_name = Frame(bd=1, bg="blue",relief="sunken") ##crea la caja superior
    frame_contenido = Frame(bd=1, bg="green",relief="sunken") ##crea la caja central
    frame_info = Frame(bd=1, bg="red",relief="sunken") ##crea la caja inferior
    frame_command = Frame(bd=1, bg="black",relief="sunken") ##crea la caja inferior

    #split = 0.5
    frame_name.place(rely=0, relheight=.03, relwidth=1)
    frame_contenido.place(rely=.03, relx=.2, relheight=1.0-0.03, relwidth=.8)
    frame_command.place(rely=.03, relheight=1.0-0.03, relwidth=.2)

    frame_info.place(rely=1.0-0.03, relheight=.03, relwidth=1)

    fig = graph()
    graphy = FigureCanvasTkAgg(fig, master=frame_contenido)
    graphy.get_tk_widget().pack(side="top",fill='both',expand=True)

    menu = Menu(root)
    root.config(menu=menu)
    file = Menu(menu, tearoff=0)
    file.add_command(label="Abrir usuario", command=OD_plotter)
    file.add_command(label="Nuevo usuario", command=OD_plotter)
    file.add_command(label="Cerrar usuario", command=OD_plotter)
    file.add_separator()
    file.add_command(label="Salir", command=OD_plotter)
    menu.add_cascade(label="Archivo", menu=file)
    edit = Menu(menu, tearoff=0)
    edit.add_command(label="Nueva Prueba")
    edit.add_command(label="Borrar Prueba")
    edit.add_separator()

    edit.add_command(label="Abrir prueba suelta")

    menu.add_cascade(label="Editar prueba", menu=edit)

    help = Menu(menu, tearoff=0)
    help.add_command(label="Ayuda")
    help.add_separator()
    help.add_command(label="Acerca de nosotros",)
    menu.add_cascade(label="Ayuda", menu=help)
    label_name = StringVar()
    label_name = Label(frame_name, textvariable=label_name, text="Label")
    label_name.pack(side = LEFT)
    
    root.update()
    fr_cmd_with = frame_command.winfo_width()
    fr_cmd_height = frame_command.winfo_height()

#Tabs en comandos cuadro izquierdo pantalla principal
    note_command = ttk.Notebook(frame_command, width=fr_cmd_with, height=fr_cmd_height)
    note_command.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
#Tab 1: registro
    tab_registro= Frame(note_command)
    note_command.add(tab_registro, text='Registro')

#Tab1, frame1: Estimulo
    frame_estimulo =Frame(tab_registro, relief=GROOVE, borderwidth=2)
    label_nivel = ('Intensidad : '+str(niveldb)+' db nHL')
    Label(frame_estimulo, text=label_nivel).grid(row=1,sticky=W)
    Label(frame_estimulo, text='Estimulo : Click').grid(row=2,sticky=W)
    Label(frame_estimulo, text='Mask : Off').grid(row=3,sticky=W)
    Label(frame_estimulo, text='Estimulo',font=("Courier",10)).grid(row=0)
    frame_estimulo.place(rely=0.03)

#Tab1, frame2: Nuevo test
    frame_new_test=Frame(tab_registro, relief=GROOVE, borderwidth=2)
    check_array = ['0db', '10db', '20db', '30db',
                    '40db', '50db', '60db', '70db', '80dB',
                    '90db', '100db']
    check_vars = []
    for i in range(len(check_array)):
            check_vars.append(StringVar())
            check_vars[-1].set(0)
            c = Checkbutton(frame_new_test, text=check_array[i], variable=check_vars[-1], command=lambda i=i: printSelection(i), onvalue=1, offvalue=0)
            if i < 1:
                c.grid(row=i+1,sticky=W)
            else:
                c.grid(row=i,sticky=W)
    Lado_estimulo = [
        ("OD", "1"),
        ("OI", "2"),
        ("Bilateral", "3")]

    v = StringVar()
    v.set("1") # initialize

    for text, mode in Lado_estimulo:
         b = Radiobutton(frame_new_test, text=text,
                         variable=v, value=mode)
         b.grid(sticky=W)
    Label(frame_new_test, text='Prueba',font=("Courier",10)).grid(row=0)
    frame_new_test.place(rely=0.03, relx=0.6)


#Tab1, frame3: reproductibilidad
    frame_reproductibilidad=Frame(tab_registro, relief=GROOVE, borderwidth=2)
    reproductibilidad = ttk.Progressbar(frame_reproductibilidad, 
                                        orient="horizontal",length=200, mode="determinate")
    reproductibilidad.grid(row=2, columnspan=3)
    Label(frame_reproductibilidad, text='0').grid(row=1, column=0, sticky=W)
    Label(frame_reproductibilidad, text='50').grid(row=1, column=1, sticky=W+E)
    Label(frame_reproductibilidad, text='100').grid(row=1, column=2, sticky=E)
    Label(frame_reproductibilidad, text='% de reproductibilidad ',
            font=("Courier",10)).grid(row=0, columnspan=3)
    frame_reproductibilidad.place(rely=0.47, relx=0)


#Tab1, frame4: promediaciones
    frame_promediaciones=Frame(tab_registro, relie=GROOVE, borderwidth=2)
    Label(frame_promediaciones, text='Promediaciones',
            font=("Courier",10)).grid(row=0)
    prom_estim=0
    rechazos=0
    Label(frame_promediaciones,text=('Promediaciones: '+str(prom_estim))).grid(row=1, sticky=W)
    Label(frame_promediaciones,text=('Rechazos: '+str(rechazos))).grid(row=2,sticky=W)
    frame_promediaciones.place(rely=0.3, relx=0)

#Tab1, frame 5: Botones de control
    frame_iniciar=Frame(tab_registro, relie=GROOVE, borderwidth=0)

    Button(frame_iniciar,text="Iniciar", height=2, widt=25).grid(row=1)
    Button(frame_iniciar,text="Pausa", height=1, widt=25).grid(row=2)
    Button(frame_iniciar,text="Siguiente estimulo", height=1, widt=25).grid(row=3)

    frame_iniciar.place(rely=0.6, relx=0.02)



    def printSelection(i):
            print(check_vars[i].get())


    def plotter():

            ax3.cla()
            ax3.grid()     
            L1 = ax3.plot([1,2,3,4,5,6,7,8,9,10],[5,5,5,5,5,5,5,5,5,5])

            graph.draw()
            time.sleep(1)
 
    def gui_handler():
        change_state()
        threading.Thread(target=OD_plotter).start()

 #   b = Button(root, text="Start/Stop", command=plotter, bg="red", fg="white")
  #  b.pack()
    
    root.mainloop()
 
if __name__ == '__main__':
    app()

    #https://www.machinelearningplus.com/plots/top-50-matplotlib-visualizations-the-root-plots-python/