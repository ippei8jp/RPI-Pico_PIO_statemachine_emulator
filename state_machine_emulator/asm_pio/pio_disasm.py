# PIO_ASMの逆アセンブル処理

# オペコードーニーモニック変換テーブル
mnemonic_str = [
                "jmp  ",    # 000
                "wait ",    # 001
                "in   ",    # 010
                "out  ",    # 011
                "XXXX ",    # 100   別途定義
                "mov  ",    # 101
                "irq  ",    # 110
                "set  ",    # 111
               ]

# サブオペコードーニーモニック変換テーブル(オペコード 0b100用)
mnemonic_100_str = [
                "push ",    # 100_..._0xx0_...
                "mov ",     # 100_..._0xx1_...
                "pull ",    # 100_..._1xx0_...
                "mov  ",    # 100_..._1xx1_...
                   ]

def extract_instruction(instruction, MSB, LSB) :
    return (instruction >> LSB) & ((1 << (MSB - LSB + 1)) - 1)

def instr_000(instruction) :
    op_code = 0b000             # jmp命令
    cond    = extract_instruction(instruction, 7, 5)
    addr    = extract_instruction(instruction, 4, 0)
    cond_str =  [
                    "",         # 000
                    "!x, ",      # 001
                    "x--, ",     # 010
                    "!y,",       # 011
                    "y--, ",     # 100
                    "x!=y, ",    # 101
                    "pin, ",     # 110
                    "!osre, ",   # 111
                ]
                
    inst_str = f'{mnemonic_str[op_code]}{cond_str[cond]}{addr:2d}'
    return inst_str


def instr_001(instruction) :
    op_code = 0b001             # wait命令
    pol     = extract_instruction(instruction, 7, 7)
    src     = extract_instruction(instruction, 6, 5)
    idx     = extract_instruction(instruction, 4, 0)
    src_str =   [
                    "gpio, ",    # 00
                    "pin, ",     # 01
                    "irq, ",     # 10
                    "jmppin, ",  # 11 ver.1以降
                ]
    if src != 0b10 :
        inst_str = f'{mnemonic_str[op_code]}{pol} {src_str[src]}{idx}'
    else :
        opt = extract_instruction(idx, 4, 3)
        idx = extract_instruction(idx, 2, 0)
        opt_str =   [
                        "",     # 00
                        "PREV", # 01 Ver.1以降
                        "REL",  # 10
                        "NEXT", # 11 Ver.1以降
                    ]
        inst_str = f'{mnemonic_str[op_code]}{pol} {src_str[src]}{idx}'
        if len(opt_str[opt]) > 0 :
            inst_str = inst_str + f' {opt_str[opt]}'
    return inst_str

def instr_010(instruction) :
    op_code = 0b010             # in命令
    src     = extract_instruction(instruction, 7, 5)
    bitcnt  = extract_instruction(instruction, 4, 0)
    bitcnt  = bitcnt if bitcnt != 0 else 32     # 0は32を意味する
    src_str =   [
                    "pins, ",   # 000
                    "x, ",      # 001
                    "y, ",      # 010
                    "null, ",   # 011
                    "????, ",   # 100
                    "????, ",   # 101
                    "isr, ",    # 110
                    "osr, ",    # 111
                ]
    inst_str = f'{mnemonic_str[op_code]}{src_str[src]}{bitcnt:2d}'
    return inst_str

def instr_011(instruction) :
    op_code = 0b011             # out命令
    dst     = extract_instruction(instruction, 7, 5)
    bitcnt  = extract_instruction(instruction, 4, 0)
    bitcnt = bitcnt if bitcnt != 0 else 32      # 0は32を意味する
    dst_str =   [
                    "pins, ",   # 000
                    "x, ",      # 001
                    "y, ",      # 010
                    "null, ",   # 011
                    "pindirs, ",# 100
                    "pc, ",     # 101
                    "isr, ",    # 110
                    "osr, ",    # 111
                ]
    inst_str = f'{mnemonic_str[op_code]}{dst_str[dst]}{bitcnt:2d}'
    return inst_str

