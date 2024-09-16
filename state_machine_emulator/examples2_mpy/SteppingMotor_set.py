from rp2 import *

@asm_pio(set_init=[PIO.OUT_LOW for _ in range(4)])
def SteppingMotor():
    set(pins, 0b0001) .delay(1)
    set(pins, 0b0010) .delay(1)
    set(pins, 0b0100) .delay(1)
    set(pins, 0b1000) .delay(1)

    return 0

RESULT = StateMachine(0, SteppingMotor, set_base=Pin(12))

