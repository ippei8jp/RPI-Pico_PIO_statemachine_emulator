from asm_pio.rp2 import *

@asm_pio(
            out_shiftdir=PIO.SHIFT_RIGHT,
            autopull=True,
            pull_thresh=10, 
            in_shiftdir = PIO.SHIFT_LEFT,
            autopush=True,
            push_thresh=3, 
            )
def push_pull_auto():
    out(x, 5)                   # 0x6025, //  0: out    x, 5                       
    in_(x, 3)                   # 0x4023, //  1: in     x, 3                       

RESULT = StateMachine(0, push_pull_auto)