def instr_100(instruction) :
    op_code = 0b100             # push/pull/mov命令
    op_code_sub1 = extract_instruction(instruction, 7, 7)   # bit7と4がサブオペコード
    op_code_sub0 = extract_instruction(instruction, 4, 4)
    op_code_sub  = (op_code_sub1 << 1) + op_code_sub0
    if   op_code_sub == 0b00 :      # push命令
        iffl = extract_instruction(instruction, 6, 6)   # (instruction >>  6) & 0x01
        blk  = extract_instruction(instruction, 5, 5)   # (instruction >>  5) & 0x01
        iffl_str =  [
                        "",         # 0
                        "iffull ",  # 1
                    ]
        blk_str =   [
                        "noblock",  # 0
                        "block",    # 1
                    ]
        inst_str = f'{mnemonic_100_str[op_code_sub]}{iffl_str[iffl]}{blk_str[blk]}'
    elif op_code_sub == 0b01 :      # mov命令
        idx     = extract_instruction(instruction, 1, 0)
        idxi    = extract_instruction(instruction, 3, 3)
        if idxi == 0 :
            idx_str = 'y'
        else :
            idx_str = str(idx)
        inst_str = f'{mnemonic_100_str[op_code_sub]}rxfifo {idx_str}, isr'
    elif op_code_sub == 0b10 :      # pull命令
        ifem =  extract_instruction(instruction, 6, 6)  # (instruction >>  6) & 0x01
        blk  =  extract_instruction(instruction, 5, 5)  # (instruction >>  5) & 0x01
        ifem_str =  [
                        "",         # 0
                        "ifempty ", # 1
                    ]
        blk_str =   [
                        "noblock",  # 0
                        "block",    # 1
                    ]
        inst_str = f'{mnemonic_100_str[op_code_sub]}{ifem_str[ifem]}{blk_str[blk]}'
    else :   # op_code_sub == 0b11       # mov命令   Ver.1以降
        idx     = extract_instruction(instruction, 1, 0)
        idxi    = extract_instruction(instruction, 3, 3)
        if idxi == 0 :
            idx_str = 'y'
        else :
            idx_str = str(idx)
        inst_str = f'{mnemonic_100_str[op_code_sub]}osr, rxfifo {idx_str}'
    return inst_str

def instr_101(instruction) :
    op_code = 0b101             # mov命令
    dst     = extract_instruction(instruction, 7, 5)
    op      = extract_instruction(instruction, 4, 3)
    src     = extract_instruction(instruction, 2, 0)
    dst_str =   [
                    "pins, ",       # 000
                    "x, ",          # 001
                    "y, ",          # 010
                    "pindirs, ",    # 011
                    "exec, ",       # 100
                    "pc, ",         # 101
                    "isr, ",        # 110
                    "osr, ",        # 111
                ]
    op_str =    [
                    "",             # 000
                    "~",            # 001
                    ":",            # 010
                    "?",            # 011
                ]
    src_str =   [
                    "pins",         # 000
                    "x",            # 001
                    "y",            # 010
                    "null",         # 011
                    "????",         # 100 未定義
                    "status",       # 101
                    "isr",          # 110
                    "osr",          # 111
                ]
    if op == 0b00 and dst == src :
        # mov y, y は nop
        inst_str = f'nop'
    else :
        inst_str = f'{mnemonic_str[op_code]}{dst_str[dst]}{op_str[op]}{src_str[src]}'
    return inst_str

def instr_110(instruction) :
    op_code = 0b110             # irq命令
    clrwait = extract_instruction(instruction, 6, 5)    # (instruction >> 5) & 0x03
    idxmd   = extract_instruction(instruction, 4, 3)    # (instruction >> 3) & 0x03
    idx     = extract_instruction(instruction, 2, 0)    # (instruction >> 0) & 0x07
    clrwait_str = [
                    "nowait ",      # 00 set/nowaitは同じ
                    "wait ",        # 01 
                    "clear ",       # 10 
                    "clear ",       # 11  両方セットされていたらclear
                  ]
    idxmd_str = [
                    "",             # 00 
                    "PREV",         # 01 
                    "REL",          # 10 
                    "NEXT",         # 11 
                ]
    inst_str = f'{mnemonic_str[op_code]}{clrwait_str[clrwait]}{idx}'
    if len(idxmd_str[idxmd]) > 0 :
        inst_str = inst_str + f' {idxmd_str[idxmd]}'
    return inst_str

