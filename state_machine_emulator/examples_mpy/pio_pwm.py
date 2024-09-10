from asm_pio.rp2 import *

@asm_pio(sideset_init=PIO.OUT_LOW)
def pwm_prog():
    pull(noblock) .side(0)
    mov(x, osr)  # Keep most recent pull data stashed in X, for recycling by noblock
    mov(y, isr)  # ISR must be preloaded with PWM count max
    label("pwmloop")
    jmp(x_not_y, "skip")
    nop()         .side(1)
    label("skip")
    jmp(y_dec, "pwmloop")

    return 0


RESULT = StateMachine(0, pwm_prog, sideset_base=Pin(15))
print("done")

