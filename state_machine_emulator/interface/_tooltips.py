# thanks to crxguy52 and Stevoisiak:
# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
from tkinter import Toplevel, Label

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info', offset_x=150, offset_y=20, label_conf={}):
        self.waittime = 500     #milliseconds
        self.widget = widget
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.label_conf = label_conf

        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.offset_x
        y += self.widget.winfo_rooty() + self.offset_y
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        
        # ここでのデフォルトの設定値を設定
        for key, default in {
                                'justify':      'left',
                                'background':   'yellow', 
                                'relief':       'solid', 
                                'borderwidth':  1, 
                                'wraplength':   180,
                            }.items() :
            self.label_conf[key] = self.label_conf.get(key, default)
        # ラベルの生成と配置
        label = Label(self.tw, text=self.text, **self.label_conf)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()