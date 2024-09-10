from asm_pio.rp2 import *

@asm_pio(
            out_shiftdir=PIO.SHIFT_RIGHT,
            out_init=[PIO.OUT_LOW for _ in range(4)],
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            )
def stepper():
#         //     .wrap_target
    pull(block)                 # 0x80a0, //  0: pull   block
    mov(x, osr)                 # 0xa027, //  1: mov    x, osr
    pull(block)                 # 0x80a0, //  2: pull   block
    mov(y, osr)                 # 0xa047, //  3: mov    y, osr
    jmp(not_x, "label_9")       # 0x0029, //  4: jmp    !x, 9
    label("label_5")
    jmp(not_osre, "label_7")    # 0x00e7, //  5: jmp    !osre, 7
    mov(osr, y)                 # 0xa0e2, //  6: mov    osr, y
    label("label_7")
    out(pins, 4)  .delay(31)    # 0x7f04, //  7: out    pins, 4                [31]
    jmp(x_dec, "label_5")       # 0x0045, //  8: jmp    x--, 5
    label("label_9")
    irq(0)                      # 0xc000, //  9: irq    nowait 0
                                #         //     .wrap

RESULT = StateMachine(0, stepper, out_base=Pin(0))

