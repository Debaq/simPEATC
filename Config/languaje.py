def i18n(a,b,*f):
	words={
		'new':['nuevo','new'],
		'record':['Registro','Record'],
		'edit':['Editar','Edit'],
		'file':['Archivo','File'],
		'help':['Ayuda', 'Help'],
		'level':['Intensidad','Level'],
		'type':['Tipo','Type'],
		'mark':['Enmascaramiento', 'Mask'],
		'rate':['Tasa','Rate'],
		'polarity':['Polaridad','Polarity'],
		'alt':['Alternada', 'Alternated']
	}
	if f:
		return words[a][b].capitalize()
	else:
		return words[a][b].lower()


