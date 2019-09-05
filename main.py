# Librerias Necesarias
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import numpy as np
import sys
sys.path.insert(1, 'config/')
import languaje as lang
import setting as stt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Ellipse
from matplotlib.text import OffsetFrom
from matplotlib.gridspec import GridSpec

import json 





##Lenguaje
def i18n(a,b,*f):
    i18n = lang.i18n(a,b)
    return i18n


##Variables de forma del gráfico
Y_ampl = 18
X_time = 10
average = 2000
niveldb = 80

fonticksmini = {'fontsize': 6}

GridTrue = True
LANG=0

continuePlotting = False

def cmd(icon):
    pass


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

class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
 
    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background='white', relief='solid', borderwidth=1,
                       font=("arial", "10", "normal"))
        label.pack(ipadx=1)
 
    def close(self, event=None):
        if self.tw:
            self.tw.destroy()

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
# Se inicia la ventana
    root = Tk()
    root.config(background='white')
    root.geometry(stt.size_window[0])#Tamaño inicial de la ventana
    root.update_idletasks()
    root.minsize(stt.size_window[1], stt.size_window[2])#Tamaño minimo de la ventana
    #root.maxsize(stt.size_window[1], stt.size_window[2])#mantiene un tamaño fijo 

    root.call('wm', 'iconphoto', root._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))#Icono de la ventana
    root.title("simPEATC") ##Titulo de la ventana
    
#Configuración de los Frames, proporciones en setting.py variable stt.size_frame
    frame_quick = Frame(bd=1,relief="sunken") ##crea la caja superior
    frame_contenido = Frame(bd=1, bg="white",relief="sunken") ##crea la caja derecha
    frame_info = Frame(bd=1,relief="sunken") ##crea la caja inferior
    frame_command = Frame(bd=1,relief="sunken") ##crea la caja izquierda

    frame_quick.place(relx=0, rely=0, relwidth=stt.size_frame['up'][0], relheight=stt.size_frame['up'][1])
    frame_contenido.place(relx=stt.size_frame['izq'][0],rely=stt.size_frame['up'][1],
                        relwidth=stt.size_frame['der'][0], relheight=stt.size_frame['der'][1])
    #frame_command.place(relx=0, rely=stt.size_frame['up'][1], relwidth=stt.size_frame['izq'][0],
    #                    relheight=stt.size_frame['izq'][1])
    frame_command.place(relx=0,rely=stt.size_frame['up'][1],relheight=stt.size_frame['izq'][1], width=stt.size_frame['izq'][5])
    frame_info.place(relx=0, rely=stt.size_frame['down'][3], relwidth=stt.size_frame['down'][0],
                    relheight=stt.size_frame['down'][1])

#Se llama al grafico para que se posicione sobre la caja Derecha como canvas
    fig = graph()
    graphy = FigureCanvasTkAgg(fig, master=frame_contenido)
    graphy.get_tk_widget().pack(side="top",fill='both',expand=True)

#Menú
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

    menu.add_cascade(label="Editar", menu=edit)

    help = Menu(menu, tearoff=0)
    help.add_command(label="Ayuda")
    help.add_separator()
    help.add_command(label="Acerca de nosotros",)
    menu.add_cascade(label="Ayuda", menu=help)

 #Comandos para actualizar información sobre la pantalla, y obtener la información del ancho y alto   
    root.update()
    fr_cmd_with = frame_command.winfo_width()
    fr_cmd_height = frame_command.winfo_height()

#Tabs en comandos cuadro izquierdo pantalla principal
    note_command = ttk.Notebook(frame_command, width=stt.size_frame['izq'][5], height=fr_cmd_height)
    #note_command.grid(row=1, column=0, columnspan=50, rowspan=49, sticky='NESW')
    note_command.pack(expand=True, fill=BOTH)
#Tab 1: registro
    tab_registro= Frame(note_command)
    note_command.add(tab_registro, text=lang.i18n('record',LANG,0))

    tab_mark= Frame(note_command)
    note_command.add(tab_mark, text=lang.i18n('edit',LANG,0))
    tab_latency= Frame(note_command)
    note_command.add(tab_latency, text=lang.i18n('latency',LANG,0))
        
#Tab1, frame1: Estimulo
    frame_estimulo =Frame(tab_registro, relief=GROOVE, borderwidth=2)
    label_nivel = (lang.i18n('level',LANG,0)+':'+str(niveldb)+' db nHL')
    Label(frame_estimulo, text=label_nivel).grid(row=1,sticky=W)
    Label(frame_estimulo, text=lang.i18n('record',LANG,0)+':'+ lang.stim[0]).grid(row=2,sticky=W)#el stimulo debe ser modificable
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
    frame_new_test.place(rely=0.03, relx=0.65)


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
    frame_reproductibilidad.place(rely=0.5, relx=0.07)


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

    Button(frame_iniciar, state=DISABLED,text="Iniciar", height=2, width=22).grid(row=1)
    Button(frame_iniciar, state=DISABLED,text="Pausa", height=1, width=22).grid(row=2)
    Button(frame_iniciar, state=DISABLED,text="Siguiente estimulo", height=1, width=22).grid(row=3)

    frame_iniciar.place(rely=0.65, relx=0.07)

#Quick Bar
    #Button(frame_quick, text='Ayuda').pack(anchor=W)
    width = 50
    height = 50
    icons = ('new', 'save', 'saveas', 'print', 'potential', 'config', 'help')
    names = ('Nuevo', 'Guardar', 'Guardar como...','Imprimir', 'Potenciales', 'Configurar', 'Ayuda')
    for i, icon in enumerate(icons):
        tool_bar_icon = PhotoImage(file='resources/icons/{}.png'.format(icon))
        #cmd = eval(icon)
        small_logo = tool_bar_icon.subsample(4, 4)
        tool_bar = Button(frame_quick, bd=0, image=small_logo, )
        tool_bar.image = small_logo
        button1_ttp = CreateToolTip(tool_bar, names[i])
        tool_bar.pack(side='left')
    test = StringVar()
    select_test = ttk.Combobox(frame_quick, textvariable=test,state="readonly")
    select_test['values']=['PEAT, Tono Click','PEAT, tono Burst', 'PEAT tono Chirp']
    select_test.current(0)
    select_test.pack(side='left')



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

 
    root.mainloop()
 
if __name__ == '__main__':
    app()

