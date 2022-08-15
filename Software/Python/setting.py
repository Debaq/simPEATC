
import csv

def i18n():
	file = open('translation.csv','r')
	reader = csv.reader(f)
	people = {row[0]: {'value':row[1],'value2':row[2]} for row in reader}
	print(people)

def tres_simple(a,b,tipo=None):
	d=b*100
	d=d/a
	p=tipo
	if p is None:
		return d/100
	if(p=="invert"):
		return 1-(d/100)


def size_screen(w,h):
	
	'''proporciones de los frames principales 
	[relx,rely,relwidth,relheight,width,height]
	'''

	size_frame = {'up':[0,0,1,.045], 'down':[0,0,1,.03],
	             'izq':[0,0,.19,0,200],'der':[0,0,0,0]}

	size_center = 1-(size_frame['up'][3]+size_frame['down'][3])
	size_frame['izq'][3]=size_center
	size_frame['der'][3]=size_center
	size_frame['der'][2]=1-size_frame['izq'][2]

	size_frame['down'][1]=round(size_frame['up'][3]+size_center,3)
	size_frame['izq'][1]=size_frame['up'][3]
	size_frame['der'][1]=size_frame['up'][3]
	size_frame['der'][0]=size_frame['izq'][2]

	#Calcular el ancho en pixeles[4] y porcentaje[2]
	if(w>=size_frame['izq'][4]):
		size_frame['der'][2]=tres_simple(w,size_frame['izq'][4],tipo="invert")
		size_frame['izq'][2]=tres_simple(w,size_frame['izq'][4])
		size_frame['der'][0]=size_frame['izq'][2]

	return size_frame

