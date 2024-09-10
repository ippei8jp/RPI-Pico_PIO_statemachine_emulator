from pio_disasm import pio_disasm



print(f"'{pio_disasm(0b111_11111_100_00000, 0, False)}'")

print(f"'{pio_disasm(0b111_11111_100_00000, 1, False)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 2, False)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 3, False)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 4, False)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 5, False)}'")
print(f"'{pio_disasm(0b111_00000_100_00000, 5, False)}'")



print(f"'{pio_disasm(0b111_11111_100_00000, 2, True)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 3, True)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 4, True)}'")
print(f"'{pio_disasm(0b111_11111_100_00000, 5, True)}'")

print(f"'{pio_disasm(0b111_01111_100_00000, 5, True)}'")
print(f"'{pio_disasm(0b111_00111_100_00000, 5, True)}'")
print(f"'{pio_disasm(0b111_00011_100_00000, 5, True)}'")
print(f"'{pio_disasm(0b111_00001_100_00000, 5, True)}'")
print(f"'{pio_disasm(0b111_00000_100_00000, 5, True)}'")









print(f"'{pio_disasm(0b000_00000_00000000)}'")
print(f"'{pio_disasm(0b000_00000_11100000)}'")
print(f"'{pio_disasm(0b000_00000_11111111)}'")



print(f"'{pio_disasm(0b001_00000_0_00_00000)}'")
print(f"'{pio_disasm(0b001_00000_0_11_00001)}'")
print(f"'{pio_disasm(0b001_00000_0_10_01001)}'")



print(f"'{pio_disasm(0b010_00000_000_00000)}'")
print(f"'{pio_disasm(0b010_00000_011_00001)}'")




print(f"'{pio_disasm(0b011_00000_000_00000)}'")
print(f"'{pio_disasm(0b011_00000_100_00001)}'")




print(f"'{pio_disasm(0b100_00000_0_00_00000)}'")
print(f"'{pio_disasm(0b100_00000_0_01_00000)}'")
print(f"'{pio_disasm(0b100_00000_0_10_00000)}'")
print(f"'{pio_disasm(0b100_00000_0_11_00000)}'")

print(f"'{pio_disasm(0b100_00000_0_00_1_0_000)}'")
print(f"'{pio_disasm(0b100_00000_0_00_1_1_000)}'")
print('====')



print(f"'{pio_disasm(0b100_00000_1_00_0_0000)}'")
print(f"'{pio_disasm(0b100_00000_1_01_0_0000)}'")
print(f"'{pio_disasm(0b100_00000_1_10_0_0000)}'")
print(f"'{pio_disasm(0b100_00000_1_11_0_0000)}'")
print('====')


print(f"'{pio_disasm(0b100_00000_1_00_1_0_000)}'")
print(f"'{pio_disasm(0b100_00000_1_00_1_1_000)}'")
print('====')




# mov
print(f"'{pio_disasm(0b101_00000_000_00_000)}'")
print(f"'{pio_disasm(0b101_00000_000_00_001)}'")
print(f"'{pio_disasm(0b101_00000_010_01_011)}'")
print(f"'{pio_disasm(0b101_00000_011_10_111)}'")
print('====')




# irq
print(f"'{pio_disasm(0b110_00000_0_0_0_00_000)}'")
print(f"'{pio_disasm(0b110_00000_0_0_1_00_000)}'")
print(f"'{pio_disasm(0b110_00000_0_1_0_00_000)}'")
print('====')

# set
print(f"'{pio_disasm(0b111_00000_000_00000)}'")
print(f"'{pio_disasm(0b111_00000_100_11111)}'")


