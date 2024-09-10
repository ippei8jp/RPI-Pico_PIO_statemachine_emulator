from asm_pio.rp2 import *

@asm_pio(
            in_shiftdir = PIO.SHIFT_LEFT,
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
            )
def in_shift():
    in_(pins, 4)                # 0x4004, //  0: in     pins, 4

button_pin = Pin(0)
RESULT = StateMachine(0, in_shift, in_base=button_pin)

