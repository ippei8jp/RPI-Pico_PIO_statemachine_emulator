# from matplotlib import pyplot as plt  # plt.figure()を使うとtk.checkbutton()が正常に動作しなくなる
from matplotlib.figure import Figure    # 代わりにFigure()を使う
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator,MultipleLocator,AutoMinorLocator

import numpy as np

# numpyの配列を省略せずにprintする設定
np.set_printoptions(threshold=np.inf)

import tkinter as tk

from ._tooltips import CreateToolTip

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
        self.cursor_cur = 0
        self.cursor_A = 0
        self.cursor_B = 0
        
        # 表示するデータ
        self.y_datas = np.array(gpio_data).transpose()  # [時間, チャネル]を[チャネル, 時間]に変換
        self.sumple_num = len(self.y_datas[0])          # サンプリング数
        self.x_data = list(range(self.sumple_num))      # 時間軸
        
        # ツールバーを生成
        self.frame_toolbar = self.build_toolbar()
        
        # ステータスバーを生成
        self.frame_statusbar = self.build_statusbar()
        
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
    # ステータスバーの作成
    def build_statusbar(self) :
        frame_statusbar = tk.Frame(self.master)
        
        # =================================================================
        # カーソル位置情報
        label = tk.Label(frame_statusbar, text="cursor \u24D8", width=10)
        label.pack(side=tk.LEFT)
        CreateToolTip(label, 
            "cursor current (RED)   : Double click to move.\n" 
            "cursor A       (GREEN) : CTRL+click to move.\n" 
            "cursor B       (BLUE)  : SHIFT+click to move.", 
            offset_x=80, offset_y=-50, label_conf={'wraplength': -1})
        
        label = tk.Label(frame_statusbar, text="cur(RED):", width=10)
        label.pack(side=tk.LEFT)
        self.status_cursor_cur = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_cursor_cur, width=7)
        label.pack(side=tk.LEFT)

        label = tk.Label(frame_statusbar, text="A(GREEN):", width=10)
        label.pack(side=tk.LEFT)
        self.status_cursor_A = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_cursor_A, width=7)
        label.pack(side=tk.LEFT)

        label = tk.Label(frame_statusbar, text="B(BLUE):", width=10)
        label.pack(side=tk.LEFT)
        self.status_cursor_B = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_cursor_B, width=7)
        label.pack(side=tk.LEFT)

        label = tk.Label(frame_statusbar, text="C-A:", width=5)
        label.pack(side=tk.LEFT)
        self.status_AC = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_AC, width=7)
        label.pack(side=tk.LEFT)

        label = tk.Label(frame_statusbar, text="C-B:", width=5)
        label.pack(side=tk.LEFT)
        self.status_BC = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_BC, width=7)
        label.pack(side=tk.LEFT)

        label = tk.Label(frame_statusbar, text="B-A:", width=5)
        label.pack(side=tk.LEFT)
        self.status_BA = tk.IntVar()
        label = tk.Label(frame_statusbar, textvariable=self.status_BA, width=7)
        label.pack(side=tk.LEFT)

        # ステータスバーを配置
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ステータスバーに値を表示
        self.update_statusbar()
        
        return frame_statusbar

    # =================================================================
    # ステータスバーの更新
    def update_statusbar(self) :
        self.status_cursor_cur.set(self.cursor_cur)
        self.status_cursor_A.set(self.cursor_A)
        self.status_cursor_B.set(self.cursor_B)
        self.status_AC.set(self.cursor_A - self.cursor_cur)
        self.status_BC.set(self.cursor_B - self.cursor_cur)
        self.status_BA.set(self.cursor_B - self.cursor_A)
    
    # =================================================================
    # カーソルの描画
    def disp_cursor(self, new_cursor_position, kind=0, force=False) :
                    # kind : 0: カレントカーソル  1: Aカーソル  2: Bカーソル
        # 範囲外に出ないようチェック
        new_cursor_position = new_cursor_position if new_cursor_position > 0 else 0
        new_cursor_position = new_cursor_position if new_cursor_position < self.sumple_num else self.sumple_num
        if kind == 0:
            old_cursor_position = self.cursor_cur
            cursor_color = "red"
            # 他のカーソルと重なっていたときの対策
            if old_cursor_position == self.cursor_A :
                old_cursor_color, old_alfa = "green", 0.3
            elif old_cursor_position == self.cursor_B :
                old_cursor_color, old_alfa = "blue", 0.3
            else :
                old_cursor_color, old_alfa = "white", 1
        elif kind == 1:
            old_cursor_position = self.cursor_A
            cursor_color = "green"
            # 他のカーソルと重なっていたときの対策
            if old_cursor_position == self.cursor_cur :
                old_cursor_color, old_alfa = "red", 0.3
            elif old_cursor_position == self.cursor_B :
                old_cursor_color, old_alfa = "blue", 0.3
            else :
                old_cursor_color, old_alfa = "white", 1
        elif kind == 2:
            old_cursor_position = self.cursor_B
            cursor_color = "blue"
            # 他のカーソルと重なっていたときの対策
            if old_cursor_position == self.cursor_cur :
                old_cursor_color, old_alfa = "red", 0.3
            elif old_cursor_position == self.cursor_A :
                old_cursor_color, old_alfa = "green", 0.3
            else :
                old_cursor_color, old_alfa = "white", 1
        else :
            print(f'disp_cursor : Unknown cursor type ({kind})')
            return
        
        if old_cursor_position != new_cursor_position or force:
            # カーソル位置が変更された
            if len(self.axs) > 0 :
                # グラフが表示されている
                for ax in self.axs :
                    # 前のカーソルを消す
                    if old_cursor_position is not None :
                         # 一度消してから
                        ax.axvspan(old_cursor_position, old_cursor_position+1, color="white", alpha=1)
                        # 描く
                        ax.axvspan(old_cursor_position, old_cursor_position+1, color=old_cursor_color, alpha=old_alfa)
                    # 新しいカーソルを描画
                    ax.axvspan(new_cursor_position, new_cursor_position+1, color=cursor_color, alpha=0.3)
                    
                # 再描画
                self.axs[0].get_figure().canvas.draw()
            
            # 現在位置変更
            if kind == 0:
                self.cursor_cur = new_cursor_position
            elif kind == 1:
                self.cursor_A = new_cursor_position
            elif kind == 2:
                self.cursor_B = new_cursor_position
            
            # ステータスバーの更新
            self.update_statusbar()
    
    # =================================================================
    # ダブルクリックの処理
    def doubleclick_handler(self, event) :
        # print(f'doubleclick_handler : {event.xdata=}')
        if event.xdata is not None :
            if self.change_current_position : 
                self.change_current_position(int(event.xdata))
            else :
                # カレントカーソルを描画
                self.disp_cursor(int(event.xdata), kind=0)
    
    # =================================================================
    # Ctrl+クリックの処理
    def ctrl_click_handler(self, event) :
        # print(f'ctrl_click_handler : {event.xdata=}')
        if event.xdata is not None :
            # Aカーソルを描画
            self.disp_cursor(int(event.xdata), kind=1)
    
    # =================================================================
    # Alt+クリックの処理
    def alt_click_handler(self, event) :
        print(f'alt_click_handler : {event.xdata=}')
    
    # =================================================================
    # Shift+クリックの処理
    def shift_click_handler(self, event) :
        # print(f'shift_click_handler : {event.xdata=}')
        if event.xdata is not None :
            # Bカーソルを描画
            self.disp_cursor(int(event.xdata), kind=2)
    
    # =================================================================
    # updateボタンの処理
    def update_button(self):
        checked_button_list = []
        for idx in range(len(self.check_val)):
            if self.check_val[idx].get():
                checked_button_list.append(idx)
        # print(f'{checked_button_list=}')
        
        # 新しくグラフを表示
        self.DrawWaveform(checked_button_list, self.cursor_cur)
    
    
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
            self.disp_cursor(cursor_pos, kind=0, force=True)
            
            return
        
        # figureとsubplotの生成
        # fig_widthは 厳密にはself.canvas.child_frameの幅から計算するべきだが、
        # 貼り付け時に微調整されるのでself.canvas_sizeから計算する
        # fig_heightは 見栄えがおかしくない(と思われる)値をトライアンドエラーで選んだ
        fig_dpi = 100.0
        fig_width = self.canvas_size[0] / fig_dpi 
        fig_height = self.channel_num * 0.6 if self.channel_num > 2 else 1.8

        # plt.figure()を使うとtk.checkbutton()が正常に動作しなくなる
        # 代わりにmatplotlib.figure.Figureを使う
        # plt.subplots()は便利なんだけど、↑の件で使えない
        # self.fig, axs = plt.subplots(self.channel_num, 1, figsize=(fig_width, fig_height), sharex=True)
        # figure()してからadd_subplot()するように変更し、plt.figure()をFigure()に変更
        # self.fig = plt.figure(figsize=(fig_width, fig_height))
        self.fig = Figure(figsize=(fig_width, fig_height), dpi=fig_dpi)
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
        
        handlers = {
                "doubleclick" : self.doubleclick_handler,
                "ctrl_click"  : self.ctrl_click_handler,
                #"alt_click"   : self.alt_click_handler,
                "shift_click" : self.shift_click_handler,
            }
        self.zp = ZoomPan(self.axs, handlers)
        
        # =================================================================
        # グラフを張り付け
        graph_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas.child_frame)
        graph_canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.NONE, expand=False)
        
        # カーソル位置の描画
        self.disp_cursor(cursor_pos, kind=0, force=True)

        # canvasを描画
        graph_canvas.draw()
