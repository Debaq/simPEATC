
import pandas as pd

def i18n():
	file = open('translation.csv','r')
	reader = csv.reader(file)
	people = {}
	for row in reader:
		people[row[0]]={'value':row[1],'value2':row[2]}
	print(people)


def get():
	df = pd.read_csv('setting.csv')
	saved_column = df['conf']
	font=[]
	font=df.iloc[:,0]
	print(font)



#proporciones de los frames principales [height,with,x,y]

size_window=[0,1280,720]
size_window[0]=str(size_window[1])+'x'+str(size_window[2])

size_frame={'up':[1,.045,0,0], 'down':[1,.03,0,0],
            'izq':[.19,0,0,0,0,240],'der':[0,0,0,0]}
size_frame['der'][1]=(1-(size_frame['up'][1]+size_frame['down'][1]))
size_frame['izq'][1]=(size_frame['der'][1])
size_frame['der'][0]=(1-(size_frame['izq'][0]))
size_frame['down'][3]=(size_frame['der'][1]+size_frame['up'][1])

get()