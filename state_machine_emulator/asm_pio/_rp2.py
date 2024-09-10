# StateMachine class コンストラクタによる
#       ・pio asm コード化
#       ・pio asm コードの逆アセンブル
#       ・パラメータ設定
# PIO class エラー回避のための定数値定義

from pio_disasm import pio_disasm

class PIO() :
    IN_LOW      = 0
    IN_HIGH     = 1
    OUT_LOW     = 2
    OUT_HIGH    = 3

    SHIFT_LEFT  = 0
    SHIFT_RIGHT = 1

    JOIN_NONE   = 0
    JOIN_TX     = 1
    JOIN_RX     = 2

    IRQ_SM0 = 0x100
    IRQ_SM1 = 0x200
    IRQ_SM2 = 0x400
    IRQ_SM3 = 0x800

class StateMachine() :
    def __init__(self, 
            id, 
            pio_program, 
            freq=-1, 
            in_base=None, 
            out_base=None, 
            set_base=None, 
            jmp_pin=None, 
            sideset_base=None, 
            in_shiftdir=None, 
            out_shiftdir=None, 
            push_thresh=None, 
            pull_thresh=None
        ) :
        
        PIO_ASM_RESULT = pio_program()
        
        self.id                      = id             # 未使用
        self.freq                    = freq           # 未使用

        self.sideset_opt             = PIO_ASM_RESULT[3] & (1 << 30) != 0  # bit 30

        self.set_base                = set_base
        if PIO_ASM_RESULT[6] is None:
            self.set_count = 0
        elif isinstance(PIO_ASM_RESULT[6], int):
            self.set_count = 1
        else:
            self.set_count = len(PIO_ASM_RESULT[6])

        self.in_base                 = in_base

        self.jmp_pin                 = jmp_pin

        self.sideset_base            = sideset_base
        if PIO_ASM_RESULT[7] is None:
            self.sideset_count = 0
        elif isinstance(PIO_ASM_RESULT[7], int):
            self.sideset_count = 1
        else:
            self.sideset_count = len(PIO_ASM_RESULT[7])
        if self.sideset_opt :
            self.sideset_count = self.sideset_count + 1     # sideset_optがTrueなら1加算
        
        self.out_base                = out_base
        if PIO_ASM_RESULT[5] is None:
            self.out_count = 0
        elif isinstance(PIO_ASM_RESULT[5], int):
            self.out_count = 1
        else:
            self.out_count = len(PIO_ASM_RESULT[5])
        
        if pull_thresh is None :
            self.pull_threshold          = (PIO_ASM_RESULT[4] >> 25) & 0x1f        # bit 29-25 
            self.pull_threshold          = self.pull_threshold if self.pull_threshold != 0 else 32      # 0のとき32指定
        else :
            # StateMachine のパラメータで上書き
            self.pull_threshold         = pull_thresh

        if push_thresh is None :
            self.push_threshold          = (PIO_ASM_RESULT[4] >> 20) & 0x1f        # bit 24-20
            self.push_threshold          = self.push_threshold if self.push_threshold != 0 else 32      # 0のとき32指定
        else :
            # StateMachine のパラメータで上書き
            self.push_threshold         = push_thresh

        if out_shiftdir is None :
            self.out_shift_right         = (PIO_ASM_RESULT[4] & (1 << 19) ) != 0   # bit 19
        else :
            # StateMachine のパラメータで上書き
            self.out_shift_right         = out_shiftdir != 0
        
        if in_shiftdir is None :
            self.in_shift_right          = (PIO_ASM_RESULT[4] & (1 << 18) ) != 0   # bit 18
        else :
            # StateMachine のパラメータで上書き
            self.in_shift_right          = in_shiftdir != 0
            
        self.out_shift_autopull      = (PIO_ASM_RESULT[4] & (1 << 17) ) != 0   # bit 17
        self.in_shift_autopush       = (PIO_ASM_RESULT[4] & (1 << 16) ) != 0   # bit 16

        pio_program = [[f'0x{x:04x}', pio_disasm(x, addr, self.sideset_count, self.sideset_opt)] for addr, x in enumerate(PIO_ASM_RESULT[0])]  # 文字列 & 逆アセンブル
        self.pio_program             = pio_program
        self.pio_program_length      = len(PIO_ASM_RESULT[0])
        self.pio_program_origin      = -1                           # 未使用
        self.pio_program_wrap_target = (PIO_ASM_RESULT[3] >>  7) & 0x1f    # bit 11-7
        self.pio_program_wrap        = (PIO_ASM_RESULT[3] >> 12) & 0x1f    # bit 16-12

