from asm_pio.rp2 import *

@asm_pio(
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
        )
def irq_set_and_clear():
    irq(0)              # 0xc000, //  0: irq    nowait 0
    irq(1)              # 0xc001, //  1: irq    nowait 1
    irq(2)              # 0xc002, //  2: irq    nowait 2
    irq(3)              # 0xc003, //  3: irq    nowait 3
    irq(4)              # 0xc004, //  4: irq    nowait 4
    irq(5)              # 0xc005, //  5: irq    nowait 5
    irq(6)              # 0xc006, //  6: irq    nowait 6
    irq(7)              # 0xc007, //  7: irq    nowait 7
    irq(block, 0)       # 0xc020, //  8: irq    wait 0
    irq(block, 1)       # 0xc021, //  9: irq    wait 1
    irq(block, 2)       # 0xc022, //  10: irq    wait 2
    irq(block, 3)       # 0xc023, //  11: irq    wait 3
    irq(block, 4)       # 0xc024, //  12: irq    wait 4
    irq(block, 5)       # 0xc025, //  13: irq    wait 5
    irq(block, 6)       # 0xc026, //  14: irq    wait 6
    irq(block, 7)       # 0xc027, //  15: irq    wait 7

RESULT = StateMachine(0, irq_set_and_clear)

