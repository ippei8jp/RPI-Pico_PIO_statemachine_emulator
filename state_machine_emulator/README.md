# Emulator of a Raspberry Pi Pico PIO state machine

## 準備
``matplotlib``を使用するので、あらかじめインストールしておいてください。
```
pip install matplotlib
```

## 修正点 
オリジナルに対して以下の変更を実施  

### micropython 対応
ファイルの書き方は``examples_mpy``ディレクトリを参照してください。  

### 各種パラメータのコマンドラインオプション化
``config.py``で指定していたパラメータをコマンドラインオプションに変更。  
これに伴い、``config.py``を削除。  

- ``SAVE_TEST_DATA`` の設定  
  コマンドラインオプションの``--dump``で指定します。  
  互換性のために残していますが、``--save --no-disp``の方が結果が見やすいです。  

- ``EMULATION_STEPS`` の設定  
  コマンドラインオプションの``--step=<STEP>``で指定します。  

- ``STATEMACHINE_NUMBER`` の設定  
  ``.pio.h``ファイル、ディレクトリを指定した場合は コマンドラインオプションの``--sm_number=<NUMBER>``で指定します。  
  ``.py``ファイルを指定した場合は ``StateMachine``クラスのコンストラクタで指定します。

### emulation対象ファイルの指定方法の変更
以下の方法で指定できます。  
- ``.pio.h`` ファイルを指定   
  従来の3パラメータ指定時と同じ動作ですが、
  ``c_program``と``pin_program``の指定は別途オプションで行います。  

- ディレクトリを指定  
  emulation対象ファイルは指定したディレクトリの*.pio.hファイルです。  
  複数存在する場合はエラーになります。  
  従来の1パラメータ指定時と同じ動作です。  

- ``.py`` ファイルを指定  
  micropython版PIO制御ソースを受け付けてemulationします。  

### ``c_program``と``pin_program`` の指定方法の変更
``c_program``と``pin_program`` の指定は ``--c_prog``、``--pin_prog``オプションで指定します。  
それぞれのデフォルトは以下の通りです。  

- ``.pio.h`` ファイルを指定した場合  
  ``.pio.h`` ファイルと同じディレクトリの``c_program``と``pin_program``  

- ディレクトリを指定した場合  
  指定したディレクトリの``c_program``と``pin_program``  

- ``.py`` ファイルを指定した場合  
  ``.py`` ファイルと同じディレクトリの``.py``ファイルの拡張子を``.c_program``と``.pin_program``に変更したファイル  


### 追加オプション
- ``--save``  
  emulation結果を保存します。  
  ``--dump``オプションとほぼ同じですが、フォーマットはJSONで、結果をファイルに保存します。  
  本オプション単独ではGUI表示も行います。  

  保存ファイル名は以下の通りです。
    - ``.pio.h`` ファイルを指定した場合  
      ``.pio.h`` ファイルと同じディレクトリの``result.json``  

    - ディレクトリを指定した場合  
      指定したディレクトリの``result.json``  

    - ``.py`` ファイルを指定した場合  
      ``.py`` ファイルと同じディレクトリの``.py``ファイルの拡張子を``.json``に変更したファイル  

- ``--no-disp``  
  GUI表示を行いません。  
  ``--save``オプションと組み合わせてバッチ処理で複数のエミュレーションを行うときに使用します。  


### 波形表示ウィンドウの追加
![動作画面(修正版)](emulator_screenshot_annotations2.png)

GPIO端子の出力波形を表示できるようにしました。  
中央のウィンドウのGPIOのデータを時系列で表示できます。  
0をLow、1をHighとして表示します。「･」(不定)は表示されません。  

起動直後は何も表示されていませんので、
表示したいチャネルを表示チャネル選択部のチェックボタンで選択し、
``update``ボタンをクリックすることで表示できます。  
すべてのチャネルを同時に表示することもできますが、
動作が遅くなるので必要なチャネルだけ選択して表示するのが良いでしょう。  

表示を拡大/縮小(水平方向のみ)するには、マウスのホイールを使用します。  
また、拡大した表示を移動(水平方向)や多チャンネル表示で画面に入りきらない部分に移動(垂直方向)するには
マウスをドラッグします。  
垂直方向の移動はウィンドウ右側のスクロールバーでもできます。  

また、波形部分には現在位置(clockで示される値)に赤いカーソルが表示されます。  
波形部分をダブルクリックをすると現在位置を移動することができます。
このとき、他の表示部分もそのclock時点の情報に書き換えられます。  

