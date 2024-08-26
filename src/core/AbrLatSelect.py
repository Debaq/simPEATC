
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from UI.Ui_ABR_lat_select import Ui_ABR_lat_select


class AbrLatSelect(QWidget, Ui_ABR_lat_select):
    data = Signal(dict)
    def __init__(self, side):
        QWidget.__init__(self)
        self.side = side
        self.setupUi(self)

        self.update_data({})
        self.configure_btn()
        self.flag_ab = "A"
        self.list_marks = { 'I':0,'Ip':0,'II':1,'IIp':1,
                            'III':2,'IIIp':2,'IV':3,'IVp':3,
                            'V':4,'Vp':4}


    def configure_btn(self):
        self.btn_AB.clicked.connect(self.toogle_AB)
        list_btn_waves = [i for i in dir(self) if i.startswith('btn_wave')]
        for i in list_btn_waves:
            getattr(self, i).clicked.connect(self.update_marks)

    def update_marks(self):
        widget = self.sender()
        name = widget.objectName()
        end = name.endswith('p')
        idx = 1 if end else 0
        _,_,name_wave = name.split('_')
        subidx = self.list_marks[name_wave]
        self.data.emit({'action':'update_mark', 
                        'data':{'prima': idx, 'n_curve':subidx,
                                'side':self.side, 'flag' : self.flag_ab}})
        
    def toogle_AB(self):
        widget = self.sender()
        text = widget.text()
        if text == "|A":
            text = "B|"
            new = "B"
        else:
            text = "|A"
            new = "A"
        widget.setText(text)
        self.flag_ab = new
        

    def update_data(self, data):
        
        if 'lat_A' in data:
            self.lbl_1.setText('A:{:.1f}ms B:{:.1f}ms'.format(data['lat_A'], data['lat_B']))
            self.lbl_2.setText('A-B:{:.2f}μV'.format(data['amp_AB']))
            self.lbl_3.setText('A<>B:{:.2f}ms'.format(data['lat_AB']))
        if 'non_prima' in data:
            self._extracted_from_update_data_8(data)

    # TODO Rename this here and in `update_data`
    def _extracted_from_update_data_8(self, data):
        self.lbl_4.setText("I:{:.1f}ms I':{:.1f}ms".format(data['non_prima'][0],data['prima'][0]))
        self.lbl_5.setText("II:{:.1f}ms II':{:.1f}ms".format(data['non_prima'][1],data['prima'][1]))
        self.lbl_6.setText("III:{:.1f}ms III':{:.1f}ms".format(data['non_prima'][2],data['prima'][2]))
        self.lbl_7.setText("IV:{:.1f}ms IV':{:.1f}ms".format(data['non_prima'][3],data['prima'][3]))
        self.lbl_8.setText("V:{:.1f}ms V':{:.1f}ms".format(data['non_prima'][4],data['prima'][4]))
        I_III = data['non_prima'][2]-data['non_prima'][0]
        III_V = data['non_prima'][4]-data['non_prima'][2]
        I_V = data['non_prima'][4]-data['non_prima'][0]
        self.lbl_9.setText("I-III:{:.1f}ms".format(I_III))
        self.lbl_10.setText("III-V:{:.1f}ms".format(III_V))
        self.lbl_11.setText("I-V:{:.1f}ms".format(I_V))
