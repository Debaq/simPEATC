from pylive import live_plotter
import numpy as np

size = 100
x_vec = np.linspace(0,1,size+1)[0:-1]
y_vec = np.random.randn(len(x_vec))

line1 = []
a = 0
while (a<30):
    a =a+1
    y_vec = np.random.randn(len(x_vec))

    #rand_val = np.random.randn(1)
    #print(rand_val,y_vec[-2])
    #y_vec[-1] = rand_val
    line1 = live_plotter(x_vec,y_vec,line1)
    print(type(line1))
#    y_vec = np.append(y_vec[1:],0.0)
