import tkinter as tk

class ScrollableCanvas(tk.Canvas):
    def __init__(self, master, cnf={}, yscrollincrement=1, width=100, **kw):
        # ドラッグによるスクロールをスムーズにするため、yscrollincrementを1にしておく
        super().__init__(master, cnf=cnf, yscrollincrement=yscrollincrement, width=width, **kw)
        self.pack_propagate(False)        # サイズの自動調整を無効にする

        # スクロールバーの幅
        scrollbar_width=20

        # スクロールバーの作成
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.yview, width=scrollbar_width)
        self.scrollbar.pack(side="right", fill="y")
        self.configure(yscrollcommand=self.scrollbar.set)

        # キャンバスにフレーム(表示する中身)を配置
        self.child_frame = tk.Frame(self)
        self.create_window((0, 0), window=self.child_frame, anchor="nw", width=width-scrollbar_width)   # スクロールバーの分を引いておく

        # ウィンドウイベントのバインディング
        self.bind("<Configure>", self._configure_canvas)    # リサイズ/移動など
        self.child_frame.bind("<Configure>", self._configure_frame)
        
        # マウスイベントのバインディング
        # 重なっている部分でもイベントを補足するため、rootにbindする
        # 既に登録されているハンドラを上書きしないよう "+" を指定
        self.winfo_toplevel().bind("<Button-1>", self._on_click, "+")               # 左クリック
        self.winfo_toplevel().bind("<B1-Motion>", self._on_drag, "+")               # 左クリック中の移動(ドラッグ)

        # 初期化
        self._configure_canvas()
        self._configure_frame()

        # ドラッグ開始位置
        self.start_y = 0

    # 座標がcanvas内かをチェック
    def isInCanvas(self, event) :
        # マウス位置(画面上座標)
        x = event.x_root
        y = event.y_root
        # canvasの範囲(画面上座標)
        canvas_x1 = self.winfo_rootx()
        canvas_y1 = self.winfo_rooty()
        canvas_x2 = self.winfo_rootx() + self.winfo_width()
        canvas_y2 = self.winfo_rooty() + self.winfo_height()

        # 範囲内ならTrue
        return canvas_x1 <= x < canvas_x2 and canvas_y1 <= y < canvas_y2
    
    def _configure_canvas(self, event=None):
        # print(f'_configure_canvas: {event=}')
        # canvas全体の座標をスクロール範囲に設定
        self.configure(scrollregion=self.bbox("all"))
    
    def _configure_frame(self, event=None):
        # print(f'_configure_frame: {event=}')
        # canvas全体の座標をスクロール範囲に設定
        self.configure(scrollregion=self.bbox("all"))
    
    def _on_click(self, event):
        if not self.isInCanvas(event) :
            # キャンバス外なら何もしない
            return
        # print(f'_on_click: {event=}')
        # ドラッグ開始位置
        self.start_y = event.y_root
    
    def _on_drag(self, event):
        if not self.isInCanvas(event) :
            # キャンバス外なら何もしない
            return
        # print(f'_on_drag: {event=}')
        # スクロール処理
        dy = event.y_root - self.start_y
        self.yview_scroll(-dy, "units")
        # ドラッグ開始位置を更新
        self.start_y = event.y_root
