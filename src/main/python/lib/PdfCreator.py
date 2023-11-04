from fpdf import FPDF, HTMLMixin

class PDFCreator(FPDF, HTMLMixin):
    def __init__(self, title, html1, html2, images, data_dict):
        super().__init__()
        self.title = title
        self.html1 = html1
        self.html2 = html2
        self.images = images
        self.data_dict = data_dict
        self.create_pdf()

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.title, 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página %s' % self.page_no(), 0, 0, 'C')

    def add_html_content(self, html):
        self.write_html(html)

    def add_images(self):
        self.add_page()
        self.set_auto_page_break(auto=1, margin=1)  # 1 cm margin for auto page break
        self.set_margins(10, 10, 10)  # Set margins to 1 cm on each side
        self.image(self.images[0], x=10, y=self.get_y(), w=(self.epw / 2) - 5)
        self.image(self.images[1], x=(self.epw / 2) + 5, y=self.get_y(), w=(self.epw / 2) - 5)

    def add_table(self):
        self.add_page()
        for label, content in self.data_dict.items():
            self.add_table_section(label, content)

    def add_table_section(self, label, content):
        # Implementation of add_table_section similar to the previous example
        # ...

    def create_pdf(self):
        # Add first page with HTML content
        self.add_page()
        self.add_html_content(self.html1)
        self.add_html_content(self.html2)

        # Add second page with images
        self.add_images()

        # Add third page with table
        self.add_table()

# Uso de la clase PDFCreator
pdf = PDFCreator(
    title="Mi Título",
    html1="<h1>Encabezado HTML 1</h1><p>Parágrafo 1...</p>",
    html2="<h1>Encabezado HTML 2</h1><p>Parágrafo 2...</p>",
    images=["path_to_image1.png", "path_to_image2.png"],
    data_dict={
        # ... tu diccionario de datos ...
    }
)
pdf.output("report.pdf")
