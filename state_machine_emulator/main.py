"""
TODO:
- check the 'status' with 'set_N' and 'status_sel' with the actual hardware!
    Wait! not just the status, but many, many things should be tested with the pico hardware
- "FIFO IRQs" Figure 38. in rp2040-datasheet.pdf
- start without c-program or pin-program
- try except around emulation
- make the way statements in c_program are made exactly the same as how they appear in the GUI
- use the pio assembler to read raw programs and compile them (i.e. read prog.pio instead of prog.pio.h)
"""

import sys
import os

from argparse import ArgumentParser, SUPPRESS, RawTextHelpFormatter
import pathlib
import importlib
import json

from interface import Emulator_Interface
from emulation import emulation
# configで設定していた内容はコマンドラインオプションに移動
# from config import EMULATION_STEPS, SAVE_TEST_DATA
from state_machine import state_machine

"""
This code emulates a state machine of a RP4020
It provides a GUI to step through the emulation results.
"""

def process_file_pio_h(filename, c_program):
    """ read and parse a pioasm generated header file """
    pio_program = list()
    pio_program_length = None
    pio_program_origin = -1 # note: not actually used
    pio_program_wrap_target = 0
    pio_program_wrap = None

    try:
        with open(filename, 'r') as pio_file:
            line = pio_file.readline()
            while line:
                if line[0] == '/' and line[1] == '/':
                    pass
                elif ".length" in line:
                    d = line.strip().split('=')
                    pio_program_length = int(d[1].replace(',', ''))
                elif ".origin" in line: # note: origin is not actually used
                    d = line.strip().split('=')
                    pio_program_origin = int(d[1].replace(',', ''))
                elif "#define" in line:
                    if "wrap_target" in line:
                        d = line.strip().split(' ')
                        pio_program_wrap_target = int(d[2])
                    elif "wrap" in line:
                        d = line.strip().split(' ')
                        pio_program_wrap = int(d[2])
                elif "static const uint16_t" in line:
                    line = pio_file.readline()
                    while '};' not in line:
                        d = line.strip().split(', //')
                        if len(d) == 2:
                            pio_program.append(d)
                        line = pio_file.readline()
                elif "static inline pio_sm_config" in line:
                    # add to the c-program at t=0
                    line2 = pio_file.readline()
                    while '}' not in line2:
                        if 'sm_config_set_sideset' in line2:
                            parts = line2.split(',')
                            a1 = int(parts[1].strip())
                            c_program.append([0, 'sideset_count', a1])
                            a2 = parts[2].strip().lower() == 'true'
                            c_program.append([0, 'sideset_opt', a2])
                            a3 = parts[3].split(')')[0].strip().lower() == 'true'
                            c_program.append([0, 'sideset_pindirs', a3])
                        line2 = pio_file.readline()
                line = pio_file.readline()
        if len(pio_program) != pio_program_length:
            print("Warning: length specification in pio file doesn't match actual length, continuing anyway")
        if len(pio_program) > 32:
            print("Warning: program too long, continuing anyway")
    except IOError as e:
        print("I/O Error reading pio program file:", e.errno, e.strerror)
    except:
        print("Error reading pio program file:", sys.exc_info()[0])
    return pio_program, pio_program_length, pio_program_origin, pio_program_wrap_target, pio_program_wrap


def process_file_pin_program(filename, pin_program):
    """ read the pin program file and parse it """
    try:
        allowed_parts1 = ['GPIO'+str(i) for i in range(32)]
        allowed_parts1.append('all')
        with open(filename, 'r') as pin_program_file:
            for line in pin_program_file:
                # remove all # characters and all text after it (i.e. comments)
                line = line.split("#", 1)[0]
                # check if the line still has some content
                if line.strip():
                    parts = line.split(',')
                    parts[1] = parts[1].strip()
                    if parts[1] in allowed_parts1:
                        parts[0] = int(parts[0])   # time at which the command should be run
                        parts[2] = int(parts[2])   # argument of the command
                        pin_program.append(parts)
                    else:
                        print("Warning: Unknown command in pin_program: ", parts, 'continuing anyway')
    except IOError as e:
        print("I/O Error reading pin program file:", e.errno, e.strerror)
    except:
        print("Error reading pin program file:", sys.exc_info()[0])


