from tkinter import Tk, Frame, BOTH
from tkinter import ttk
from PIL import ImageTk, Image
import setting as stt

##Lenguaje
def i18n(a,b,*f):
    i18n = lang.i18n(a,b)
    return i18n
    
class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
        self.parent = parent        
        self.pack(fill=BOTH, expand=1)




def main():

# Se inicia la ventana
    root = Tk()
    root.config(background='white')
    root.geometry(stt.size_window[0])#Tamaño inicial de la ventana
    root.update_idletasks()
    root.minsize(stt.size_window[1], stt.size_window[2])#Tamaño minimo de la ventana
    root.call('wm', 'iconphoto', root._w, ImageTk.PhotoImage(Image.open('../resources/icon.ico')))#Icono de la ventana
    root.title("simPEATC") ##Titulo de la ventana

    app = Example(root)
    root.mainloop()  

if __name__ == '__main__':
    main()