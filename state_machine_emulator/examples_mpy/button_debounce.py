from rp2 import *

@asm_pio(
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
            )
def button_debounce():
    jmp(pin, "label_6")         # 0x00c6, //  0: jmp    pin, 6
    label("label_1")
    wait(1, pin, 0)             # 0x20a0, //  1: wait   1 pin, 0
    set(x, 31)                  # 0xe03f, //  2: set    x, 31
    label("label_3")
    jmp(pin, "label_5")         # 0x00c5, //  3: jmp    pin, 5
    jmp("label_1")              # 0x0001, //  4: jmp    1
    label("label_5")
    jmp(x_dec, "label_3")         # 0x0043, //  5: jmp    x--, 3
    label("label_6")
    wait(0, pin, 0)             # 0x2020, //  6: wait   0 pin, 0
    set(x, 31)                  # 0xe03f, //  7: set    x, 31
    label("label_8")
    jmp(pin, "label_6")         # 0x00c6, //  8: jmp    pin, 6
    jmp(x_dec, "label_8")         # 0x0048, //  9: jmp    x--, 8
    jmp("label_1")              # 0x0001, // 10: jmp    1

button_pin = Pin(0)
RESULT = StateMachine(0, button_debounce, in_base=button_pin, jmp_pin=button_pin)
# print("done")