def process_file_c_program(filename, c_program):
    """ read the c program file and parse it """
    try:
        with open(filename, 'r') as c_program_file:
            for line in c_program_file:
                # remove all # characters and all text after it (i.e. comments)
                line = line.split("#", 1)[0]
                # check if the line still has some content
                if line.strip():
                    # a "c-instruction" has two or three parts:
                    # timestamp, command, and possibly an argument of the command
                    # the timestamp and argument must be integers/bool, the command is a (stripped) string
                    parts = line.strip().split(',')
                    parts[1] = parts[1].strip()
                    # check if the command is valid 
                    if parts[1].strip() in ['put', 'get', 'set_base', 'set_count', 'in_base', 'jmp_pin', 'sideset_base', 'out_base', 'out_count', 'out_shift_right', 'out_shift_autopull', 'pull_threshold', 'in_shift_right', 'in_shift_autopush', 'push_threshold', 'get_pc', 'set_pc', 'irq', 'set_N', 'status_sel', 'dir_out', 'dir_in', 'dir_non']:
                        parts[0] = int(parts[0])
                        parts[1] = parts[1]
                        if len(parts) == 3:
                            parts[2] = parts[2].strip()
                            # convert strings "True" and "False" to boolean, otherwise it is an int
                            if parts[2] in ["True", "true", "Yes", "yes"]:
                                parts[2] = True
                            elif parts[2] in ["False", "false", "No", "no"]:
                                parts[2] = False
                            else:
                                parts[2] = int(parts[2])
                        c_program.append(parts)
                    else:
                        print("Warning: Unknown command in c_program: ", parts, "continuing anyway")
    except IOError as e:
        print("I/O Error reading c program file:", e.errno, e.strerror)
    except:
        print("Error reading c program file:", sys.exc_info()[0])

# ================================================================================
def load_pioasm_program(pio_h_filename, sm_number) :
    # the pio program (with associated data) is a dict
    program_definitions = dict()
    # the c_program and pin_program are lists
    c_program = list()
    pin_program = list()

    # process the pio.h file (which may already contribute to the c_program)
    pio_program, pio_program_length, pio_program_origin, pio_program_wrap_target, pio_program_wrap = process_file_pio_h(pio_h_filename, c_program)
    
    program_definitions['pio_program'] = pio_program
    program_definitions['pio_program_length'] = pio_program_length
    program_definitions['pio_program_origin'] = pio_program_origin  # note: not used
    program_definitions['pio_program_wrap_target'] = pio_program_wrap_target
    program_definitions['pio_program_wrap'] = pio_program_wrap
    program_definitions['pio_sm_number'] = sm_number

    return program_definitions, c_program, pin_program

# ================================================================================
def load_mpy_program(py_modulename) :
    # the pio program (with associated data) is a dict
    program_definitions = dict()
    # the c_program and pin_program are lists
    c_program = list()
    pin_program = list()

    try :
        pio_settings = importlib.import_module(py_modulename)
    except Exception as e:
        print("module import error")
        print(e)
        sys.exit(1)
    
    program_definitions['pio_program'] = pio_settings.RESULT.pio_program
    program_definitions['pio_program_length'] = pio_settings.RESULT.pio_program_length
    program_definitions['pio_program_origin'] = pio_settings.RESULT.pio_program_origin  # note: not used
    program_definitions['pio_program_wrap_target'] = pio_settings.RESULT.pio_program_wrap_target
    program_definitions['pio_program_wrap'] = pio_settings.RESULT.pio_program_wrap
    program_definitions['pio_sm_number'] = pio_settings.RESULT.id
    
    if pio_settings.RESULT.sideset_base is not None :
        c_program.append([0, 'sideset_count', pio_settings.RESULT.sideset_count])
        c_program.append([0, 'sideset_opt', pio_settings.RESULT.sideset_opt])
        c_program.append([0, 'sideset_pindirs', False])           # とりあえずFalseで
        c_program.append([0, 'sideset_base', pio_settings.RESULT.sideset_base])
    if pio_settings.RESULT.out_base is not None :
        c_program.append([0, 'out_base', pio_settings.RESULT.out_base])
        c_program.append([0, 'out_count', pio_settings.RESULT.out_count])
    if pio_settings.RESULT.set_base is not None :
        c_program.append([0, 'set_base', pio_settings.RESULT.set_base])
        c_program.append([0, 'set_count', pio_settings.RESULT.set_count])
    if pio_settings.RESULT.in_base is not None :
        c_program.append([0, 'in_base', pio_settings.RESULT.in_base])
    if pio_settings.RESULT.jmp_pin is not None :
        c_program.append([0, 'jmp_pin', pio_settings.RESULT.jmp_pin])
    
    c_program.append([0, 'out_shift_right',     pio_settings.RESULT.out_shift_right])
    c_program.append([0, 'out_shift_autopull',  pio_settings.RESULT.out_shift_autopull])
    c_program.append([0, 'pull_threshold',      pio_settings.RESULT.pull_threshold])
    c_program.append([0, 'in_shift_right',      pio_settings.RESULT.in_shift_right])
    c_program.append([0, 'in_shift_autopush',   pio_settings.RESULT.in_shift_autopush])
    c_program.append([0, 'push_threshold',      pio_settings.RESULT.push_threshold])
    
    return program_definitions, c_program, pin_program

