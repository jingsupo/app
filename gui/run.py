import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiSubWindow, QTextEdit
from mdi import Ui_MainWindow


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.count = 0

    def menubar_action(self, q):
        type = q.text()
        print("Triggered : %s" % type)
        if type == "层叠":
            self.mdiArea.cascadeSubWindows()
        elif type == "平铺":
            self.mdiArea.tileSubWindows()
        elif type == "关闭全部":
            self.mdiArea.closeAllSubWindows()

    def toolbar_action(self, q):
        type = q.text()
        print("Triggered : %s" % type)
        if type == "新建窗口":
            # 子窗口增加一个
            self.count += 1
            # 实例化多文档界面对象
            sub = QMdiSubWindow()
            # 向sub内部添加控件
            sub.setWidget(QTextEdit())
            sub.setWindowTitle("subWindow %d" % self.count)
            self.mdiArea.addSubWindow(sub)
            sub.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec())
    # app.exec()