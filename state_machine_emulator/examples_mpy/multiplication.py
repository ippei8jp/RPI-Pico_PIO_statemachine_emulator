from asm_pio.rp2 import *

@asm_pio(
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
            )
def multiplication():
                            # //     .wrap_target
    label("label_0")
    pull(block)             # 0x80a0, //  0: pull   block
    mov(x, osr)             # 0xa027, //  1: mov    x, osr
    mov(isr, x)             # 0xa0c1, //  2: mov    isr, x
    pull(block)             # 0x80a0, //  3: pull   block
    mov(y, osr)             # 0xa047, //  4: mov    y, osr
    jmp(y_dec, "label_9")   # 0x0089, //  5: jmp    y--, 9
    mov(isr, null)          # 0xa0c3, //  6: mov    isr, null
    push(block)             # 0x8020, //  7: push   block
    jmp("label_0")          # 0x0000, //  8: jmp    0
    label("label_9")
    mov(osr, y)             # 0xa0e2, //  9: mov    osr, y
    mov(y, invert(null))    # 0xa04b, // 10: mov    y, !null
    label("label_11")
    jmp(x_dec, "label_16")            # 0x0050, // 11: jmp    x--, 16
    mov(x, osr)             # 0xa027, // 12: mov    x, osr
    jmp(x_dec, "label_20")  # 0x0054, // 13: jmp    x--, 20
    mov(isr, invert(y))     # 0xa0ca, // 14: mov    isr, !y
    push(block)             # 0x8020, // 15: push   block
    wrap()                  #         //     .wrap
    label("label_16")
    jmp(y_dec, "label_11")  # 0x008b, // 16: jmp    y--, 11
    mov(isr, invert(null))  # 0xa0cb, // 17: mov    isr, !null
    push(block)             # 0x8020, // 18: push   block
    jmp("label_0")          # 0x0000, // 19: jmp    0
    label("label_20")
    mov(osr, x)            # 0xa0e1, // 20: mov    osr, x
    mov(x, isr)            # 0xa026, // 21: mov    x, isr
    jmp("label_11")        # 0x000b, // 22: jmp    11

RESULT = StateMachine(0, multiplication)

