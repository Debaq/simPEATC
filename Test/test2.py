icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste', 'undo', 'redo', 'find_text')
for i, icon in enumerate(icons):
tool_bar_icon = PhotoImage(file='icons/{}.gif'.format(icon))
cmd = eval(icon)
tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=cmd)
tool_bar.image = tool_bar_icon
tool_bar.pack(side='left')



width = 50
height = 50
img = Image.open("dir.png")
img = img.resize((width,height), Image.ANTIALIAS)
photoImg =  ImageTk.PhotoImage(img)
b = Button(master,image=photoImg, command=callback, width=50)
b.pack()
mainloop()




logo = PhotoImage(file = 'mine32.gif')
small_logo = logo.subsample(5, 5)
self.b.config(image = small_logo , compound = LEFT )



samples = StringVar()

a = ttk.Combobox(root,textvariable=samples)

a['values']=['San Salvador','La Union','San Marcos','El Puerto']
a.current(0)
a.grid(row=0,column=0)
