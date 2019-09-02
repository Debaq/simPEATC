def i18n(a,b):
	words={
		'nuevo':['Nuevo','New'],
		'registro':['Registro','Record'],
		'editar':['Editar','Edit'],
		'archivo':['Archivo','File'],
		'ayuda':['Ayuda', 'Help'],
		'intensidad':['Intensidad','Level'],
		'estimulo':['Tipo','Type'],
		'masking':['Enmascaramiento', 'Mask'],
		'tasa':['Tasa','Rate'],
		'polaridad':['Polaridad','Polarity'],
		'alternada':['Alternada', 'Alternated']
	}

	return words[a][b]

print(i18n('nuevo',0))


# print(words['nuevo'][1])
# values = words.values()
# i = 0
# for f in values:
# 	print(list(words.values())[i][1])
# 	i=i+1
