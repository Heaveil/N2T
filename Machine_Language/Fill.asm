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