def instr_111(instruction) :
    op_code = 0b111             # set命令
    dst     = extract_instruction(instruction, 7, 5)   # (instruction >> 5) & 0x07
    data    = extract_instruction(instruction, 4, 0)   # (instruction >> 0) & 0x1f
    dst_str =   [
                    "pins, ",       # 000
                    "x, ",          # 001
                    "y, ",          # 010
                    "????, ",       # 011 未定義
                    "pindirs, ",    # 100
                    "????, ",       # 101 未定義
                    "????, ",       # 110 未定義
                    "????, ",       # 111
                ]
    inst_str = f'{mnemonic_str[op_code]}{dst_str[dst]}{data:2d}'
    return inst_str

def pio_disasm(instruction, addr=None, sideset_count=0, sideset_opt=False) :
    # オペコード
    op_code = extract_instruction(instruction, 15, 13)      # (instruction >> 13) & 0x07

    if   op_code == 0b000 :
        inst_str = instr_000(instruction)
    elif op_code == 0b001 :
        inst_str = instr_001(instruction)
    elif op_code == 0b010 :
        inst_str = instr_010(instruction)
    elif op_code == 0b011 :
        inst_str = instr_011(instruction)
    elif op_code == 0b100 :
        inst_str = instr_100(instruction)
    elif op_code == 0b101 :
        inst_str = instr_101(instruction)
    elif op_code == 0b110 :
        inst_str = instr_110(instruction)
    else : # op_code == 0b111
        inst_str = instr_111(instruction)
    
    # side_setとdelayの付加
    ss_delay = extract_instruction(instruction, 12, 8)
    
    sideset_count = int(sideset_count)      # シフト/スライスに使うのでintにしておく(念のため)
    sideset_shift = 5 - sideset_count       # side_setのシフト値
    sideset_ptn = None                      # 初期値
    delay = 0                               # 初期値
    
    if sideset_opt :
        # sideset_optがセットされていてss_delayの MSBがセットされていたらsideset指定あり
        if ss_delay & (1 << 4) :
            # MSBがセットされている
            ss_delay = ss_delay & ((1 << 4) - 1)    # MSBを落とす
            sideset_ptn = ss_delay >> sideset_shift
            delay       = ss_delay &  ((1 << sideset_shift) - 1)
        else :
            # MSBがセットされていない
            delay = ss_delay                # すべてdelay

        if sideset_ptn is not None :        # sideset指定あり
            ss_str = f'{sideset_ptn:08b}'           # 2進数文字列化
            ss_str = ss_str[-(sideset_count - 1):]  # 必要分だけ切り出し(MSBの分を削除)
            inst_str = inst_str + f'  side {ss_str}'
        if delay > 0 :                      # 0のときは表示しない
            inst_str = inst_str + f'  [{delay:2d}]'
    else :
        # sideset_optがセットされていなければてss_delayの MSB側sideset_countビット分がsideset指定
        if sideset_count > 0 :
            # sideset使用する
            sideset_ptn = ss_delay >> sideset_shift
            delay       = ss_delay &  ((1 << sideset_shift) - 1)
        else :
            # sideset使用しない
            delay = ss_delay                # すべてdelay

        if sideset_ptn is not None :        # sideset指定あり
            ss_str = f'{sideset_ptn:08b}'           # 2進数文字列化
            ss_str = ss_str[-sideset_count:]        # 必要分だけ切り出し
            inst_str = inst_str + f'  side {ss_str}'
        if delay > 0 :                      # 0のときは表示しない
            inst_str = inst_str + f'  [{delay}]'
    
    # アドレスが指定されていたらアドレス付加
    if isinstance(addr, int) :
        inst_str = f'{addr:3d}: ' + inst_str
    
    return inst_str



