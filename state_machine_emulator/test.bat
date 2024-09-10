
REM mpyモード
python main.py --save --no-disp examples_mpy\button_debounce.py
python main.py --save --no-disp examples_mpy\in_shift.py
python main.py --save --no-disp examples_mpy\irq_set_and_clear.py
python main.py --save --no-disp examples_mpy\ledpanel.py
python main.py --save --no-disp examples_mpy\multiplication.py
python main.py --save --no-disp examples_mpy\push_pull_auto.py
python main.py --save --no-disp examples_mpy\rotational_shift.py
python main.py --save --no-disp examples_mpy\side_step.py
python main.py --save --no-disp examples_mpy\square_wave.py
python main.py --save --no-disp examples_mpy\stepper.py

REM pio_asmモード
python main.py --save --no-disp examples\button_debounce
python main.py --save --no-disp examples\in_shift
python main.py --save --no-disp examples\irq_set_and_clear
python main.py --save --no-disp examples\ledpanel
python main.py --save --no-disp examples\multiplication
python main.py --save --no-disp examples\push_pull_auto
python main.py --save --no-disp examples\rotational_shift
python main.py --save --no-disp examples\side_step
python main.py --save --no-disp examples\square_wave
python main.py --save --no-disp examples\stepper

"C:\Program Files\WinMerge\WinMergeU.exe" examples\button_debounce\result.json   examples_mpy\button_debounce.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\in_shift\result.json          examples_mpy\in_shift.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\irq_set_and_clear\result.json examples_mpy\irq_set_and_clear.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\ledpanel\result.json          examples_mpy\ledpanel.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\multiplication\result.json    examples_mpy\multiplication.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\push_pull_auto\result.json    examples_mpy\push_pull_auto.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\rotational_shift\result.json  examples_mpy\rotational_shift.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\side_step\result.json         examples_mpy\side_step.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\square_wave\result.json       examples_mpy\square_wave.json
"C:\Program Files\WinMerge\WinMergeU.exe" examples\stepper\result.json           examples_mpy\stepper.json
