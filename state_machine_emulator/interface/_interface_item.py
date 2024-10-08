from tkinter import Text, Label, Listbox
from interface._tooltips import CreateToolTip

"""
All the classes here are an element of the GUI. They all have a setup (__init__), a method to make a string to be used and update.
"""

class Interface_Item:
    def __init__(self, frame, display_name, row, col, width):
        self.display_name = display_name
        self.row = row
        self.col = col
        self.width = width
        # make the Text widget for the name of the variable to be displayed
        label = Text(frame, height=1, width=12)
        label.insert("end", self.display_name)
        label.configure(font="TkFixedFont", state="disabled")
        label.grid(row=self.row, column=self.col, padx=(5, 5), sticky='W')
        # make the Text widget for the value of the variable
        self.value_label = Text(frame, height=1, width=self.width)
        self.value_label.insert("end", self.value_string(0))
        self.value_label.configure(font="TkFixedFont", state="disabled")
        self.value_label.grid(row=self.row, column=self.col, padx=(5, 5), sticky='E')
        # make tags to be used in showing which characters have changed, and which have not
        self.value_label.tag_config("changed", foreground="White", background="Red")
        self.value_label.tag_config("unchanged", foreground="Black", background="White")

    def update(self, clock, hex_mode=False):
        # save the current value
        old_value = self.value_label.get("1.0", "end").strip()
        # allow the widget text to be changed, and delete the existing content
        self.value_label.configure(state="normal")
        self.value_label.delete("1.0", "end")
        # determine the new text for the widget, and insert it
        new_value = self.value_string(clock, hex_mode=hex_mode)
        self.value_label.insert("end", new_value)
        # disallow changing the text, justify right
        self.value_label.configure(state="disabled")
        self.value_label.tag_configure("j_left", justify='left')    # 左寄せタグの設定
        self.value_label.tag_add("j_left", 1.0, "end")              # その指定
        """
        # now apply colors, using tags "changed and "unchanged", e.g. to the last 32 characters (the binary representation)
        len_string = min(len(new_value), len(old_value), 32)
        for i in range(-1,-len_string-1, -1):
            if old_value[i] != new_value[i]:
                self.value_label.tag_add("changed", f"{1}.{len(new_value)+i}") 
            else:
                self.value_label.tag_add("unchanged", f"{1}.{len(new_value)+i}") 
        """
        # now apply colors, using tags "changed and "unchanged"
        # 2進数表記と10/16進数表記を入れ替えたので先頭から比較する
        len_string = new_value.find("=")    # '=' の手前まで比較する
        len_string = len_string if len_string > 0 else len(new_value) # '=' がなければ文字列全体
        for i in range(len_string):
            if old_value[i] != new_value[i]:
                self.value_label.tag_add("changed", f"{1}.{i}") 
            else:
                self.value_label.tag_add("unchanged", f"{1}.{i}")
        
            
class Var_Bits_32(Interface_Item):
    def __init__(self, display_name, var_name, frame, row, col, var, var_index):
        self.var_name = var_name
        self.var = var
        self.var_index = var_index
        super().__init__(frame, display_name, row, col, 53)

    def value_string(self, clock, hex_mode=False):
        value_string = ""
        value = self.var[clock][self.var_index][self.var_name]
        # extend the value_string based on bits in 'value' 
        for i in reversed(range(32)):
            value_string += "0" if (value & (1 << i)) == 0 else "1"
            value_string += "_" if i % 4 == 0 and i != 0 else ""   # 4桁毎に"_"を挿入
        if hex_mode :
            value_string += f" = {self.var[clock][self.var_index][self.var_name] & 0xFFFFFFFF : #010x}"
        else :
            value_string += f" = {self.var[clock][self.var_index][self.var_name] & 0xFFFFFFFF : >10d}"
        return value_string


