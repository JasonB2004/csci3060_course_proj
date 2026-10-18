// main.cpp
//
// Front End for the Digital Games Distribution System (CSCI 3060U, Phase 2).
// A point-of-purchase terminal: reads transactions (login, logout, create,
// delete, sell, buy, refund, addcredit, list, listaccounts) one line at a
// time from standard input and prints prompts and results to standard output.
//
// Input files (read at every login, from the current directory, never changed):
//   users.txt       current user accounts
//   games.txt       available games for sale
//   collection.txt  which user owns which game
// Output file (appended at every logout):
//   transactions.txt  daily transaction file, one line per successful transaction
//
// How to run:   make            (in phase2/, builds ./frontend)
//               ./frontend                       type commands, Ctrl+D to end
//               ./frontend < session_input.txt   run a saved session

#include <iostream>

#include "FrontEnd.h"

// Starts the Front End on the terminal and runs until the input ends.
int main() {
    FrontEnd frontEnd(std::cin, std::cout); // engine reads keybord, prints to screen
    frontEnd.run(); // loop until input runs out
    return 0;
}
