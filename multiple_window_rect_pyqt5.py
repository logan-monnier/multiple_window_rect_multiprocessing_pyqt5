import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsRectItem
import multiprocessing


class Fenetre1(QWidget):
    def __init__(self, conn_principale, conn_fenetre1):
        super().__init__()

        self.conn_principale = conn_principale
        self.conn_fenetre1 = conn_fenetre1

        self.square_size = 50
        self.x_pos = 50
        self.y_pos = 50
        self.direction = [0,0,0,0]
        self.speed = 5

        self.initUI()
        
        self.win_pos = self.pos()
        
        # Création d'un timer pour le rafraîchissement continu
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(16)  # Rafraîchit toutes les 16 millisecondes (environ 60 FPS)

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('fenetre 2')
        self.show()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self.direction[0] = 1
        elif key == Qt.Key_Right:
            self.direction[1] = 1
        elif key == Qt.Key_Up:
            self.direction[2] = 1
        elif key == Qt.Key_Down:
            self.direction[3] = 1

    def keyReleaseEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self.direction[0] = 0
        elif key == Qt.Key_Right:
            self.direction[1] = 0
        elif key == Qt.Key_Up:
            self.direction[2] = 0
        elif key == Qt.Key_Down:
            self.direction[3] = 0

    def timerEvent(self):
        # Met à jour la position du carré périodiquement
        self.x_pos += (self.direction[1]-self.direction[0])*self.speed
        self.y_pos += (self.direction[3]-self.direction[2])*self.speed
        if 1 in self.direction:
            self.conn_principale.send((self.x_pos, self.y_pos))
        # Récupérer les coordonnées depuis la fenêtre principale
        if conn_fenetre1.poll():
            self.x_pos, self.y_pos = conn_fenetre1.recv()

        self.win_pos = self.pos()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawSquare(painter)
        
    def drawSquare(self, painter):
        painter.drawRect(self.x_pos-self.win_pos.x(), self.y_pos-self.win_pos.y(), self.square_size, self.square_size)

class FenetrePrincipale(QWidget):
    def __init__(self, conn_principale, conn_fenetre1):
        super().__init__()

        self.conn_principale = conn_principale
        self.conn_fenetre1 = conn_fenetre1

        self.square_size = 50
        self.x_pos = 50
        self.y_pos = 50
        self.direction = [0,0,0,0]
        self.speed = 5

        self.initUI()

        self.win_pos = self.pos()

        # Création d'un timer pour le rafraîchissement continu
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(16)  # Rafraîchit toutes les 16 millisecondes (environ 60 FPS)

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('fenetre 1')
        self.show()

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self.direction[0] = 1
        elif key == Qt.Key_Right:
            self.direction[1] = 1
        elif key == Qt.Key_Up:
            self.direction[2] = 1
        elif key == Qt.Key_Down:
            self.direction[3] = 1

    def keyReleaseEvent(self, event):
        key = event.key()

        if key == Qt.Key_Left:
            self.direction[0] = 0
        elif key == Qt.Key_Right:
            self.direction[1] = 0
        elif key == Qt.Key_Up:
            self.direction[2] = 0
        elif key == Qt.Key_Down:
            self.direction[3] = 0

    def timerEvent(self):
        # Met à jour la position du carré périodiquement
        self.x_pos += (self.direction[1]-self.direction[0])*self.speed
        self.y_pos += (self.direction[3]-self.direction[2])*self.speed
        if 1 in self.direction:
            self.conn_fenetre1.send((self.x_pos, self.y_pos))
                
        if conn_principale.poll():
            self.x_pos, self.y_pos = conn_principale.recv()
            
        self.win_pos = self.pos()
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawSquare(painter)
        
    def drawSquare(self, painter):
        painter.drawRect(self.x_pos-self.win_pos.x(), self.y_pos-self.win_pos.y(), self.square_size, self.square_size)

    def mousePressEvent(self, event):
        # Appelé lorsque le bouton de la souris est enfoncé
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        # Appelé lorsque la souris est déplacée
        if hasattr(self, 'drag_start_position'):
            delta = event.pos() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.pos()
            QCoreApplication.processEvents()

    def mouseReleaseEvent(self, event):
        # Appelé lorsque le bouton de la souris est relâché
        if hasattr(self, 'drag_start_position'):
            del self.drag_start_position

if __name__ == '__main__':
    app = QApplication(sys.argv)

    conn_principale, parent_conn_principale = multiprocessing.Pipe()
    conn_fenetre1, parent_conn_fenetre1 = multiprocessing.Pipe()

    fenetre1 = Fenetre1(parent_conn_principale, parent_conn_fenetre1)
    fenetre_principale = FenetrePrincipale(parent_conn_principale, parent_conn_fenetre1)

    sys.exit(app.exec_())
