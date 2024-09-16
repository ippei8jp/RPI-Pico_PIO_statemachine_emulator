from rp2 import *

@asm_pio(sideset_init=[PIO.OUT_LOW for _ in range(4)])
def SteppingMotor():
    nop() .side(0b0001) .delay(1)
    nop() .side(0b0010) .delay(1)
    nop() .side(0b0100) .delay(1)
    nop() .side(0b1000) .delay(1)

    return 0

RESULT = StateMachine(0, SteppingMotor, sideset_base=Pin(12))

