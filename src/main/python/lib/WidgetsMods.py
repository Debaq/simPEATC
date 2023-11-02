
from functools import partial

from pyqtgraph import (GraphicsLayoutWidget, InfiniteLine, InfLineLabel,
                       TextItem)
from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import QGraphicsLayoutItem, QMenu, QPushButton


class TextItemMod(TextItem):
    sigDragged = Signal(dict)
    sigPositionChangeFinished = Signal(object)
    sigPositionChangeStarted= Signal(str)

    def __init__(self,name:str, tipo:str, curve_parent:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moving = False
        self.name = name
        self.tipo = tipo
        self.curve_parent = curve_parent

    def mouseDragEvent(self, ev):
        if self.tipo != 'mark':
            if ev.button() == Qt.MouseButton.LeftButton:
                if ev.isStart():
                    self.moving = True
                    self.cursorOffset = self.pos() - self.mapToParent(ev.buttonDownPos())
                    self.startPosition = self.pos()
                    self.pos_x = self.pos().x()
                    self.sigPositionChangeStarted.emit(self.name)
                ev.accept()
                
                if not self.moving:
                    return
                pos = self.cursorOffset + self.mapToParent(ev.pos())
                
                self.setPos(self.pos_x, pos.y())
                list_pos = {"pos":(self.pos_x, pos.y()),"name":self.name}
                self.sigDragged.emit(list_pos)

                if ev.isFinish():
                    self.moving = False
                    self.sigPositionChangeFinished.emit(self)
        
    def mouseDoubleClickEvent(self, ev):
        if self.tipo != 'mark':
            self.sigPositionChangeStarted.emit(self.name)




class InfiniteLineMod(InfiniteLine):

    def __init__(self, lbl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #if self.label:
        #    self.label.scene().removeItem(self.label) # Esto elimina el label de la escena
        self.label = None
        
        # Crea el label modificado
        labelopt = kwargs['labelOpts']
        self.label = InfiniteLineLabelMod(self, text=lbl, **labelopt)

class InfiniteLineLabelMod(InfLineLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_line = self.line.getPos()

    def mouseDragEvent(self, ev):
        super().mouseDragEvent(ev)
        pos = ev.pos()
        pos = self.mapToItem(self, pos)
        prev_pos = self.line.getXPos()
        new_pos = prev_pos + pos.x()/60
        self.line.setPos([new_pos,0])


class GraphicsLayoutWidgetMod(GraphicsLayoutWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def contextMenuEvent(self, event):
        # Crea el menú contextual
        contextMenu = QMenu(self)

        # Añade acciones al menú
        delete = contextMenu.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Eliminar curva"))
        delete_mark = contextMenu.addMenu(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Eliminar marcas"))
        
        # Añade submenús a 'delete_mark'
        mark_i = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Curva I"))
        mark_ii = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Curva II"))
        mark_iii = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Curva III"))
        mark_iv = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Curva IV"))
        mark_v = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Curva V"))
        mark_all = delete_mark.addAction(QCoreApplication.translate("GraphicsLayoutWidgetMod", "Eliminar todas"))

        mark_i.triggered.connect(partial(self.delete_mark, 'Curva I'))
        mark_ii.triggered.connect(partial(self.delete_mark, 'Curva II'))
        mark_iii.triggered.connect(partial(self.delete_mark, 'Curva III'))
        mark_iv.triggered.connect(partial(self.delete_mark, 'Curva IV'))
        mark_v.triggered.connect(partial(self.delete_mark, 'Curva V'))
        mark_all.triggered.connect(self.delete_all_marks)


        # Muestra el menú en la posición del cursor
        action = contextMenu.exec_(event.globalPos())

        # Realiza alguna acción basada en la selección del usuario
        if action == delete:
            self.delete_curve()
       
    def delete_all_marks(self):
        pass
    def delete_curve(self):
        pass

    def delete_mark(self):
        pass
    

    def disable_wheel_event(ev):
        pass

    def wheelEvent(self, ev, axis=None):
        pass