# ================================================================================
# ================================================================================
def build_argparser():
    parser = ArgumentParser(add_help=False, formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('pio_prog', type=str, help='PIO program file')
    parser.add_argument('-h', '--help', action='help', default=SUPPRESS, 
                        help='Show this help message and exit.')
    parser.add_argument("--step", default=500, type=int, 
                        help="Optional.\n"
                             "emulation steps\n"
                             "Default is 500steps")
    parser.add_argument("--sm_number", default=0, type=int, 
                        help="Optional.\n"
                             "Statemachine number\n"
                             "pioasm mode/dir mode only\n"
                             "in mpy mode, specified in constructor of StateMachine class\n"
                             "Default is 0")
    parser.add_argument("--dump", action='store_true', 
                        help="Optional.\n"
                             "dump emulation data")
    parser.add_argument("--save", action='store_true', 
                        help="Optional.\n"
                             "save emulation data")
    parser.add_argument("--no-disp", action='store_true', 
                        help="Optional.\n"
                             "no result display")
    parser.add_argument("--c_prog", default=None, type=str, 
                        help="Optional.\n"
                             "C program definition file\n"
                             "Default is to change the extension of the target program fil\n"
                             "to '.c_prpgram'.")
    parser.add_argument("--pin_prog", default=None, type=str, 
                        help="Optional.\n"
                             "PIN program definition file\n"
                             "Default is to change the extension of the pio program file\n"
                             "to '.pin_prpgram'.")
    return parser
# ================================================================================

if __name__ == "__main__":
    from enum import Enum
    # ファイルモード
    class file_mode(Enum):
        mpy = 1
        dir = 2
        pioasm = 3

    # コマンドラインオプションの解析
    args = build_argparser().parse_args()
    if   args.pio_prog.endswith(".py") :
        # ファイル名が".py"で終わっている
        input_file_mode = file_mode.mpy
    elif args.pio_prog.endswith(".pio.h") :
        input_file_mode = file_mode.pioasm
    else :
        if os.path.isdir(args.pio_prog) :
            input_file_mode = file_mode.dir
        else :
            print("unknown file type")
            sys.exit(1)

    # コマンドラインオプションで与えられたパラメータを格納
    EMULATION_STEPS      = args.step
    SAVE_TEST_DATA       = args.dump
    STATEMACHINE_NUMBER  = args.sm_number
    c_program_filename   = args.c_prog
    pin_program_filename = args.pin_prog

    if input_file_mode == file_mode.mpy :
        # 各ファイル名
        pio_filename = pathlib.Path(args.pio_prog)
        py_modulename = pio_filename.stem
        base_dir = pio_filename.parent

        if c_program_filename is None :
            # デフォルトは~.pyファイルの拡張子を.c_programに変えたもの
            c_program_filename   = pio_filename.with_suffix('.c_program')
        if pin_program_filename is None :
            # デフォルトは~.pyファイルの拡張子を.pin_programに変えたもの
            pin_program_filename = pio_filename.with_suffix('.pin_program')

        # saveファイル名は~.pyファイルの拡張子を.jsonに変えたもの
        save_filename = pio_filename.with_suffix('.json')

        # asm_pioとpyファイルがあるディレクトリをsys.pathに追加
        sys.path.append(pathlib.Path("asm_pio").resolve().as_posix())
        sys.path.append(base_dir.resolve().as_posix())

    elif input_file_mode == file_mode.pioasm :
        # 各ファイル名
        pio_filename = pathlib.Path(args.pio_prog)
        base_dir = pio_filename.parent

        if c_program_filename is None :
            # デフォルトは~.pio.hファイルと同じディレクトリのc_program
            c_program_filename   = pio_filename.with_name('c_program')
        if pin_program_filename is None :
            # デフォルトは~.pio.hファイルと同じディレクトリのpin_program
            pin_program_filename = pio_filename.with_name('pin_program')

        # saveファイル名は~.pio.hファイルと同じディレクトリのresult.json
        save_filename = pio_filename.with_name('result.json')

    elif input_file_mode == file_mode.dir :
        # 各ファイル名
        base_dir = pathlib.Path(args.pio_prog)
        pio_files = list(base_dir.glob("*.pio.h"))
        if len(pio_files) == 1 :
            pio_filename = pio_files[0]
        else :
            print('Multiple "*.pio.h" files exist')
            sys.exit(1)

        if c_program_filename is None :
            # デフォルトは指定ディレクトリのc_program
            c_program_filename   = pio_filename.with_name('c_program')
        if pin_program_filename is None :
            # デフォルトは指定ディレクトリのpin_program
            pin_program_filename = pio_filename.with_name('pin_program')

        # saveファイル名は~.pio.hファイルと同じディレクトリのresult.json
        save_filename = pio_filename.with_name('result.json')

    # ファイル名の確認
    print(f"pio program : {pio_filename.as_posix()}")
    print(f"mode        : {str(input_file_mode)}")
    print(f"c program   : {c_program_filename.as_posix()}")
    print(f"pin program : {pin_program_filename.as_posix()}")
    if args.save :
        print(f"save file   : {save_filename.as_posix()}")

    # flag to indicate that files need to be (re)loaded. This is used when the user pushes the reload button in the GUI
    load_files = True
    while load_files:
        load_files = False
        
        if   input_file_mode == file_mode.mpy :
            program_definitions, c_program, pin_program = load_mpy_program(py_modulename)
        elif input_file_mode == file_mode.dir :
            program_definitions, c_program, pin_program = load_pioasm_program(pio_filename, STATEMACHINE_NUMBER)
        elif input_file_mode == file_mode.pioasm :
            program_definitions, c_program, pin_program = load_pioasm_program(pio_filename)
            # statemachine numberはpioプログラムファイル内で指定する
        else :
            print("unknown file type")
            sys.exit(1)
        
        # process the c_program
        process_file_c_program(c_program_filename, c_program)
        # process the pin_program
        process_file_pin_program(pin_program_filename, pin_program)

        # make the RP2040 emulation (and it will make the PIO and sm)
        my_state_machine = state_machine(program_definitions)
        my_emulation = emulation(my_state_machine, pin_program, c_program)

        # do the emulation
        my_emulation.emulate(EMULATION_STEPS)
        
        if args.save :
            # 結果をJSONファイルに保存
            emulation_result = {
                        "program_definitions":  program_definitions, 
                        "pin_program":          pin_program, 
                        "c_program":            c_program, 
                        "output":               my_emulation.output,
                        "output_c_program":     my_emulation.emulation_output_c_program,
                     }
            # print(json.dumps(emulation_result, indent=2))
            with open(save_filename, 'w') as f:
                json.dump(emulation_result, f, indent=2)

        if SAVE_TEST_DATA:
            print("program_definitions:")
            print(program_definitions)
            print("pin_program:")
            print(pin_program)
            print("c_program:")
            print(c_program)
            print("my_emulation.output:")
            print(my_emulation.output)
            print("my_emulation.emulation_output_c_program:")
            print(my_emulation.emulation_output_c_program)
        else:
            if not args.no_disp :
                # show the interface
                my_Emulator_Interface = Emulator_Interface(program_definitions, pin_program, c_program, my_emulation.output, my_emulation.emulation_output_c_program)

                # check if a reload was requested
                load_files = my_Emulator_Interface.get_reload_flag()
