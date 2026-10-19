# CSCI3060U — Digital Games Distribution System (Fall 2026)

Team: Group 35 — Jason Badwal, Emma Zhu

| Phase | Due | Folder |
|---|---|---|
| 1. Front End Requirements (tests) | Oct 2 | `phase1/` |
| 2. Front End Rapid Prototype | Oct 19 | `phase2/` |
| 3. Front End Requirements Testing | Nov 6 | |
| 4. Back End Rapid Prototype | Nov 20 | |
| 5. Back End Unit Testing | Nov 30 | |
| 6. Integration and Delivery | Dec 7 | |

## Phase 1 layout
- `phase1/tests/data/` — accounts, games and collection files every test starts from
- `phase1/tests/<command>/<command>_NN_input.txt` — what the user types
- `phase1/tests/<command>/<command>_NN_output.txt` — expected terminal output
- `phase1/tests/<command>/<command>_NN_transactions.txt` — expected daily transaction file
- `phase1/outputs/` — actual results from each test run, by date
- `phase1/docs/` — test case table, test plan, GenAI disclosure

## Phase 2 layout
- `phase2/src/` — Front End source (C++17), one `.h`/`.cpp` pair per class, plus `Constants.h` and `main.cpp`
- `phase2/Makefile` — builds `phase2/frontend`
- `phase2/data/` — sample `users.txt`, `games.txt` and `collection.txt` for trying it by hand
- `phase2/docs/` — design document, UML diagrams (`uml_diagrams/`), GenAI disclosure and the script that exports it

## Building and running the Front End
```bash
cd phase2
make                  # builds ./frontend
cd data
../frontend           # type commands; Ctrl+D to end
```
The Front End reads `users.txt`, `games.txt` and `collection.txt` from the folder it is run in, and appends to `transactions.txt` there at each logout.

Commands: `login`, `logout`, `create`, `delete`, `sell`, `buy`, `refund`, `addcredit`, `list`, `listaccounts`.

## Running the Phase 1 tests against it
```bash
cd phase1
FRONTEND="$(pwd)/../phase2/frontend" ./run_tests.sh          # all tests
FRONTEND="$(pwd)/../phase2/frontend" ./run_tests.sh sell     # one command's tests
```
`FRONTEND` must be a full path, since each test runs in a temporary folder.
