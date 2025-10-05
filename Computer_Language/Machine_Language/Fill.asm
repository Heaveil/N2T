// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// Pseudocode
// label white
//     if key == 0; goto white
//     goto set_black

// label set_white
//     fill(white)
//     goto white

// label black
//     if key != 0; goto black
//     goto set_white

// label set_black
//    fill(black)
//    goto black

(WHITE)
@KBD
D=M   // Get Key Stroke
@WHITE
D;JEQ // Key == 0; goto WHITE
@SET_BLACK
0;JMP // goto SET_BLACK

(BLACK)
@KBD
D=M   // Get Key Stroke
@BLACK
D;JNE // Key =! 0; goto BLACK
@SET_WHITE
0;JMP // goto SET_WHITE

(SET_WHITE)
@color
M=0   // SET color to WHITE
@SETUP
0;JMP // goto SETUP
@WHITE
0;JMP // goto WHITE

(SET_BLACK)
@color
M=-1  // SET color to BLACK 
@SETUP
0;JMP // goto SETUP
@BLACK
0;JMP // goto BLACK

(SETUP)
@SCREEN
D=A
@array
M=D   // Array Start Address

@8192
D=A
@index
M=D   // Size of Array

(FILL)
@color
D=M  // set D to color

@array
A=M  // set A to the Array Start Address
M=D  // set RAM[A] to color

@array
M=M+1 // array += 1

@index
M=M-1 // index -= 1
D=M   // set D to index

@FILL
D;JNE // if index != 0 goto FILL
@color
D=M   // set D to color
@WHITE
D;JEQ // if D == WHITE goto WHITE 
@BLACK
0;JMP // else goto BLACK
