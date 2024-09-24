from tkinter import Frame, Label, Listbox, Text


def build_output_frame(self, frame_width, frame_height):
    """ build the frame with the output (of c-statements) of the emulation """
    # the output frame
    self.output_frame = Frame(self.root, width=frame_width, height=frame_height)
    self.output_frame.grid(row=1, column=3, padx=0, pady=2)
    self.output_frame.grid_propagate(0)

    # program output label
    self.program_label = Label(self.output_frame, text="Highlight is just produced output from RxFIFO:")
    self.program_label.grid(row=2, column=3, padx=(5, 5), sticky='W')

    # program output is in a listbox
    self.output_listbox = Listbox(self.output_frame, height=26, width=62, justify="left", exportselection=0)
    self.output_listbox.grid(row=3, column=3, padx=(5, 5), sticky='W')

    # put the c-program into the listbox (in update_output_frame the current line will be highlighted (selected) in the GUI)
    for line in self.emulation_output_c_program:
        self.output_listbox.insert("end", line)

    # messages label
    self.program_label = Label(self.output_frame, text="Messages")
    self.program_label.grid(row=4, column=3, padx=(5, 5), sticky='W')

    # messages
    self.messages_text = Text(self.output_frame, height=11, width=50, exportselection=0)
    self.messages_text.tag_config('warning', background="#ffa0a0", foreground="#000000")
    self.messages_text.grid(row=5, column=3, padx=(5, 5), sticky='W')


def update_output_frame(self):
    """ update the panel with the output (of c-statements) """
    # highlight the just executed output
    self.output_listbox.selection_clear(0, "end")

    # 表示項目すべてについてループする
    for i in range(self.output_listbox.size()) :
        # 1行取得
        line=self.output_listbox.get(i).split('=')
        # get_pcの表示は処理しない
        if not 'pc' in line[0] :
            # '='の右側を数値化
            val=int(line[-1], 0)
            if self.hex_check_val.get() :
                # 16進数文字列
                val_str = f' {val:#010x}'
            else :
                # 10進数文字列
                val_str = f' {val:>10d}'
            line[-1] = val_str
            # 文字列に戻す
            new_Line = '='.join(line)
            # 表示を更新
            self.output_listbox.delete(i)
            self.output_listbox.insert(i, new_Line)

    for index in self.emulation_results[self.current_clock][6]:
        self.output_listbox.selection_set(index)
        self.output_listbox.see(index)

    # put the messages produced at the current clock here
    self.messages_text.delete("1.0", "end")
    for line in self.emulation_results[self.current_clock][7]:
        self.messages_text.insert("end", "-> " + line, "warning")
