# CA-Project
A cycle-accurate simulator of a 5-stage RISC CPU. 
## ISA
It implements 10 instructions from the RISC-V ISA -
* AND
* OR
* ADD
* SUB
* ADDI
* BEQ
* LW
* SW
* SLL
* SRA

Besides this 2 special instructions have been implemented -
* STORENOC

This instruction will always write the integer 1 to the Memory Mapped Register with address
0x4010(MMR4).

Semantics:
 00000000000000000000000001111011

* LOADNOC



This instruction will store the data in the register rs2 to special
memory mapped registers whose address will be (rs1+imm). In
theory, this instruction is very similar to the “Store” instruction
of RISC-V. However, a regular store would write data to the
Data Cache while this instruction will write the data to
memory-mapped registers. Eg. to store a 32-bit integer 0x33293745 into MMR2; you
would first need to move this integer and 0x4000 into a
Register File Registers(let’s say R1 and R2) respectively, then
use the instruction LOADNOC R1, R2, #8.

Semantics:
imm[11:5] rs2 rs1 000 imm[4:0] 1111111 

## Memory

The memory is word (4 byte) addressable. Two types of memory have been implemented i.e. the Instruction Memory and the Data Memory. The latency for the respective memory fetches can be specified in the number of CPU cycles.

## Pipeline
This processor supports a 5 stage pipeline, where the 5 stages are Fetch, Decode, Execute, Memory and Writeback. The pipeline stalls in the Decode stage when operands are not available. Value forwarding has been implemented from the Execute and Memory stages to save cycles.
