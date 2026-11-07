# CSCI3060U — Digital Games Distribution System (Fall 2026)

Team: Group 35 — Jason Badwal, Emma Zhu

| Phase | Due | Folder |
|---|---|---|
| 1. Front End Requirements (tests) | Oct 2 | `phase1/` |
| 2. Front End Rapid Prototype | Oct 19 | `phase2/` |
| 3. Front End Requirements Testing | Nov 7 | `phase3/` |
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

## Phase 3 layout
- `phase3/run_tests.sh` — builds the Front End, runs every test, then checks the results
- `phase3/check_outputs.sh` — compares a run's actual outputs with the expected ones
- `phase3/tests/inputs/<test>.inp` — what the user types
- `phase3/tests/expected/<test>.out` / `<test>.etf` — expected terminal output / daily transaction file
- `phase3/tests/data/` — starting files for every test (`data/search/` for the search tests)
- `phase3/outputs/<date>_<time>/` — actual outputs, `report.txt` and `failures.txt` for each run
- `phase3/docs/phase3_report.md` — failure log and instructions (PDF version alongside), plus `genai_disclosure.md`

## Building and running the Front End
```bash
cd phase2
make                  # builds ./frontend
./frontend data/users.txt data/games.txt data/collection.txt transout.atf   # type commands; Ctrl+D to end
```
The four arguments are the current user accounts file, the available games file, the game
collection file and the daily transaction file. The first three are read at every login and never
changed; the transaction file is appended to at each logout.

Commands: `login`, `logout`, `create`, `delete`, `sell`, `buy`, `refund`, `addcredit`, `list`, `listaccounts`, `search`.

## Running the tests
```bash
cd phase3
./run_tests.sh            # all tests
./run_tests.sh sell       # one command's tests
./check_outputs.sh        # re-check the latest run
```
