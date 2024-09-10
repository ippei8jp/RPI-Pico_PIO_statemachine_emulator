from asm_pio.rp2 import *

@asm_pio(
            sideset_init=[PIO.OUT_LOW for _ in range(3)],
            autopull=True,
            pull_thresh=22, 
            out_init=[PIO.OUT_LOW for _ in range(11)],
            out_shiftdir=PIO.SHIFT_RIGHT,
            in_shiftdir = PIO.SHIFT_RIGHT,
            )
def ledpanel():
    mov(isr, invert(null)) .side(4)         # 0xb0cb, //  0: mov    isr, !null      side 4     
    in_(null, 25)   .side(4)                # 0x5079, //  1: in     null, 25        side 4     
    wrap_target()                           #         //     .wrap_target
    mov(x, isr)     .side(0)                # 0xa026, //  2: mov    x, isr          side 0     
    label("label_3")
    out(pins, 11)   .side(6)    .delay(2)   # 0x7a0b, //  3: out    pins, 11        side 6 [2] 
    jmp(x_dec, "label_3")   .side(4)        # 0x1043, //  4: jmp    x--, 3          side 4     
    out(x, 11)      .side(1)                # 0x642b, //  5: out    x, 11           side 1     
    out(x, 11)      .side(1)                # 0x642b, //  6: out    x, 11           side 1     
    label("label_7")
    nop()           .side(0)    .delay(3)   # 0xa342, //  7: nop                    side 0 [3] 
    nop()           .side(0)    .delay(3)   # 0xa342, //  8: nop                    side 0 [3] 
    nop()           .side(0)    .delay(3)   # 0xa342, //  9: nop                    side 0 [3] 
    jmp(x_dec, "label_7")   .side(0)        # 0x0047, // 10: jmp    x--, 7          side 0     
                                            #         //     .wrap
    
RESULT = StateMachine(0, ledpanel, sideset_base=Pin(13), out_base=Pin(0))

