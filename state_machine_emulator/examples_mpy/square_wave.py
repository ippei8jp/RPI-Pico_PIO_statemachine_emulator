from asm_pio.rp2 import *

@asm_pio(
            set_init=PIO.OUT_LOW,
            in_shiftdir = PIO.SHIFT_RIGHT,      # シミュレータのデフォルトに合わせるため指定
            out_shiftdir = PIO.SHIFT_LEFT,      # シミュレータのデフォルトに合わせるため指定
        )
def square_wave():
                                #         //     .wrap_target
    set(pindirs, 1)             # 0xe081, //  0: set    pindirs, 1                 
    label("label_1")
    set(pins, 1)    .delay(1)   # 0xe101, //  1: set    pins, 1                [1] 
    set(pins, 0)                # 0xe000, //  2: set    pins, 0                    
    jmp("label_1")              # 0x0001, //  3: jmp    1                          
                                #         //     .wrap

RESULT = StateMachine(0, square_wave, set_base=Pin(0))

