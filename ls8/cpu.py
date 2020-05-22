"""CPU functionality."""

import sys

# Registers:
IM = 5  # Interrupt Mask register
IS = 6  # Interrupt Status register
SP = 7  # Stack Pointer

# Instructions
LDI = 0b10000010  # 0x82
PRN = 0b01000111  # 0x47
HLT = 0b00000001  # 0x01
ADD = 0b10100000  # 0xA0
SUB = 0b10100001  # 0xA1
MUL = 0b10100010  # 0xA2
DIV = 0b10100011  # 0xA3
PUSH = 0b01000101  # 0x45
POP = 0b01000110  # 0x46
CALL = 0b01010000  # 0x50
RET = 0b00010001  # 0x11


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 0xFF  # Initialize RAM to zeroes
        self.reg = [0] * 8  # Initialize all registers to zero
        self.reg[SP] = 0xF4  # Set Stack Pointer to memory address 0xF4

        # Internal Registers
        self.PC = 0         # Program Counter starts at address 0x00
        self.FL = 0x00  # Flags
        # IR, MAR, MDR not initialized

        self.halted = False
        # self.load() # Already in ls8.py

    def load(self, filename="examples/mult.ls8"):
        """Load a program into memory."""

        address = 0
        print("Loading...")
        # TODO: handle file open errors
        with open(filename) as f:
            for line in f:
                str_val = line.split("#")[0].strip()  # The line up to '#'
                if str_val == '':  # In case there's no code on the line.
                    continue
                inst = int(str_val, 2)  # Convert line to binary number
                self.ram[address] = inst
                address += 1
        print(address, "bytes. Done.")

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "div":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while not self.halted:
            ir = self.ram[self.PC]  # Instruction
            op1 = self.ram[self.PC + 1]    # Operand 1
            op2 = self.ram[self.PC + 2]    # Operand 2

            if ir == HLT:
                self.halted = True
                sys.exit(0)

            elif ir == LDI:
                self.reg[op1] = op2
                self.PC += 3

            elif ir == PRN:
                print(self.reg[op1])
                self.PC += 2

            elif ir == ADD:
                self.alu("ADD", op1, op2)
                self.PC += 3

            elif ir == SUB:
                self.alu("SUB", op1, op2)
                self.PC += 3

            elif ir == MUL:
                self.alu("MUL", op1, op2)
                self.PC += 3

            elif ir == DIV:
                self.alu("DIV", op1, op2)
                self.PC += 3

            elif ir == PUSH:
                # TODO: Check for overflow
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.reg[op1]
                self.PC += 2

            elif ir == POP:
                # TODO: Check for underflow
                self.reg[op1] = self.ram[self.reg[SP]]
                self.reg[SP] += 1
                self.PC += 2

            elif ir == CALL:
                # Push return address (PC+2) on stack
                return_addr = self.PC + 2  # Call + Address = 2
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = return_addr

                # Set PC to address of the function
                self.PC = self.reg[op1]

            elif ir == RET:
                # Pop the return address off the stack
                # Store it in the PC
                self.PC = self.ram[self.reg[SP]]
                self.reg[SP] += 1

            else:
                print("Instruction ", ir, "not implemented. Halting.")
                sys.exit(0)
