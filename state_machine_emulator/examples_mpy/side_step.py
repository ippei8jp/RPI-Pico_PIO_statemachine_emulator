from asm_pio.rp2 import *

@asm_pio(
            sideset_init=PIO.OUT_LOW,
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
            )
def side_step():
    nop()         .side(0)
    nop()
    nop()         .side(1)


RESULT = StateMachine(0, side_step, sideset_base=Pin(4))
# print("done")

