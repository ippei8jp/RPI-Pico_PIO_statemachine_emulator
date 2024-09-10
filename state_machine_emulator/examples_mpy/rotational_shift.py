from asm_pio.rp2 import *

@asm_pio(
            in_shiftdir = PIO.SHIFT_RIGHT,
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
            )
def rotational_shift():
    pull(block)             # 0x80a0, //  0: pull   block
    mov(isr, osr)           # 0xa0c7, //  1: mov    isr, osr
    mov(y, isr)             # 0xa046, //  2: mov    y, isr
    push(block)             # 0x8020, //  3: push   block
    mov(isr, y)             # 0xa0c2, //  4: mov    isr, y
    set(x, 31)              # 0xe03f, //  5: set    x, 31
    label("label_6")
    in_(isr, 1)             # 0x40c1, //  6: in     isr, 1
    mov(y, isr)             # 0xa046, //  7: mov    y, isr
    push(block)             # 0x8020, //  8: push   block
    mov(isr, y)             # 0xa0c2, //  9: mov    isr, y
    jmp(x_dec, "label_6")   # 0x0046, // 10: jmp    x--, 6
    set(x, 31)              # 0xe03f, // 11: set    x, 31
    label("label_12")
    mov(isr, reverse(isr))  # 0xa0d6, // 12: mov    isr, ::isr
    in_(isr, 1)             # 0x40c1, // 13: in     isr, 1
    mov(isr, reverse(isr))  # 0xa0d6, // 14: mov    isr, ::isr
    mov(y, isr)             # 0xa046, // 15: mov    y, isr
    push(block)             # 0x8020, // 16: push   block
    mov(isr, y)             # 0xa0c2, // 17: mov    isr, y
    jmp(x_dec, "label_12")  # 0x004c, // 18: jmp    x--, 12

RESULT = StateMachine(0, rotational_shift)

