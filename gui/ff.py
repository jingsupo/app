import wx


class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        # 确保父类的__init__方法被调用
        super(MyFrame, self).__init__(*args, **kw)

        # 创建面板
        panel = wx.Panel(self)

        # 在面板上放置静态文本并设置字体
        poems = '山无陵，江水为竭，冬雷震震衰，夏雨雪，天地合，乃敢与君绝！'
        st = wx.StaticText(panel, label=poems, pos=(10,10))
        font = st.GetFont()
        font.PointSize += 1
        font = font.Bold()
        st.SetFont(font)

        # 创建菜单栏
        self.makemenubar()
        # 创建状态栏
        self.CreateStatusBar()
        self.SetStatusText('韩燕芳，欢迎您！')

    def makemenubar(self):
        # 创建文件按钮
        filemenu = wx.Menu()
        # '\t...'语法定义一个快捷键来执行相同的动作
        helloitem = filemenu.Append(-1, '&Hello...\tCtrl-H', '状态栏提示')
        filemenu.AppendSeparator()
        exititem = filemenu.Append(0, '退出\tCtrl-Q', '退出程序')

        # 创建帮助按钮
        helpmenu = wx.Menu()
        aboutitem = helpmenu.Append(-1, '关于', '关于本程序')

        # 创建菜单栏
        menubar = wx.MenuBar()
        menubar.Append(filemenu, '&文件')
        menubar.Append(helpmenu, '&帮助')

        # 放置菜单栏
        self.SetMenuBar(menubar)

        # 最后，给每一个按钮关联EVT_MENU动作，这样在按钮被点击的时候可以触发相应的功能函数
        self.Bind(wx.EVT_MENU, self.onhello, helloitem)
        self.Bind(wx.EVT_MENU, self.onexit, exititem)
        self.Bind(wx.EVT_MENU, self.onabout, aboutitem)

    def onhello(self, event):
        wx.MessageBox('芳芳，我爱你！（づ￣3￣）づ╭❤～', '❤')

    def onexit(self, event):
        self.Close(True)

    def onabout(self, event):
        wx.MessageBox('爱你的车车', '关于')


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame(None, title='韩燕芳')
    frm.Show()
    app.MainLoop()
