from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QPushButton, QWidget
from UI.Ui_ABR_ctrl_graph import Ui_ABR_control_curve
from PySide6.QtGui import QFont


class AbrCtrlCurve(QWidget, Ui_ABR_control_curve):
    data = Signal(dict)
    def __init__(self, side):
        QWidget.__init__(self)
        self.contra_view = False
        self.side = side
        self.setupUi(self)
        self.config_btn()
        self.lbl_scale.setText('0.5')

    
    def config_btn(self):
        self.btn_up.clicked.connect(self.move_curve)
        self.btn_down.clicked.connect(self.move_curve)
        self.btn_del.clicked.connect(self.remove_curve)
        self.btn_scale_plus.clicked.connect(self.scale_graph)
        self.btn_scale_minus.clicked.connect(self.scale_graph)
        self.btn_contra.clicked.connect(self.contra_activate_toggle)
        
    
    def move_curve(self):
        widget = self.sender()
        _,direction = widget.objectName().split('_')
        self.data.emit({'action':'move', 
                        'data':{'direction': direction, 'side':self.side}})
    
    def scale_graph(self):
        widget = self.sender()
        _,_,direction = widget.objectName().split('_')
        self.scale_lbl_change(direction)
        self.data.emit({'action':'scale', 
                        'data':{'direction': direction, 'side':self.side}})
    
    def scale_lbl_change(self, direction):
        scale = float(self.lbl_scale.text())
        if direction == 'plus':
            scale *= 2
        else:
            scale = scale/2
        
        self.lbl_scale.setText(str(scale))
            
    def remove_curve(self):
        self.data.emit({'action':'remove', 
                        'data':{'side':self.side}})
        
    def contra_activate_toggle(self):
        self.contra_view = not self.contra_view
        self.data.emit({'action':'contra', 
                    'data':{'contra_view':self.contra_view}})
        
    def update_flag_curves(self, list_btns:list) -> None:
        for i in reversed(range( self.layout_curves.count())): 
            self.layout_curves.itemAt(i).widget().deleteLater()
        
        self.btns_flags_curves(list_btns)
        
    
    def btns_flags_curves(self, btns:list):
        color = "255,0,0" if self.side == 0 else "106,154,242"
        style =f"""
                    QWidget {'{'}
                    color: rgb(0, 0, 0);
                    background-color: rgb({color});
                    border-style: outset;
                    border-width: 0px;
                    {'}'}"""
        for btn_ in btns:
            btn = QPushButton(f'{btn_[0]}')
            btn.setObjectName(btn_[1])
            btn.setStyleSheet(style)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(self.selected_curve)
            btn.setMaximumSize(30,30)
            font = QFont('Times', 7)
            btn.setFont(font)
            btn.setToolTip(f'{btn_[2]}')
            btn.setChecked(True)
            self.layout_curves.addWidget(btn)
        
    def selected_curve(self):
        widget = self.sender()
        curve = widget.objectName()
        self.data.emit({'action':'selected', 
                        'data':{'curve': curve}})