class Pin_Settings_32(Interface_Item):
    def __init__(self, display_name, base_name, count_name, frame, row, col, var, var_index):
        self.base_name = base_name
        self.count_name = count_name
        self.var = var
        self.var_index = var_index
        super().__init__(frame, display_name, row, col, 53)

    def value_string(self, clock, hex_mode=False):
        base = self.var[clock][self.var_index][self.base_name]
        count = 0
        if self.count_name:
            count = self.var[clock][self.var_index][self.count_name]
            # dirty hack: sideset_count includes the sideset_opt bit, but this does not set a pin!
            if self.count_name == "sideset_count" and self.var[clock][self.var_index]["sideset_opt"]:
                count -= 1
        value_string_list = ['.' for i in range(32)]
        if base >= 0:
            value_string_list[31-base] = 'B'
        for i in range(count-1):
            value_string_list[31-(base+1+i) % 32] = 'C'
        value_string = ''.join(value_string_list)
        value_string = '_'.join(value_string[i:i+4] for i in range(0, len(value_string), 4))    # 4桁毎に"_"を挿入
        return value_string


class Var_List_IRQ(Interface_Item):
    def __init__(self, display_name, frame, row, col, var, var_index):
        self.var = var
        self.var_index = var_index
        super().__init__(frame, display_name, row, col, 53)

    def value_string(self, clock, hex_mode=False):
        value_string = ""
        l = len(self.var[clock][self.var_index])
        for i, v in enumerate(reversed(self.var[clock][self.var_index])):
            value_string += "_" if (l-i) % 4 == 0 and i != 0 else ""   # 4桁毎に"_"を挿入
            value_string += "1" if v==1 else "0" if v==0 else "."
        return value_string

class Var_List(Interface_Item):
    def __init__(self, display_name, frame, row, col, var, var_index):
        self.var = var
        self.var_index = var_index
        super().__init__(frame, display_name, row, col, 53)

    def value_string(self, clock, hex_mode=False):
        value_string = ""
        for v in reversed(self.var[clock][0][self.var_index]):
            value_string += "1" if v==1 else "0" if v==0 else "."
        value_string = '_'.join(value_string[i:i+4] for i in range(0, len(value_string), 4))    # 4桁毎に"_"を挿入
        return value_string


class Interface_Item_Listbox_Bits:
    def __init__(self, display_name, var_name, frame, row, col, var, clock):
        self.display_name = display_name
        self.var_name = var_name
        self.var = var
        label = Label(frame, text=display_name + ' \u24D8')
        CreateToolTip(label, \
            "The data in TxFIFO is transmitted from the normal core to the state machine.\n"
            "The data in RxFIFO is transmitted from the state machine to the normal core. ",
            offset_x=80, offset_y=20, label_conf={'wraplength': -1})
        label.grid(row=row, column=col, padx=(5, 5), sticky='W')
        self.value_listbox = Listbox(frame, height=4, width=55, justify="left", exportselection=0)
        for index in range(4):
            self.value_listbox.insert("end", self.value_string(index, clock))
        self.value_listbox.grid(row=row+1, column=0, padx=(5, 5))

    def update(self, clock, hex_mode=False):
        for index in range(4):
            self.value_listbox.delete(0)
        for index in range(4):
            self.value_listbox.insert("end", self.value_string(index, clock, hex_mode=hex_mode))

    def value_string(self, index, clock, hex_mode=False):
        value_string = ""
        value = self.var[clock][1][self.var_name][index]
        for i in reversed(range(32)):
            value_string += "0" if (value & (1 << i)) == 0 else "1"
            value_string += "_" if i % 4 == 0 and i != 0 else ""   # 4桁毎に"_"を挿入
        if hex_mode :
            value_string += f" = {self.var[clock][1][self.var_name][index] & 0xFFFFFFFF : #010x}"
        else :
            value_string += f" = {self.var[clock][1][self.var_name][index] & 0xFFFFFFFF : >10d}"
        return value_string


class Interface_Item_Listbox_Time:
    def __init__(self, display_name, frame, row, col, var):
        self.display_name = display_name
        self.var = var
        label = Label(frame, text=display_name)
        label.grid(row=row, column=col, padx=(5, 5), sticky='W')
        self.value_listbox = Listbox(frame, height=13, width=55, exportselection=0)
        for index in range(len(var)):
            self.value_listbox.insert("end", self.value_string(index))
        self.value_listbox.grid(row=row+1, column=0, padx=(5, 5))

    def update(self):
        for index in range(4):
            self.value_listbox.delete(0)
        for index in range(4):
            self.value_listbox.insert("end", self.value_string(index))

    def value_string(self, index, hex_mode=False):
        value_string = str(self.var[index][0]) + " : " + self.var[index][1]
        first = True
        for l in self.var[index][2:]:
            value_string += "=" if first else ", "
            first = False
            value_string += str(l)
        return value_string
