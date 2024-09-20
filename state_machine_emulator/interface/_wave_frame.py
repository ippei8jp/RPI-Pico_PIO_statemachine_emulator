from tkinter import Frame, Label, Listbox, Text

from .WaveformDiagram import WaveformDiagram

def build_wave_frame(self, frame_width, frame_height):
    """ build the frame with the waveform of the emulation """
    window_size = (frame_width, frame_height)
    # the wave frame
    self.wave_frame = Frame(self.root, width=window_size[0], height=window_size[1])
    self.wave_frame.grid(row=2, column=0, columnspan=4)
    self.wave_frame.grid_propagate(False)

    
    # GPIOデータの抽出
    GPIO_tmp=[]
    for idx, data in enumerate(self.emulation_results) :
        GPIO_tmp.append(data[0]["GPIO"])
    
    # WaveformDiagram インスタンスの生成
    self.wfd = WaveformDiagram(self.wave_frame, GPIO_tmp, 
                    width=window_size[0], height=window_size[1], 
                    change_current_position=self.change_current_position)

    # グラフ描画
    # wfd.DrawWaveform(channel_list)
    # 空リストで表示要求(チェックボタンで選択を促すメッセージを表示)
    self.wfd.DrawWaveform(channel_list=[], cursor_pos=self.current_clock)


def update_wave_frame(self):
    # カーソル位置の描画
    self.wfd.disp_cursor(self.current_clock)

def change_current_position(self, pos) :
    self.current_clock = pos
    self.enable_disable_buttons()
    self.update_display()

