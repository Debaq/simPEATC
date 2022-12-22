from PIL import Image
from fpdf import FPDF
from base import context



def dataset(data):
    data_c = [("Curva", "Estimulo", "Polaridad", "Intencidad", "Masking","Tasa", "Filtros","Promediaciones", "I", "III", "V", "I-III", "III-V", "I-V")]
    for i in data:
        view = data[i]["view"]
        if view:
            stim = data[i]["stim"]
            pol = data[i]["pol"]
            intencity = f"{data[i]['intencity']} dBnHl"
            mkg = f"{data[i]['mkg']} dBnHl"
            rate =f"{data[i]['rate']} est./seg."
            fil = f"{data[i]['intencity']} Hz."
            prom = str(data[i]["prom"])
            I = round(data[i]["marks"][0],2)
            III = round(data[i]["marks"][2],2)
            V = round(data[i]["marks"][4],2)
            I_III = round(III - I,2)
            I_V = round(V - I,2)
            III_V = round(V - III,2)
            new_line = (i,stim,pol,intencity,mkg,rate,fil,prom,f"{I}ms.",f"{III}ms.",f"{V}ms.", f"{I_III}ms.", f"{III_V}ms.", f"{I_V}ms.")
            data_c.append(new_line)
    return data_c

def image_ABR():
    image_od = Image.open(context.get_resource("image_0.png"))
    image_oi = Image.open(context.get_resource("image_1.png"))
    image1_size = image_od.size
    image2_size = image_oi.size
    new_image = Image.new('RGB',(2*image1_size[0], image1_size[1]), (250,250,250))
    new_image.paste(image_od,(0,0))
    new_image.paste(image_oi,(image1_size[0],0))
    new_image.save(context.get_resource("merged_image.jpg"),"JPEG")
    
    
def create_pdf(table, n):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    pdf.cell(200, 10, txt = "POTENCIALES EVOCADOS AUDITIVOS DE TRONCO CEREBRAL (PEATC)", ln = 1, align = 'C')
    text = f"caso: {n}"
    pdf.cell(200, 10, txt = text, ln = 1, align = 'C')

    pdf.image(context.get_resource("merged_image.jpg"), 15, 35, 180)
    pdf.ln(100)

    # Setting font: Times 12
    pdf.set_font("Times", size=7)
    # Printing justified text:

    line_height = pdf.font_size * 2.5
    col_width = pdf.epw / 14 # distribute content evenly
    for row in table:
        for datum in range(len(row)):
            if datum > 7:
                col_width = 10
            elif datum in [7, 5]:
                col_width = 20
            else:
                col_width = pdf.epw /14
            pdf.multi_cell(col_width, line_height, row[datum], border=1,
                    new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)


    # Performing a line break:
    pdf.ln()



    pdf.output(context.get_resource("GFG.pdf"))