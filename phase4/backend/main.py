"""
Games Distribution System: Back End (overnight batch processor)

Intention:
    Applies one day of Front End transactions to the system's data files.
    It reads the merged daily transaction file and yesterday's data files,
    applies every transaction session by session, and writes the new data
    files for the next day's Front End. A transaction that breaks a
    constraint (negative balance, duplicate username, account-manager
    permissions) is skipped and logged to the terminal. A malformed input
    file stops the program.

Input files:
    merged_transactions   Merged Daily Transaction File (all sessions, ending with a 00 session)
    old_accounts          Old Current User Accounts File
    old_games             Old Available Games File
    old_collection        Old Game Collection File

Output files:
    new_accounts          New Current User Accounts File
    new_games             New Available Games File
    new_collection        New Game Collection File

Terminal output:
    ERROR: <description> <transaction line>   failed constraint (processing continues)
    ERROR: <description> <file>               fatal input error (program stops)

How to run (Python 3, standard library only), from the backend/ folder:
    python3 main.py <merged_transactions> <old_accounts> <old_games> <old_collection> \
                    <new_accounts> <new_games> <new_collection>
"""

import sys

from data_files import AvailableGamesFile, GameCollectionFile, TransactionFile, UserAccountsFile
from file_format import BackEndInputError
from transaction_processor import TransactionProcessor

USAGE = ("Usage: python3 main.py <merged_transactions> <old_accounts> <old_games> "
         "<old_collection> <new_accounts> <new_games> <new_collection>")
FILE_ARGUMENT_COUNT = 7


def main():
    """Read the inputs, apply every transaction and write the outputs.

    Reads the seven file paths from the command line. A BackEndInputError
    from any reader is printed as a fatal ERROR line and the program exits
    with status 1.
    """
    if len(sys.argv) != FILE_ARGUMENT_COUNT + 1:
        print(USAGE)
        sys.exit(1)

    (transactions_path, old_accounts_path, old_games_path, old_collection_path,
     new_accounts_path, new_games_path, new_collection_path) = sys.argv[1:]

    try:
        sessions = TransactionFile(transactions_path).read()
        users = UserAccountsFile(old_accounts_path).read()
        games = AvailableGamesFile(old_games_path).read()
        collection = GameCollectionFile(old_collection_path).read()
    except BackEndInputError as error:
        print(f"ERROR: {error.description} {error.file_path}")
        sys.exit(1)

    processor = TransactionProcessor(users, games, collection)
    processor.process_sessions(sessions)

    UserAccountsFile(new_accounts_path).write(processor.users)
    AvailableGamesFile(new_games_path).write(processor.games)
    GameCollectionFile(new_collection_path).write(processor.collection)


if __name__ == "__main__":
    main()
