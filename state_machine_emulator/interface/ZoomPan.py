from matplotlib.backend_bases import MouseButton
import numpy as np

class ZoomPan:
    def __init__(self,axs, handlers=None):
        self.cur_xlim = None
        self.xpress = None
        self.ctrl_press = False
        self.alt_press = False
        self.shift_press = False
        self.axs = axs
        # オリジナルのビュー範囲
        self.orig_xlim = axs[0].get_xlim()
        
        # クリック処理の外部ハンドラ
        if not isinstance(handlers, dict) :
            print("ZoomPan : handlers is not dictionary. Ignore.") 
            handlers = {}
        self.handlers = handlers

        # 各イベント処理を登録
        self.zoom_factory(axs[0],base_scale=1.1)
        self.key_factory(axs[0])
        self.pan_factory(axs[0])
    
    # ==================================================================
    # ZOOM処理定義
    def zoom_factory(self, ax, base_scale = 2.):
        # X方向ズーム処理
        def zoomX(event,scale_factor):
            # 現在のビュー範囲
            cur_xlim = ax.get_xlim()
            
            if (event.xdata is not None) : 
                xdata = event.xdata         # マウス位置
            else :
                xdata = self.axs[0].transData.inverted().transform((event.x, event.y))[0]
            if xdata is not None :      # マウス位置が有効範囲のときのみ処理
                # 新しいビュー範囲の幅
                new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                
                # 相対位置
                relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
                
                # 新しいビュー範囲
                new_xlim = np.array([xdata - new_width * (1-relx), xdata + new_width * (relx)])
                # print(f'{new_xlim=}')
                
                if (new_xlim[1] - new_xlim[0]) > (self.orig_xlim[1] - self.orig_xlim[0]) :
                    # オリジナルサイズより縮小されたらオリジナルサイズに制限
                    new_xlim = self.orig_xlim
                
                ax.set_xlim(new_xlim)
                
                # 再描画
                ax.figure.canvas.draw()
        
        # マウスホイール イベントハンドラ
        def zoom(event):
            # print(f'zoom() : {vars(event)}')
            if event.button == 'down':
                # zoom in
                zoomX(event, 1 / base_scale)    # X方向ズーム処理
            elif event.button == 'up':
                # zoom out
                zoomX(event, base_scale)        # X方向ズーム処理
            else:
                # その他
                print(f'unknown wheel button : {event.button}')
            
        
        # イベントハンドラの登録
        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom
    
    # ==================================================================
    # キー処理定義
    def key_factory(self,ax):
        def onPress(event):
            # print(f'key_factory.onPress() : {vars(event)}')
            if event.key == "control":              # CTRLキーが押された
                self.ctrl_press = True
            elif event.key == "alt":                # ALTキーが押された
                self.alt_press = True
            elif event.key == "shift":              # SHIFTキーが押された
                self.shift_press = True

        def onRelease(event):
            # print(f'key_factory.onRelease() : {vars(event)}')
            
            if event.key == "control":              # CTRLキーが離された
                self.ctrl_press = False
            elif event.key == "alt":                # ALTキーが離された
                self.alt_press = False
            elif event.key == "shift":              # SHIFTキーが離された
                self.shift_press = False
        
        # イベントハンドラの登録
        fig = ax.get_figure()
        fig.canvas.mpl_connect('key_press_event',onPress)
        fig.canvas.mpl_connect('key_release_event',onRelease)

    
    # ==================================================================
    # 移動処理定義
    def pan_factory(self, ax):
        # マウス ボタンが押されたときのイベントハンドラ
        def onClick(event):
            # print(f'pan_factory.onClick() : {vars(event)}')
            
            if event.button == MouseButton.LEFT :
                # 左ボタン
                if event.dblclick :
                    # ダブルクリック
                    if self.ctrl_press : 
                        # CTRL+ダブルクリックは何もしない
                        pass
                    elif self.alt_press : 
                        # ALT+ダブルクリックは何もしない
                        pass
                    elif self.shift_press : 
                        # SHIFT+ダブルクリックは何もしない
                        pass
                    else :
                        handler = self.handlers.get("doubleclick")
                        if handler :
                            handler(event)
                else :
                    # シングルクリック
                    # 現在の表示範囲
                    self.cur_xlim = ax.get_xlim()       # (left,right))
                    
                    # クリックされたx座標
                    # x0,y0         : canvas内の相対座標
                    # xdata,ydata   : データ座標
                    # ax範囲外でもデータ座標を取得(x座標連動しているのでどこでとっても同じ)
                    if (event.xdata is not None) : 
                        xpress = event.xdata
                    else :
                        xpress = self.axs[0].transData.inverted().transform((event.x, event.y))[0]

                    if self.ctrl_press : 
                        # print(f"ctrl+clicl : {xpress}")
                        handler = self.handlers.get("ctrl_click")
                        if handler :
                            handler(event)
                    elif self.alt_press : 
                        # print(f"alt+clicl : {xpress}")
                        handler = self.handlers.get("alt_click")
                        if handler :
                            handler(event)
                    elif self.shift_press : 
                        # print(f"shift+clicl : {xpress}")
                        handler = self.handlers.get("shift_click")
                        if handler :
                            handler(event)
                    else :
                    # 押された位置を記憶
                        self.xpress = xpress

        # マウス ボタンが離されたときのイベントハンドラ
        def onRelease(event):
            # print(f'pan_factory.onRelease() : {vars(event)}')
            
            if event.button == MouseButton.LEFT :
                # 左ボタン
                # 押された位置をクリア
                self.xpress = None
                
                # 再描画
                ax.figure.canvas.draw()

        # マウス移動時のイベントハンドラ
        def onMove(event):
            # print(f'pan_factory.onMove() : {vars(event)}')
            
            # X方向の移動
            if (event.xdata is not None) : 
                xdata = event.xdata         # マウス位置
            else :
                xdata = self.axs[0].transData.inverted().transform((event.x, event.y))[0]
            
            if self.xpress is not None and xdata is not None :  # マウス位置が有効範囲のときのみ処理
                dx = xdata - self.xpress        # 移動量(np.float64)
                self.cur_xlim -= dx             # nd.ndarray - np.float64 なので、ndarray各要素から減算
                
                if self.cur_xlim[1] > self.orig_xlim[1] :    # 右端がサンプル数より大きくならないよう制限する
                    self.cur_xlim -= self.cur_xlim[1] - self.orig_xlim[1]
                    # print(f'{self.cur_xlim=}')
                
                if self.cur_xlim[0] < 0 :       # 左端が負数にならないよう制限する
                    self.cur_xlim -= self.cur_xlim[0]
                    # print(f'{self.cur_xlim=}')
                
                ax.set_xlim(self.cur_xlim)          # 移動量分表示範囲を変更
                
                # 再描画
                ax.figure.canvas.draw()

        # イベントハンドラの登録
        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('button_press_event',  onClick)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMove)

        #return the function
        return onMove
