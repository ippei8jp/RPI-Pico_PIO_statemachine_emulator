from rp2 import *


@asm_pio(
            sideset_init    = PIO.OUT_LOW,          # 複数端子指定のときはlistで指定
            out_shiftdir    = PIO.SHIFT_LEFT,       # OSRは左シフト(最上位側から取り出す)
        )
def pwm_prog():
    mov(x, isr)   .side(0)      # FIFO empty時に読み込むデータをXに格納、端子↓
    pull(noblock)               # FIFOからデータ読み込み
    mov(isr, osr)               # isrにバックアップ
    out(x, 16)                  # 上位16bitが周期
    out(y, 16)                  # 下位16bitがHigh区間
    label("pwmloop")
    jmp(x_not_y, "skip")        # X≠Yならスキップ
    nop()         .side(1)      # X=Yなら  端子↑
    label("skip")
    jmp(x_dec, "pwmloop")       # Xをデクリメントしてループ先頭へ

"""
動作イメージ
    ^^^^|_______|^^^^^^^^|____ 波形
        |← X          →|     ループ毎にデクリメントしていく
                |← Y  →|     固定  Xがここと一致したら端子を↑する
==NOTE==
最大値を指定しても6クロックはLowが出力される
最小値を指定しても2クロックはHighが出力される
出力周波数は(count_freqで指定した周波数) / 2 /(periodで指定した値)
count_freq =   2MHz、period = 0xffff で 152Hz
count_freq = 125MHz、period = 0xffff で 954Hz
count_freq = 125MHz、period = 0x0fff で 15.2KHz
"""


RESULT = StateMachine(0, pwm_prog, sideset_base=Pin(15))

