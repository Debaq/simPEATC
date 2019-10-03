<h1 align="center">

<img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/logo.png" alt="simPEATC" width="256"/>
<br/>
</h1>

<div align="center">

[![Universidad Austral PM](https://img.shields.io/badge/UACH-PM-green.svg)](http://www.pmontt.uach.cl/)
[![TecMed](https://img.shields.io/badge/TM-PM-critical.svg)](http://tmedicapm.uach.cl/)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=flat&logo=twitter)](https://twitter.com/intent/tweet?hashtags=imagesharp,dotnet,oss&text=simPEATC.Un+simulador+de+potenciales+evocados+auditivos+de+tronco+cerebral+en+Python+https://github.com/debaq/simPEATC+#simPEATC+#simulador+#UACH+#TM-PM)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)


</div>


### simPEATC, Simulador de Potenciales Evocados de Tronco Cerebral.

simPEATC, es un proyecto de simulador de PEATC, para estudiantes de electrofisiología auditiva, en el cual se intenta recrear el procedimineto completo


### Estado actual del proyecto

* **[:speak_no_evil:]GUI**
* **[:speak_no_evil:]Insertar Matplotlib seteado**
* **[:construction_worker:]i18n**
* **[:rat:]Configuración de tonos**
* **[:speak_no_evil:]Desarrollo del Hadware**


:ok::OK, :speak_no_evil::50/50, :construction_worker::en construcción, :rat:: nivel rata(no funciona, ¡aún!)

### Avances:

<p><strong>&nbsp;02-10-2019:<br /></strong></p>

<p style="text-align: justify;">- Se agregan stickers para preamplificador y portaelectrodos en formato SVG de Inkscaper</p>
<p style="text-align: justify;">- Se modifica orden de las carpetas y archivos para una mejor interpretación</p>
<p style="text-align: justify;">- Se comienzan a crear los archivos FZZ de fritzing para mostrar de forma sencilla los cirtuitos internos del preamplificador y portaelectrodos</p>


<p style="text-align: justify;">&nbsp;</p>
<p align="center">
<table>
	<tbody>
		<tr>
			<td style="width: 263px;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Hardware/img/Stickers_preamplificador_portaelectrodos.jpeg" alt="Stickers" width="263" height="230" /></td>
			<td style="width: 263px;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Hardware/img/Preamplificador_electronica_1.png" alt="Electronica" width="263" height="230" /></td>
		</tr>
		<tr>
			<td style="width: 263px;">Stickers</td>
			<td style="width: 263px;">Fritzing -  Preamplificador</td>
		</tr>
	</tbody>
</table>
</p>

<p>&nbsp;</p>
<p><strong>&nbsp;01-10-2019:<br /></strong></p>
<p style="text-align: justify;">- Se agregan formatos STL, para impresi&oacute;n en 3d del preamplificador y portaelectros (carpeta STL): Se construyo el porta electrodos para poder fabricar electrodos con pin dupont de 1 pin</p>
<p style="text-align: justify;">&nbsp;</p>
<p align="center">
<table>
<tbody>
<tr>
<td style="width: 252px; text-align: center;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Hardware/img/portaelectrodo1.jpg" alt="Porta Electrodos" width="252" height="189" /></td>
<td style="width: 236px;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Hardware/img/preamplificador.jpg" alt="Preamplificador" width="236" height="177" /></td>
<td style="width: 263px;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Hardware/img/3d_preamplificador_portaelectrodos.jpeg" alt="impresi&oacute;n3d" width="263" height="230" /></td>

</tr>

<tr>
<td style="width: 252px;">porta electrodos</td>
<td style="width: 236px;">preamplificador</td>
<td style="width: 263px;">impresi&oacute;n 3d</td>
</tr>
</tbody>
</table>
</p>
<p style="text-align: justify;">&nbsp;</p>
<p style="text-align: justify;">&nbsp;</p>
<p style="text-align: justify;"><strong>08-09-2019:</strong></p>
<p style="text-align: justify;">- Se consigue generar animaci&oacute;n de la formaci&oacute;n de los potenciales evocados dentro de la gui.</p>
<p style="text-align: justify;"><em>bugs:</em> el sistema queda en un bucle de matplotlib impidiendo realizar acciones mientras se genera el potencial</p>
<p style="text-align: justify;">&nbsp;</p>
<p align="center">
<img width="505" height="284" src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/video.gif" alt="Video generaci&oacute;n de curva"  /></p>
<p style="text-align: justify;">&nbsp;</p>
<p style="text-align: justify;"><strong>02-09-2019:</strong></p>
<p style="text-align: justify;">- Se realiza gui completa de la pantalla principal</p>
<p align="center">
<img width="505" height="306" src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/Screenshot1.png" alt="Gui principal completo"  /></p>

### Pre-requisitos
_Para correr este script de Python es necesario tener instalado:_

```
Python 3.x
Matplotplib 
Tkinter
PIL
Numpy
csv
```

### Paquetes de instalación
|           |Paquete|Código|
|-----------|-------|------|
|**Linux**  |[![Build Status](https://img.shields.io/badge/build-faling-critical.svg)](https://github.com/Debaq/simPEATC)|[![Build Status](https://img.shields.io/badge/code-10-green.svg)](https://github.com/Debaq/simPEATC)|
|**windows**|[![Build Status](https://img.shields.io/badge/build-faling-critical.svg)](https://github.com/Debaq/simPEATC)|[![Build Status](https://img.shields.io/badge/code-0-red.svg)](https://github.com/Debaq/simPEATC)|


### Construido con 🛠️

_Este proyecto se ha desarrollado con las siguientes herramenientas_

* [Python](https://www.python.org/) 
* [Tkinter](https://docs.python.org/2/library/tkinter.html) 
* [Matplotlib](https://matplotlib.org/) 



### Autores ✒️


##Investigador Principal:
<table>
	<tbody>
		<tr>
			<td style="width: 263px; border: 10px solid black;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/Autores/Ávila.jpg" alt="Davila" width="100" height="100" /></td>		
			<td style="width: 263px;">
				David Ávila Quezada
			<a href="http://tmedicapm.uach.cl/docentes/david-%C3%A1vila-quezada">Davila</a>
			</td>
		</tr>
	</tbody>
</table>

##Investigadores Asociados:
<table>
	<tbody>
		<tr>
		<td style="width: 263px; border: 10px solid black;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/Autores/Latorre.jpg" alt="Latorre" width="100" height="100" /></td>	
		<td style="width: 263px; border: 10px solid black;"><img src="https://raw.githubusercontent.com/Debaq/simPEATC/master/Images/Autores/Inarejo.jpg" alt="Inarejo" width="100" height="100" /></td>
		</tr>
		<tr>
		<td style="width: 263px;">
		Maria Paz Latorre Gonzalez
		<a href="mailto:Marialatorre.1f@gmail.com">Email</a>
	</tr>
		</tr>
	</tbody>
</table>
* **Ignacia Inarejo Inarejo** - *Casos* - 

### Licencia 📄

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE.md](LICENSE.md) para detalles

### Agradecimientos 🎁

* Escuela de Tecnología Médica Universidad Austral de Chile - Sede Puerto Montt -  [TM-PM](http://tmedicapm.uach.cl/)


