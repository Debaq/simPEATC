import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.animation as animation
from matplotlib.text import OffsetFrom
import numpy as np
import csv
a = []
b = []

with open('curvatest.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        a.append(float(row[0])/10)
        b.append(float(row[1])/10)
        print(a)

t = np.linspace(1, 12, 26)
out_a= np.asarray(b)
out_b= np.asarray(a)
x_watts = out_a ** 2
target_noise_db = 30





prom=0
text=r"80 OI "
c_red=[1.0,0.5,0.5]
c_blue=[0.5,0.5,1.0]
color=c_blue
fig, ax = plt.subplots(figsize=(3, 3))
el = Ellipse((2, -1), 0.5, 0.5)
ax.add_patch(el)


for i in range(10):
	plt.title('PEATC')
	plt.ylabel('Amplitud (uV)')
	plt.xlabel('Tiempo (ms)')
	#plt.yticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
	#plt.axis([0,12,0,18])
	ax.grid(True)
	target_noise_db = target_noise_db - 1
	target_noise_watts = 10 ** (target_noise_db / 10)
	mean_noise = 0
	noise_volts = np.random.normal(mean_noise, np.sqrt(target_noise_watts), len(x_watts))
	y_volts = out_a + noise_volts
	ytext=y_volts[0]
	xtext=out_b[0]
	prom=prom+1
	line, = ax.plot(out_b, y_volts)
	ann = ax.annotate(text,
                  xy=(xtext,ytext), xycoords='data',
                  xytext=(8, 0), textcoords='offset points',
                  size=30, va="center",
                  bbox=dict(boxstyle="round", fc=(color), ec="none"),
                  arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                  fc=(color), ec="none",
                                  patchA=None,
                                  patchB=el,
                                  relpos=(0.2, 0.5)))




	#ax.text(right, top, 'right bottom',
     #   horizontalalignment='right',
      #  verticalalignment='bottom',
       # transform=ax.transAxes)

	plt.pause(0.2)
	plt.cla()

print("ok")
plt.show()

