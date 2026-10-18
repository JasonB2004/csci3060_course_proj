// FrontEnd.cpp
//
// Method definitions for FrontEnd. See FrontEnd.h for what the class is for.

#include "FrontEnd.h"

#include "CreateTransaction.h"
#include "LoginTransaction.h"
#include "LogoutTransaction.h"

// Creates a Front End that reads commands from input and prints to output,
// with every transaction ready to run. Each new transaction class is added here.
FrontEnd::FrontEnd(std::istream& input, std::ostream& output) : console(input, output) {
    addTransaction(std::make_unique<LoginTransaction>());
    addTransaction(std::make_unique<LogoutTransaction>());
    addTransaction(std::make_unique<CreateTransaction>());
}

// Reads and processes commands until the input runs out.
void FrontEnd::run() {
    while (true) {
        std::string commandName = console.prompt("Enter command:");
        if (!console.hasInput()) {
            break;
        }
        processCommand(commandName);
    }
}

// Makes the given transaction available under its command word.
void FrontEnd::addTransaction(std::unique_ptr<Transaction> transaction) {
    std::string commandName = transaction->getName();
    transactions[commandName] = std::move(transaction);
}

// Runs the shared checks for one command word, then runs its transaction.
void FrontEnd::processCommand(const std::string& commandName) {
    Transaction* transaction = findTransaction(commandName);
    if (transaction == nullptr) {
        console.printError("invalid command.");
        return;
    }
    if (transaction->requiresLogin() && !session.isLoggedIn()) {
        console.printError("you must log in first.");
        return;
    }
    if (session.isLoggedIn() && !transaction->isAllowedFor(session.getCurrentUser())) {
        console.printError("permission denied.");
        return;
    }
    transaction->execute(session, console);
}

// Returns the transaction for a command word, or nullptr if there is none.
Transaction* FrontEnd::findTransaction(const std::string& commandName) const {
    auto found = transactions.find(commandName);
    if (found == transactions.end()) {
        return nullptr;
    }
    return found->second.get();
}
