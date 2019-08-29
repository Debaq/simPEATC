
#!/usr/bin/env python
from tkinter import *
from PIL import ImageTk, Image
from functools import partial
import json
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np


class Window():

    def __init__(self, master=None):
        #Frame.__init__(self, master)   
        self.master = master
        self.master.update_idletasks()
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        geometry_X =  int(screen_width/2) - int(1280/2)
        geometry_Y = int(screen_height/2) - int(720/2)
        size="1280x720+"+str(geometry_X)+"+"+str(geometry_Y)
        self.master.geometry(size)
        self.master.minsize(1280, 720)
        self.master.call('wm', 'iconphoto', master._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))
        

        #self.event()
        self.init_window()

       
    def event(self):
        self.master.bind( "<Configure>", self.event_resize )

    def event_resize(self,event):
        print (event.width,event.height) ##imprime el tamaño de la pantalla
        self.screen_width=event.width ##iguala el el tamaño de la ventana al tamaño de la pantalla, ancho
        self.screen_height=event.height ##iguala el el tamaño de la ventana al tamaño de la pantalla, alto

    def init_window(self):


        self.master.title("simPEATC") ##Titulo de la ventana
        self.frame_name = Frame(bd=1, bg="blue",relief="sunken") ##crea la caja superior
        self.frame_contenido = Frame(bd=1, bg="green",relief="sunken") ##crea la caja central
        self.frame_info = Frame(bd=1, bg="red",relief="sunken") ##crea la caja inferior
        self.frame_command = Frame(bd=1, bg="black",relief="sunken") ##crea la caja inferior

        #split = 0.5
        self.frame_name.place(rely=0, relheight=.03, relwidth=1)
        self.frame_contenido.place(rely=.03, relx=.2, relheight=1.0-0.03, relwidth=.8)
        self.frame_command.place(rely=.03, relheight=1.0-0.03, relwidth=.2)

        self.frame_info.place(rely=1.0-0.03, relheight=.03, relwidth=1)


        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu, tearoff=0)
        file.add_command(label="Abrir usuario", command=self.open_user)
        file.add_command(label="Nuevo usuario", command=self.new_user)
        file.add_command(label="Cerrar usuario", command=self.client_exit)
        file.add_separator()
        file.add_command(label="Salir", command=self.client_exit)
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
        self.label_name = StringVar()
        label_name = Label(self.frame_name, textvariable=self.label_name, text="Label")
        label_name.pack(side = LEFT)
        
        self.graficar()

    def graficar(self):
    
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        
        fig.add_subplot(121).plot(t, 2 * np.sin(2 * np.pi * t),color="red")
        fig.add_subplot(122).plot(t, 2 * np.sin(2 * np.pi * t),color="blue")

        canvas = FigureCanvasTkAgg(fig, master=self.frame_contenido)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

    def open_user(self):
        self.window_newUser = Toplevel(self.master)
        self.window_newUser.title("Abrir Usuario")
        self.window_newUser.geometry("350x200")
        self.window_newUser.minsize(350, 200)
        self.window_newUser.resizable(0,0)
        self.window_newUser.tk.call('wm', 'iconphoto', self.window_newUser._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))

    def clicked(self):
        res ={
                "ID"        :   self.ID.get(),
                "Nombre"    :   self.name.get(),
                "Apellido"  :   self.lastName.get(),
                "Edad"      :   self.age.get(),
                "Altura"    :   self.height.get(),
                "Peso"      :   self.weight.get(),
                "Pruebas"   :   [None]
            }

        namefile=(res["ID"]+"_"+res["Nombre"]+"_"+res["Apellido"]+".profile")
        with open(namefile, 'w') as file:
            json.dump(res, file)
        self.label_name.set(self.name.get())

        self.window_newUser.destroy()



    def client_exit(self):
        exit()

    def new_user(self):
        self.ID=StringVar()
        self.name=StringVar()
        self.lastName=StringVar()
        self.age=StringVar()
        self.height=StringVar()
        self.weight=StringVar()
        self.window_newUser = Toplevel(self.master)
        self.window_newUser.title("Nuevo Usuario")
        self.window_newUser.geometry("350x200")
        self.window_newUser.minsize(350, 200)
        self.window_newUser.resizable(0,0)
        self.window_newUser.tk.call('wm', 'iconphoto', self.window_newUser._w, ImageTk.PhotoImage(Image.open('resources/icon.ico')))
        lbl_id = Label(self.window_newUser, text="ID").grid(column=0, row=0)
        id_entry = Entry(self.window_newUser,textvariable=self.ID, width=10).grid(column=1, row=0)
        lbl_name = Label(self.window_newUser, text="Nombre").grid(column=0, row=1)
        name = Entry(self.window_newUser,textvariable=self.name, width=10).grid(column=1, row=1)
        lbl_last_name = Label(self.window_newUser, text="Apellido").grid(column=0, row=2)
        last_name = Entry(self.window_newUser,textvariable=self.lastName, width=10).grid(column=1, row=2)
        lbl_age = Label(self.window_newUser, text="Edad").grid(column=0, row=3)
        age = Entry(self.window_newUser, textvariable=self.age,width=10).grid(column=1, row=3)
        lbl_height = Label(self.window_newUser, text="Altura").grid(column=0, row=4)
        height = Entry(self.window_newUser,textvariable=self.height,width=10).grid(column=1, row=4)
        path = 'resources/logo.png'
        img = ImageTk.PhotoImage(Image.open(path))
        panel = Label(self.window_newUser, image = img).grid(column=2, row=2, columnspan=2, rowspan=2)
        lbl_weight = Label(self.window_newUser, text="Peso").grid(column=0, row=5)
        weight = Entry(self.window_newUser,textvariable=self.weight,width=10).grid(column=1, row=5)
        btn1 = Button(self.window_newUser, text="Crear", command=self.clicked).grid(column=2, row=7)
        btn2 = Button(self.window_newUser, text="Cancelar", command=self.window_newUser.destroy).grid(column=3, row=7)
          





if __name__ == '__main__':
    root = Tk()
    app = Window(root)
    root.update()
    root.deiconify()
    root.mainloop()