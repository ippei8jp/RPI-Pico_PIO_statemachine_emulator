from rp2 import *

# データ長8bit/パリティなし/ストップビット1/LSBファースト
@asm_pio(
    autopush=True,
    push_thresh=8,
    in_shiftdir=PIO.SHIFT_RIGHT,
    fifo_join=PIO.JOIN_RX,
)
def uart_rx_mini():
    # fmt: off
    # Wait for start bit
    wait(0, pin, 0)
    # Preload bit counter, delay until eye of first data bit
    set(x, 7)                 [10]
    # Loop 8 times
    label("bitloop")
    # Sample data
    in_(pins, 1)
    # Each iteration is 8 cycles
    jmp(x_dec, "bitloop")     [6]
    # fmt: on


PIO_RX_PIN = Pin(13)
UART_BAUD = 115200
RESULT = StateMachine(
        0,
        uart_rx_mini,
        freq=8 * UART_BAUD,
        in_base=PIO_RX_PIN,  # For WAIT, IN
        jmp_pin=PIO_RX_PIN,  # For JMP
    )
    # sm.irq(handler)
    # sm.active(1)