それとは別にAカーソル(緑)、Bカーソル(青)があります。
これらは波形の目印や時間差を測定するために使用できます。  
Aカーソル(緑)はCTRLキーを押しながらマウスクリック、
Bカーソル(青)はSHIFTキーを押しながらマウスクリックで移動できます。  

各カーソルの位置やカーソル間の差分は画面下のカーソル情報表示部に表示されます。  

### 16進数表示モードの追加

画面上部のツールバーに「HEX」チェックボタンを追加しました。  
このチェックボタンをチェック/解除すると一部の数値表示を16進数/10進数に切り替えることができます。  



以下、オリジナルの説明  

## What does it do
This emulator allows you to step through the workings of a RPI Pico PIO state machine running PIO code. It is intended for running test cases and gain insight into how the code works.

This code takes a .pio.h file generated by pioasm as input and emulates how a PIO state machine (sm) would execute it.  

Besides the .pio.h file there are two more input files:
* a file describing the 'C'-statements (called c_program) such as configuring of pins and putting data into the Tx FIFO. Note that these are not the actual C/C++ statements, but much simplified versions of them. And not all of them, only some (see below.)
* a file describing the externally driven GPIO pins (called pin_program, see below)

The user can obtain insights into the workings of the pio code through a GUI which shows all (?) the relevant sm internal information.

##### Why?
The problem with the RPi Pico PIO state machines (sm) is that the debugger supplied with the vscode distribution for the Pico does not give the insight I need when writing code for a sm. I typically write some code, upload it to the Pico and find that it doesn't do what I want it to do. Instead of guessing what I do wrong, I want to see the values of e.g. the registers when the sm is executing.

And I liked making the emulator.

## What does it not do
Since this emulator is meant for studying how pio code is executed for a given test case (the combination of c_program and pin_program), it only emulates one sm. You can set which of the 8 sm it is (in config.py) because interrupts use this number. It also uses only one PIO (i.e. 32 instruction memory locations) running one program. If you want to study several PIO programs, you'll have to make separate test cases. 

Other things you might expect, but aren't implemented or used:
* It only uses non-blocking 'C'-statements to 'put' data into the TxFIFO and and 'get' data from the RxFIFO,
* 'out exec' and 'mov exec' aren't implemented,
* No FIFO joining,
* 'origin' is not used; all pio code starts at memory location 0,
* It (mostly) doesn't use the registers ([RP2040 datasheet](htts://rptl.io/rp2040-datasheet) section 3.7). 


## Is this the only means to study pio code? 
No, there are several options.

* Use explicit statements in PIO code to export values (e.g. via MOV ISR X, PUSH) but this influences your code,
* You could insert 'EXEC' commands from C/C++, but this still won't give you a deep insight. 

Or you can program the pio, look at its output (GPIO or your print messages) and try to figure out why it doesn't do what you want it to do. This is hard work and the exact reason why I built this emulator.

