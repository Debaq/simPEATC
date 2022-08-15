#Librerias Necesarias
#Tkinter para dibujar el Gui, PIL para trabajar con img
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

#Librerias para trabajr numeros y datos importados
import numpy as np
import csv

#Libreria para utilizar parametros especificos del sistema
import sys
sys.path.insert(1, 'config/') #se señala carpeta donde se encuentran librerias propias

#Librerias propias para manejar componentes externos, principalmente configuraciones
import languaje as lang
import setting as stt

#Libreria para controlar gráficos, es necesario analisar si se puede enviar a libreria propia 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Ellipse
import matplotlib.animation as animation
from matplotlib.text import OffsetFrom
from matplotlib.gridspec import GridSpec



##Variables de forma del gráfico
Y_ampl = 18
X_time = 10
average = 2000
niveldb = 80

fonticksmini = {'fontsize': 6}

GridTrue = True
LANG=0

continuePlotting = False






class Lelitxipawe():
	'''
	Clase principal de la Ventana
	'''
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
#		self.root.overrideredirect(True)
		self.root.call('wm', 'iconphoto', self.root._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))#Icono de la ventana
		self.root.title("simPEATC") ##Titulo de la ventana
		self.app()


	def app(self): #Estructura de la ventana
		self.txokiñ()
		self.ñizol()
		self.wirin()

	def ñizol(self): #Menú principal
		menu = Menu(self.root)
		self.root.config(menu=menu)
		file = Menu(menu, tearoff=0)
		file.add_command(label="Abrir usuario")
		file.add_command(label="Nuevo usuario")
		file.add_command(label="Cerrar usuario")
		file.add_separator()
		file.add_command(label="Salir")
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

	def txokiñ(self):#Marcos y estructura
		#Configuración de los Frames, proporciones en setting.py variable size_frame
		size_frame=stt.size_screen(self.w,self.h)

		self.frame_quick = Frame(bd=1,relief="sunken") ##crea la caja superior
		self.frame_contenido = Frame(bd=1, bg="white",relief="sunken") ##crea la caja derecha
		self.frame_info = Frame(bd=1,relief="sunken") ##crea la caja inferior
		self.frame_command = Frame(bd=1,relief="sunken") ##crea la caja izquierda
		#se ubican los frames en la ventana principal
		self.frame_quick.place(	relx=size_frame['up'][0], rely=size_frame['up'][1], 
								relwidth=size_frame['up'][2], relheight=size_frame['up'][3])
		self.frame_contenido.place(	relx=size_frame['der'][0], rely=size_frame['der'][1], 
									relwidth=size_frame['der'][2], relheight=size_frame['der'][3])
		self.frame_command.place(	relx=size_frame['izq'][0], rely=size_frame['izq'][1], 
									relwidth=size_frame['izq'][2], relheight=size_frame['izq'][3])
		self.frame_info.place(	relx=size_frame['down'][0], rely=size_frame['down'][1], 
								relwidth=size_frame['down'][2], relheight=size_frame['down'][3])

		self.but = Button(self.frame_command, command=self.generator).pack()

	def wirin(self):#se dibujan los gráficos
		fig = self.wirikan()
		self.graphy = FigureCanvasTkAgg(fig, master=self.frame_contenido)
		self.graphy.get_tk_widget().pack(side="top",fill='both',expand=True)

	def wirikan(self):

		fig = plt.figure(num="TUG", figsize=(3,3))
		t = np.arange(0, 3, .01)
		gs1 = GridSpec(9, 8)
		gs1.update(left=0.05, right=0.95, wspace=0.5, hspace=1, top=0.98, bottom=0.08)

		self.ax1 = plt.subplot(gs1[0:1,0:2])
		self.ax1.grid(GridTrue)
		self.ax1.set_xlim(0,1)
		self.ax1.set_ylim(0,3)
		self.ax1.set_yticks([1,2])
		self.ax1.set_xticks([0,1])
		self.ax1.xaxis.set_major_formatter(plt.NullFormatter()) 

		self.ax1.set_yticklabels(['D','I'],fontdict=fonticksmini,horizontalalignment='left')

		self.ax2 = plt.subplot(gs1[0:1, 3:8])
		self.ax2.grid(GridTrue)
		self.ax2.set_xlim(0,average)
		self.ax2.set_ylim(0,200)
		tiks_X = self.averageTick(average)
		self.ax2.set_yticks([0,40, 150, 200])
		self.ax2.set_xticks(tiks_X)
		self.ax2.set_yticklabels(['',40,'',200],fontdict=fonticksmini) 
		self.ax2.set_xticklabels([0,'','','','','','','','','','','','',average],fontdict=fonticksmini) 

		self.ax3 = plt.subplot(gs1[1:, 0:4])
		self.ax3.yaxis.set_major_formatter(plt.NullFormatter()) 
		self.ax3.grid(GridTrue, linestyle='--')
		self.ax3.set_xticks(np.arange(X_time+1))
		self.ax3.set_yticks(np.arange(Y_ampl+1))
		self.ax3.set_xlim(0,X_time)
		self.ax3.set_ylim(0,Y_ampl)


		self.ax4 = plt.subplot(gs1[1:, 4:8])
		self.ax4.yaxis.set_major_formatter(plt.NullFormatter()) 
		self.ax4.grid(GridTrue, linestyle='--')
		self.ax4.set_xlim(0,X_time)
		self.ax4.set_ylim(0,Y_ampl)
		self.ax4.set_yticks(np.arange(Y_ampl+1))
		self.ax4.set_xticks(np.arange(X_time+1))

		return fig

	def generator(self):
		size = 100
		x_vec = np.linspace(0,1,size+1)[:-1]
		y_vec = np.random.randn(len(x_vec))

		line1 = []
		for _ in range(30):
			y_vec = np.random.randn(len(x_vec))
			line1 = self.wirikan_2(x_vec,y_vec,line1)
			print(type(line1))



	def wirikan_2(x_vec,y1_data,line1,identifier='',pause_time=0.01):
		if line1==[]:
			plt.ion()
			#fig = plt.figure(figsize=(13,6))
			#ax = fig.add_subplot(111)
			#line1, = ax.plot(x_vec,y1_data)
			line1, = self.ax3.plot(x_vec,y1_data)

			plt.show()
			#self.graphy.draw()

		#line1.set_data(x_vec,y1_data)

		plt.pause(pause_time)

		return line1

	def averageTick(self,average):
		ticksAverage = average/13
		ticks =[0]
		ticks.extend(ticksAverage * i for i in range(1, 14))
		return ticks


if __name__ == '__main__':

    root = Tk()
    my_gui = Lelitxipawe(root)
    root.mainloop()