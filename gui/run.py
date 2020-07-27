import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pandas import read_csv, Series
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QMdiSubWindow, QTextEdit, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
from mdi import Ui_MainWindow
from constant import point_description
from spectrum import *

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.count = 0
        self.data = None

    def menubar_action(self, q):
        type = q.text()
        print("Triggered : %s" % type)
        if type == "层叠":
            self.mdiArea.cascadeSubWindows()
        elif type == "平铺":
            self.mdiArea.tileSubWindows()
        elif type == "关闭全部":
            self.mdiArea.closeAllSubWindows()
        elif type == "设置":
            QMessageBox.information(self, "❤", "芳芳，我爱你！（づ￣3￣）づ╭❤～")
        elif type == "关于":
            QMessageBox.information(self, "关于", "爱你的车车")

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
        elif type == "新建九宫格":
            pictures = ['C:\\Users\\Admin\\Pictures\\pictures\\0' + str(i) + '.png' for i in range(1, 10)]
            for p in pictures:
                sub = QMdiSubWindow()
                # 创建一个QLabel，用来显示图片
                label = QLabel(sub)
                label.setGeometry(QRect(40, 40, 572, 857))
                png = QPixmap(p)
                label.setPixmap(png)
                label.setScaledContents(True)
                # 子窗口增加一个
                self.count += 1
                sub.setWindowTitle("subWindow %d" % self.count)
                self.mdiArea.addSubWindow(sub)
                sub.show()
            self.mdiArea.tileSubWindows()

    def choose_file(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                    "选取文件",
                                    "",  # 起始路径
                                    "All Files (*);;CSV Files (*.csv)")  # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            print("\n取消选择")
            return

        print("\n你选择的文件为：")
        print(fileName_choose)
        # print("文件筛选器类型：", filetype)

        fnsplit = fileName_choose.split('/')[-1].split('_')
        # 风场
        farm = fnsplit[0][:-4]
        # 风机
        wind_turbine = fnsplit[0][-4:]
        # 转速
        rotating_speed = fnsplit[2]
        # 采样时间
        sampling_time = fnsplit[1]
        # 采样率
        self.sampling_fre = fnsplit[-2]
        # 测点
        try:
            self.mp = point_description[farm]
        except KeyError as e:
            self.mp = []
            print('键 %s 不存在' % e)

        self.lineEdit.setText(farm)
        self.lineEdit_2.setText(wind_turbine)
        self.lineEdit_3.setText(rotating_speed)
        self.lineEdit_4.setText(sampling_time)
        self.lineEdit_5.setText(self.sampling_fre)
        # 先清空，再添加
        self.comboBox.clear()
        self.comboBox.addItems(self.mp)

        # 读取CSV文件数据
        self.data = read_csv(fileName_choose, header=None)

        if not self.data.empty:
            # 激活绘图按钮
            self.pushButton_2.setEnabled(True)

    def plot(self):
        # 数据列
        columns = self.data.columns
        data_length = self.data.shape[0]
        for i, col in enumerate(columns):
            # 时域数据x轴间隔
            step = round((data_length / int(self.sampling_fre)) / data_length * 1000000) / 1000000
            # 频谱数据
            fre, am = fourier_transform(self.data[col], int(self.sampling_fre))
            am = Series(am)
            am = am.round(decimals=6)
            sub = QMdiSubWindow()
            fig = plt.figure()
            if self.mp:
                title = '频谱/时域信号 - ' + self.mp[i]
            else:
                title = '频谱/时域信号 - '
            fig.suptitle(title)
            axes1 = fig.add_subplot(211)
            axes2 = fig.add_subplot(212)
            axes1.grid(True, color="grey", linestyle='--')
            axes2.grid(True, color="grey", linestyle='--')
            axes1.plot(fre, am, color='blue', linewidth=0.5)
            axes2.plot([step*n for n in range(data_length)], self.data[col], color='blue', linewidth=0.5)
            axes1.set_xlabel('频率(Hz)')
            axes1.set_ylabel('加速度(m/s^2)')
            axes2.set_xlabel('时间(s)')
            axes2.set_ylabel('加速度(m/s^2)')
            canvas = FigureCanvas(fig)
            # 向sub内部添加控件
            sub.setWidget(canvas)
            # 子窗口增加一个
            self.count += 1
            sub.setWindowTitle(title)
            self.mdiArea.addSubWindow(sub)
            sub.show()
        self.mdiArea.tileSubWindows()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec())
    # app.exec()