There are other debuggers and emulators:
* You can use GDB which can give some sm parameters, but not all (e.g. no X- and Y-registers)
* [VisualGDB](https://visualgdb.com/tutorials/raspberry/pico/pio/debugger/) looks awesome but seems to involve a bit of work (I haven't tried it)
* [WOKWI](https://wokwi.com/tools/pioasm), see e.g. the [HackadayU video](https://www.youtube.com/watch?v=LIA9wpt7N60) where it is used.
* [soundpaint rp2040pio](https://github.com/soundpaint/rp2040pio)
* [NathanY3G rp2040-pio-emulator](https://github.com/NathanY3G/rp2040-pio-emulator), installable via [pip](https://pypi.org/project/rp2040-pio-emulator/)

There may be others that I don't know of.
Even though it is a lot of work, building this emulator is quite instructive and fun (if you're into such things.)

## Workflow
When working on a project, I typically have an IDE (in my case vscode) with the project files, the pin_program and c_program files opened. Additionally, I have the emulator open with the .pio.h file of the project 

When changing the .pio code, I use the IDE function 'build' to have pioasm generate a new .pio.h file. Then I press reLoad in the emulator, and study the emulation output.
When changing the C/C++ code that uses the pio code, I have to decide if the c_program also needs to change. Often, this will not be the case because the c_program and pin_program act more like test cases than that they mimic the real C/C++ code or real signals applied to the pins.


## How does it work
Using python3, after reading and parsing the input files, it emulates the sm (and the c-statements, and the externally driven GPIOs) for 500 steps, which can of course be changed in the file config.py, and stores all the state variables at each step into a variable. Then the GUI is started which allows you to step back and forth through the results.

Run it with: ```python main.py pio_program.pio.h pin_program c_program```
For example (1 line): ```python main.py examples/multiplication/pio_program.pio.h examples/multiplication/pin_program examples/multiplication/c_program```

Or simply with:
```python main.py examples/multiplication```

Note: at a given time step, first the c-program and pin-program for that time step are executed, then the PIO statement. So, if the pin-program sets a pin, the PIO sees the pin as set.

After the emulation, the GUI looks similar to the image below.
![](emulator_screenshot_annotations.png)

## GUI

The GUI consists of serveral sections:

##### Externally driven pins
In this section the pin-program is shown. The highlighted text has just been executed. The statements should be placed in a file called pin_program. The format of the statements is: ```timestep, GPIOs, state```
where:
* ```timestep``` is the timestep at which an externally driven pin is changed
* ```GPIOs``` can be either 'GPIOx' with x from 0 to 31, or 'all'
* ```state``` can be '-1' for not driven externally, '0' for externally driven low, or '1' for externally driven high.

For example, a pin_program file can look like this:
```
0, all, -1      # GPIOs are not externally driven (=default, so not necessary)
10, GPIO2, 1    # starting at t=10 GPIO2 is externally driven high
15, GPIO2, 0    # starting at t=15 GPIO2 is externally driven low
20, GPIO2, -1   # starting at t=20 GPIO2 is no longer externally driven
```

The just executed pin statement is highlighted.

##### State machine status
This section shows variables from the internals of the sm:
* 'clock' is the current time step (actually, this is not strictly sm internal)
* 'pc' is the program counter of the just executed pio statement
* 'delay' is the amount of time steps still to be delayed due to a pio code delay option
* 'status' is the fill state of the RxFIFO or TxFIFO
* 'OSR shift counter' indicates when an autopull will occur
* 'ISR shift counter' indicates when an autopush will occur
* 'OSR' is the value in the Output Shift Register
* 'ISR' is the value in the Input Shift Register
* 'X' is the value in the X Register
* 'Y' is the value in the Y Register
* 'IRQ (sm=5)' indicates which IRQ is set. For some pio statements the IRQ depends on the sm (the Pico has 8), in this example it is sm 5, the default is sm 0.

##### Toolbar
The toolbar presents a number of buttons to control the emulator:
* 'reLoad' reloads all the files and restarts the emulation. This is handy for repeated compiling-emulating sessions: after compiling the pio code, just hit reLoad (or the 'l' or 'L' key)
* 'Restart' goes back to t=0 (keybindings: 'r' or 'R')
* 'back 50' goes back 50 time steps
* 'back 10' goes back 10 time steps (keybinding: down arrow)
* 'back' goes back one time step (keybinding: left arrow)
* 'step' goes forward one time step (keybinding: right arrow)
* 'step 10' goes forward 10 time steps (keybinding: up arrow)
* 'step 50' goes forward 50 time steps
* 'Quit' stops the emulator and GUI (keybindings: 'q' or 'Q')

##### PIO code
This is the pio code that was obtained from the '*.pio.h' file (the * indicates that the name before .pio.h doesn't matter). This file should be generated by the pioasm tool, not hand-crafted!

The just executed line of pio code is highlighted.

In the .pio.h files generated by pioasm some statements are placed that are picked up by the emulator. The following information is used:
* ```#define tester_wrap_target```
* ```#define tester_wrap```
* the compiled statements in ```..._program_instructions[]```
* the .length in ```..._program[]```
* the  '```sm_config_set_sideset```' statement in ```..._program_get_default_config[]```
  * note: offset is not supported
  * setting wrap parameters is done using the #define statements mentioned above
* sideset: sideset_base is supported, the other settings (sideset_count, sideset_opt, and sideset_pindirs) are set by parsing the .pio.h file


##### Output (get RxFIFO)
From the 'C' program you can issue a 'get' statement. This removes one item from the RxFIFO and writes it as output. The just produced output is highlighted.

##### FIFOs
These are the two FIFOs, each with 4 data items. The 'C' program can 'put' data in the TxFIFO, and 'get' it out of the RxFIFO.

##### 'C'-statements
The important C/C++ statements for controlling the sm are supported in a simplified form. The statements should be placed in a file called 'c_program'. The format of the statements is as follows:
```timestep, command, argument```
where:
* ```timestep``` is the timestep at which the command should be executed
* ```command``` see below
* ```argument``` the argument for the command

Have a look at the examples to see how these commands work

The currently supported c-statements in the file c_program are:
* set_base, set_count
sets the 'set' pins to use, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.55.
* out_base, out_count
sets the 'out' pins to use, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.51.
* sideset_base
sets the 'sideset' pins to use, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.56, and 4.1.16.3.13. Note that sideset_count , sideset_pindirs, and sideset_opt are set by parsing the .pio.h file (.side_set directive in pio code), but sideset_base isn't, you must set it in the c_program file.
* in_base
sets the 'in' pins to use, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.50. 
* jmp_pin
sets the 'jmp' pin to use, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.16.3.7. 
* out_shift_right, out_shift_autopull, pull_threshold
sets how the out shifting is handled, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.16.3.10.
* in_shift_right, in_shift_autopush, push_threshold
sets how the in shifting is handled, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.16.3.6.
* put, get
put data into the TxFIFO (non-blocking) or get data from the RxFIFO and show it in the output frame of the GUI. See [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.42. and 4.1.15.5.30.
* get_pc
get the program counter and put it in the output frame of the GUI, see [C/C++ SDK](https://rptl.io/pico-c-sdk) 4.1.15.5.32.
* set_N
sets a register that allows monitoring the RxFIFO and TxFIFO levels via the mov statement, see [RP2040 datasheet](https://rptl.io/rp2040-datasheet) at section 3.4.8 (the mov statement) and section  3.7 (Registers). 
* status_sel
selects which FIFO's level should be checked (0 = TxFIFO, 1 = RxFIFO)
* dir_out
sets the pindir of a pin to output
* dir_in
sets the pindir of a pin to input
* dir_non
unset the pindir of a pin

##### Settings
These are some of the register settings that can influence how the sm functions.

##### GPIO status
The GPIO can be changed and used by the sm in different ways. In the section 'Pin configuration' the following information is found:
* GPIO
This shows the the GPIOs on the outside of the Pico. It is determined in the following way:
  * the lowest priority are the 'out' and 'set' values (if the pindir indicates the GPIO is an output)
  * mid priority is the sideset (if sideset is used for pins, and, if the pindir is set to output) 
  * highest priority are the externally driven pins. These win. If an external input is provided to a pin that is configured as output, a warning is given. This situation may potentially destroy the Pico.

   The state of the pins is given as follows:
  * . means not set
  * 0 means low
  * 1 means high 

* GPIO ext
This indicates if a pin is externally driven (configured by the pin-program). A '.' means not driven, '0' means driven low, and '1' means driven high.
* pindir
Indicates whether the pin is configured as Input '1', or as Output '0'.
* sideset vals
Gives the values of the pins set by sideset.
* sideset pins
Gives the pins that are going to be set via sideset. 'B' means the base, 'C' means count. So, if sideset is configured with pin 3 as base and a count of 4, this would look like: ```00000000000000000000000CCCB000```
* out vals
Gives the values of the pins set by out
* out pins
Gives the pins that are going to be set via out. 'B' means the base, 'C' means count. So, if out is configured with pin 3 as base and a count of 4, this would look like: ```00000000000000000000000CCCB000```
* set vals
Gives the values of the pins set by set
* set pins
Gives the pins that are going to be set via set. 'B' means the base, 'C' means count. So, if set is configured with pin 3 as base and a count of 4, this would look like: ```00000000000000000000000CCCB000```
* in pins
Indicates with a 'B' which pin is the base for the in operation
* jmp pin
Indicates with a 'B' which pin is the jmp-pin

##### Warning and errors
In this part of the GUI warning will appear at the time step they were observed during the emulation. 

## What could be improved
Several things, you tell me!

Some things that might be improved:
* not all functionality is implemented (search for TODO in the code), and what is implemented may be buggy and inefficient 
* there are 30 accessible GPIOs on the Pico, but in the emulator there are 32
* the emulator can't be started without pin_program, c_program, or - of course - the *.pio.h files

## Does it contain bugs?
Yes, be warned!
If you find any, please let met know so I can improve the code.


## Examples
I have included a number of examples to show that it works. For an explanation I refer to:
* [button debounce](https://github.com/GitJer/Some_RPI-Pico_stuff/tree/main/Button-debouncer)
* [multiplication](https://github.com/GitJer/Some_RPI-Pico_stuff/tree/main/multiplication)
* [rotational shift](https://github.com/GitJer/Some_RPI-Pico_stuff/tree/main/Rotational_shift_ISR)
* [led panel](https://github.com/GitJer/Some_RPI-Pico_stuff/tree/main/ledpanel)
* [square wave](https://datasheets.raspberrypi.org/rp2040/rp2040-datasheet.pdf), from the RP2040 Datasheet
* [stepper motor](https://www.youtube.com/watch?v=UJ4JjeCLuaI) by Tinker Tech Trove
* side_step
* in_shift
