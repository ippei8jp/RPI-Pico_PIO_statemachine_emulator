# from matplotlib import pyplot as plt  # plt.figure()を使うとtk.checkbutton()が正常に動作しなくなる
from matplotlib.figure import Figure    # 代わりにFigure()を使う
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator,MultipleLocator,AutoMinorLocator

import numpy as np

# numpyの配列を省略せずにprintする設定
np.set_printoptions(threshold=np.inf)

import tkinter as tk

# ズーム/パンの処理クラス
from .ZoomPan import ZoomPan

# スクロール可能なcanvas
from .ScrollableCanvas import ScrollableCanvas

# 波形表示クラス
class WaveformDiagram :
    def __init__(self, master, gpio_data, width=100, height=100, change_current_position=None) :
        # 上位ウィジェットに関する情報
        self.master = master
        self.canvas_size = (width, height)
        self.change_current_position=change_current_position
        
        # カーソルポジション
        self.cursor_position = 0
        
        # 表示するデータ
        self.y_datas = np.array(gpio_data).transpose()  # [時間, チャネル]を[チャネル, 時間]に変換
        self.sumple_num = len(self.y_datas[0])          # サンプリング数
        self.x_data = list(range(self.sumple_num))      # 時間軸
        
        # ツールバーを生成
        self.frame_toolbar = self.build_toolbar()
        
        # スクロール可能なキャンバスを生成
        self.canvas = ScrollableCanvas(self.master, width=self.canvas_size[0], height=self.canvas_size[1])
        self.canvas.pack(fill="both", expand=True)
    
    
    # =================================================================
    # ツールバーの作成
    def build_toolbar(self) :
        frame_toolbar = tk.Frame(self.master)
        
        # =================================================================
        # チェックボタンとupdateボタン
        button_num = len(self.y_datas)
        self.check_val = [None for _ in range(button_num)]
        check_btn = [None for _ in range(button_num)]
        for idx in range(button_num):
            self.check_val[idx] = tk.BooleanVar()
            check_btn[idx] = tk.Checkbutton(frame_toolbar, text=str(idx), variable=self.check_val[idx])
            check_btn[idx].pack(side=tk.LEFT)
        
        btn_update = tk.Button(frame_toolbar, text="udpate", command=self.update_button)
        btn_update.pack(side=tk.LEFT)
        
        # ツールバーを配置
        frame_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        return frame_toolbar
    
    # =================================================================
    # カーソルの描画
    def disp_cursor(self, new_cursor_position, force=False) :
        # 範囲外に出ないようチェック
        new_cursor_position = new_cursor_position if new_cursor_position > 0 else 0
        new_cursor_position = new_cursor_position if new_cursor_position < self.sumple_num else self.sumple_num
        
        if self.cursor_position != new_cursor_position or force:
            # カーソル位置が変更された
            if len(self.axs) > 0 :
                for ax in self.axs :
                    # 前のカーソルを消す
                    if self.cursor_position is not None :
                        ax.axvspan(self.cursor_position, self.cursor_position+1, color="white", alpha=1)
                    # 新しいカーソルを描画
                    ax.axvspan(new_cursor_position, new_cursor_position+1, color="red", alpha=0.3)
                    
                # 再描画
                self.axs[0].get_figure().canvas.draw()
            
            # 現在位置変更
            self.cursor_position = new_cursor_position
            
    
    # =================================================================
    # ダブルクリックの処理
    def doubleclick_handler(self, event) :
        # print(f'doubleclick_handler : {event.xdata=}')
        if event.xdata is not None :
            if self.change_current_position : 
                self.change_current_position(int(event.xdata))
            else :
                self.disp_cursor(int(event.xdata))
    
    # =================================================================
    # updateボタンの処理
    def update_button(self):
        checked_button_list = []
        for idx in range(len(self.check_val)):
            if self.check_val[idx].get():
                checked_button_list.append(idx)
        print(f'{checked_button_list=}')
        
        # 新しくグラフを表示
        self.DrawWaveform(checked_button_list, self.cursor_position)
    
    
    # =================================================================
    # グラフの作成
    def DrawWaveform(self, channel_list=[], cursor_pos=0) :
        # 表示するチャネルに関する設定
        self.channel_list = channel_list
        self.channel_num = len(self.channel_list)
        
        # 表示中のグラフを削除
        for c in self.canvas.child_frame.winfo_children() :
            c.destroy()

        self.axs = []
        self.fig = None
        
        # 描画するチャネルがなかったら何もしない
        if self.channel_num == 0 :
            label = tk.Label(self.canvas.child_frame, text=f"select the channel with the check button above, then click the “update” button.")
            label.pack(side=tk.TOP)
            
            # カーソル位置の初期化だけしておく
            self.disp_cursor(cursor_pos, force=True)
            
            return
        
        # figureとsubplotの生成
        # plt.figure()を使うとtk.checkbutton()が正常に動作しなくなる
        # 代わりにFigure()を使う
        # plt.subplots()は便利なんだけど、↑の件で使えない
        # self.fig, axs = plt.subplots(self.channel_num, 1, figsize=(15.0, self.channel_num * 0.6), sharex=True)
        # figure()してからadd_subplot()するように変更し、plt.figure()をFigure()に変更
        # self.fig = plt.figure(figsize=(15.0, self.channel_num * 0.6))
        # self.fig = Figure(figsize=(15.0, self.channel_num * 0.6))   # 幅はTk.Frameに貼り付けたときに調整されるので大体あってれば良い
        self.fig = Figure(figsize=(15.0, self.channel_num * 0.6 if self.channel_num > 2 else 1.8))   # 幅はTk.Frameに貼り付けたときに調整されるので大体あってれば良い
        for idx in range(self.channel_num) :
            self.axs.append(self.fig.add_subplot(self.channel_num, 1, idx + 1, sharex=self.axs[0] if idx != 0 else None))
        
        # channel_num が1のとき、axsはイテラブルでない(forで回せない)ので確認する
        if not getattr(self.axs, '__iter__', False) :
            self.axs = [self.axs]     # イテラブルにする
        
        # 描画範囲(描画範囲全体を使うように設定)
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0)
        
        # グラフの描画
        for idx, bit in enumerate(channel_list) :
            # グラフ
            self.axs[idx].step(self.x_data, self.y_datas[bit], where='post')
            
            # Y軸ラベル
            self.axs[idx].set_ylabel(str(bit))
            
            # 表示範囲
            self.axs[idx].set_xlim(0, self.sumple_num)
            self.axs[idx].set_ylim(0, 1)
            
            # 枠線を消す
            self.axs[idx].spines['right'].set_visible(False)
            self.axs[idx].spines['left'].set_visible(False)
            self.axs[idx].spines['top'].set_visible(False)
            self.axs[idx].spines['bottom'].set_visible(False)
            # 主目盛を10等分して補助目盛をつける(X軸)
            self.axs[idx].xaxis.set_minor_locator(AutoMinorLocator(10))
            
            # 目盛ラベルを消す
            self.axs[idx].tick_params(labelbottom=False, labelleft=False, labelright=False, labeltop=False)
            # 目盛線は下側だけ表示
            self.axs[idx].tick_params(bottom=True, left=False, right=False, top=False)
            # 目盛線を内向きにする(主目盛/補助目盛)
            self.axs[idx].tick_params(which='both', direction='in')

            # 一番上と一番下の目盛ラベルを表示
            if   idx == 0 :
                self.axs[idx].tick_params(labeltop=True)
            elif idx == self.channel_num - 1 :
                self.axs[idx].tick_params(labelbottom=True)
            else :
                pass
        # 要素が見切れるのを防ぐ
        self.fig.tight_layout()

        # =================================================================
        # ズーム/移動処理登録()
        self.zp = ZoomPan(self.axs, self.doubleclick_handler)
        
        # =================================================================
        # グラフを張り付け
        graph_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas.child_frame)
        graph_canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.NONE, expand=False)
        
        # カーソル位置の描画
        self.disp_cursor(cursor_pos, force=True)

        # canvasを描画
        graph_canvas.draw()
