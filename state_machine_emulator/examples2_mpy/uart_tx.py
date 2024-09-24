from rp2 import *

# データ長8bit/パリティなし/ストップビット1/LSBファースト
@asm_pio(sideset_init=PIO.OUT_HIGH, out_init=PIO.OUT_HIGH, out_shiftdir=PIO.SHIFT_RIGHT)
def uart_tx():
    pull()              # 送信データ取得
    set(x, 7)  .side(0)       [7]   # ビットカウンタ初期化/スタートビット送出
    label("bitloop")
    out(pins, 1)              [6]   # 1bitずつ送出 1(out) + 6(delay) + 1(jmp) = 8clock
    jmp(x_dec, "bitloop")
    nop()      .side(1)       [6]   # STOPビット送出 1(nop) + 6(delay) + 1(pull) = 8clock

UART_BAUD = 115200
RESULT = StateMachine(
        0, uart_tx, freq=8 * UART_BAUD, sideset_base=Pin(12), out_base=Pin(12)
    )
    # sm.active(1)

