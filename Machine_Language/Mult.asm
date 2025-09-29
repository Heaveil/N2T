// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// Pseudocode
// if (RAM[0] != 0 || RAM[1] != 0) {
//     while(RAM[1]){
//         RAM[2] += RAM[0]
//         RAM[1]--
//     }
// }

// set RAM[2] = 0
@R2
M=0

// If RAM[0] == 0
@R0
D=M
@END
D;JEQ

(LOOP)
// IF RAM[1] == 0; GOTO END
@R1
D=M
@END
D;JEQ

// RAM[2] += RAM[0]
@R0
D=M
@R2
M=D+M

// RAM[1]--
@R1
M=M-1

// GOTO LOOP
@LOOP
0;JMP

(END)
@END
0;JMP
