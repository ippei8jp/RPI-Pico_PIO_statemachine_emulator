# 概要
オリジナルは [https://github.com/GitJer/Some_RPI-Pico_stuff](https://github.com/GitJer/Some_RPI-Pico_stuff) にあります。  
このうち、state_machine_emulator だけを修正しています。  
そのため、その他のファイルはこのリポジトリから削除しています。  


# Content

## State machine emulator
The problem with the state machines is that debuggers do not give the insight I need when writing code for a sm. I typically write some code, upload it to the pico and find that it doesn't do what I want it to do. Instead of guessing what I do wrong, I would like to see the values of e.g. the registers when the sm is executing. So, I made an [emulator](https://github.com/GitJer/Some_RPI-Pico_stuff/tree/main/state_machine_emulator).

