from fpdf import FPDF
import re

class PDFCreator(FPDF):
    def __init__(self, title, html1, html2, images=None, image_lat=None,data_dict=None, output= None):
        super().__init__()
        self.title = title
        self.image_lat= image_lat
        self.html1 = self.remove_style_tag(html1)
        self.html2 = self.remove_style_tag(html2)
        self.images_ = images
        self.data_dict = data_dict
        self.output_ = output
        self.create_pdf()

    def remove_style_tag(self, text):
        # Expresión regular para encontrar y eliminar la etiqueta <style> y su contenido
        pattern = r'<style.*?>.*?</style>'
        # Reemplazar la etiqueta y su contenido por una cadena vacía
        modified_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return modified_text

    def header(self):
        self.set_font('helvetica', 'B', 12)
        #self.cell(w=0, h=10, text=self.title, border=0, align='C')
        self.write_html("<center>Potencial Evocado de tronco Cerebral</center>")
        self.write_html("<center>(PEATC)</center>")

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(w=0, h=10, text='Página %s' % self.page_no(), border=0, align='C')

    def add_html_content(self, html):
        self.write_html(html)

    def add_table(self, data_dict=None):
        data_table = []
        keys = list(data_dict.keys())
        for i in range(len(data_dict)):
            data = self.transform_dict({keys[i] : data_dict[keys[i]]}, i)
            if len(data) <= 2:
                data_table.append(data[0])
                data_table.append(data[1])
            else:
                data_table.append(data)
        col_widths = (35,30,50,50,40,30,40,80,50,50,50,50,50,25,28,25,25)
        self.set_font("helvetica", size=6)
        with self.table(col_widths=col_widths) as table:
            for data_row in data_table:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

    def add_images(self):
        self.set_auto_page_break(auto=1, margin=1)  # 1 cm margin for auto page break
        self.set_margins(10, 10, 10)  # Set margins to 1 cm on each side
        image = self.image(self.images_[0], x=10, y=self.get_y(), w=(self.epw / 2) - 5)
        self.image(self.images_[1], x=(self.epw / 2) + 5, y=self.get_y(), w=(self.epw / 2) - 5)
        #self.set_y(image.height)
    
    def add_image(self):
        self.set_margins(10, 10, 10)  # Set margins to 1 cm on each side
        self.image(self.image_lat, x=10, y=30, w=self.epw-30)

    def transform_dict(self, data, n):
        headers = ('Curva', 'Lado', 'Estimulo', 'Polaridad', 'int(mkg)', 'Tasa', 'Filtros',
                'Promediaciones', 'I:lat(amp)', 'II:lat(amp)', 'III:lat(amp)', 'IV:lat(amp)', 
                'V:lat(amp)', 'I-III', 'III-V', 'I-V', 'V/I')

        # Asumiendo que solo hay una clave en el nivel superior del diccionario.
        curve_key = next(iter(data))
        curve_data = data[curve_key]

        values = [
            curve_key,
            curve_data['side'],
            curve_data['stim'],
            curve_data['pol'],
            f"{curve_data['int']}({curve_data['mkg']})",
            str(curve_data['rate']),
            f"{curve_data['filter_passhigh']}-{curve_data['filter_down']}",
            str(curve_data['average']),
        ]

        # Añadir los datos de LatAmp
        for i in ['I', 'II', 'III', 'IV', 'V']:
            lat_amp = curve_data['LatAmp'].get(i, [None, None])
            values.append(f"{round(lat_amp[0],2)}({round(lat_amp[1],2)})" if lat_amp[0] is not None and lat_amp[1] is not None else "")

        i_iii = round(curve_data['LatAmp']['III'][0] - curve_data['LatAmp']['I'][0],2) if curve_data['LatAmp']['III'][0] is not None and curve_data['LatAmp']['I'][0] is not None else ""
        iii_v = round(curve_data['LatAmp']['V'][0] - curve_data['LatAmp']['III'][0],2) if curve_data['LatAmp']['V'][0] is not None and curve_data['LatAmp']['III'][0] is not None else ""
        i_v = round(curve_data['LatAmp']['V'][0] - curve_data['LatAmp']['I'][0],2) if curve_data['LatAmp']['V'][0] is not None and curve_data['LatAmp']['I'][0] is not None else ""
        vi = round(curve_data['LatAmp']['V'][1] / curve_data['LatAmp']['I'][1],2) if curve_data['LatAmp']['V'][1] is not None and curve_data['LatAmp']['I'][1] is not None else ""
        # Añadir los datos de Interpeak
        for peak in [i_iii, iii_v, i_v]:
            values.append(str(peak))

        # Añadir la relación V/I
        values.append(str(vi))
        if n == 0:
            return headers, values
        else:
            return values

    

    def create_pdf(self):
        
        # Add first page with HTML content
        self.add_page()
        self.set_y(30)
        self.add_html_content(self.html1)
        delta = self.get_y() - 30
        self.add_images()
        self.set_y(130 + delta)
        self.add_html_content(self.html2)
        self.add_page()
        #self.add_images()
        self.add_image()
        self.set_y(150)
        self.add_table(self.data_dict)
        self.output(self.output_)
  

