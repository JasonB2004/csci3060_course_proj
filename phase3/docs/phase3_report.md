---
title: "CSCI 3060U Phase 3: Front End Requirements Testing"
subtitle: "Group 35: Jason Badwal, Emma Zhu"
---

# 1. Running the Front End from the command line

The Front End is written in C++17 and builds with `make` and g++ on Linux.

```bash
cd phase2
make                     # builds ./frontend
./frontend <current user accounts file> <available games file> <game collection file> <daily transaction file>
```

Example, using the sample files in `phase2/data/`:

```bash
cd phase2
./frontend data/users.txt data/games.txt data/collection.txt transout.atf
```

The Front End reads one command per line from standard input (`login`, `logout`, `create`,
`delete`, `sell`, `buy`, `refund`, `addcredit`, `list`, `listaccounts`, `search`), and Ctrl+D
ends the input. Prompts and messages go to standard output. The three input files are read at
every login and never changed. The daily transaction file is appended to at every logout, so
all the sessions in one run end up in the same file.

A saved session can be replayed with redirection:

```bash
./frontend users.txt games.txt collection.txt transout.atf < session.inp > session.out
```

If it isn't given exactly four file names, the program prints a usage line and exits with
status 1.

# 2. Running all the tests

```bash
cd phase3
./run_tests.sh             # build the Front End, run every test, check every result
./run_tests.sh search      # only the tests whose names start with "search"
./check_outputs.sh         # re-check the most recent run without running it again
./check_outputs.sh outputs/2026-11-07_154316     # re-check one particular run
```

`run_tests.sh` builds the Front End with `make`, runs all 147 tests and then calls
`check_outputs.sh`, so nothing has to be done by hand. Both scripts work from any folder.

## Test layout

```
phase3/
  run_tests.sh               step 5: runs every test input, saves both outputs
  check_outputs.sh           step 6: compares actual outputs with expected outputs
  tests/
    inputs/<test>.inp        what the user types in one test (fed to the Front End as stdin)
    expected/<test>.out      expected terminal output
    expected/<test>.etf      expected daily transaction file
    data/                    users.txt, games.txt, collection.txt that every test starts from
    data/search/             starting files for the search tests (adds an admin who sells a game)
  outputs/<date>_<time>/     one folder per run, never overwritten
    <test>.out               actual terminal output
    <test>.atf               actual daily transaction file
    report.txt               PASS/FAIL for every test, and the totals
    failures.txt             full diff for every failed test (only if something failed)
  docs/phase3_report.md      this document
```

Tests are named `<command>_<number>`, for example `sell_05`. A test's input, expected and
actual files all share that name.

## What the scripts do

For each `tests/inputs/<test>.inp`, `run_tests.sh` runs:

```bash
../phase2/frontend <data>/users.txt <data>/games.txt <data>/collection.txt \
    outputs/<run>/<test>.atf  < tests/inputs/<test>.inp  > outputs/<run>/<test>.out 2>&1
```

`<data>` is `tests/data/<command>/` if that folder exists, and `tests/data/` otherwise. A test
that never logs out gets an empty `.atf`, so every test has both outputs to compare.

`check_outputs.sh` then makes two comparisons for every test:

1. Transaction file: `diff outputs/<run>/<test>.atf tests/expected/<test>.etf`
2. Terminal output: `diff outputs/<run>/<test>.out tests/expected/<test>.out`

A missing newline at the very end of a file is ignored. Any other difference counts as a
failure, including padding, spacing, wording and line order. Each test is reported as `PASS`,
`FAIL (transaction file)`, `FAIL (terminal output)` or both, and the script exits with status 0
only if every test passed.

# 3. Test suite executions

| Run | Results folder | Front End version | Tests | Passed | Failed |
|---|---|---|---|---|---|
| 1 | `outputs/2026-11-07_154316` | First command-line version (commit `59783e3`) | 147 | 139 | 8 |
| 2 | `outputs/2026-11-07_154332` | Run 1 failures fixed (commit `d8b7a71`) | 147 | 146 | 1 |
| 3 | `outputs/2026-11-07_154340` | Run 2 failure fixed (commit `d869be3`) | 147 | 147 | 0 |

Each run covers the whole suite: the 122 Phase 1 tests, 14 `search` tests, 10 tests for
clarifications given after Phase 1 (section 6) and `addcredit_16` (section 5).

# 4. Failure log

## Run 1 (8 failures)

| # | Test | What it tests | How the output was wrong | Error (in code or test) | Fix |
|--|-----|-------------|---------------|---------------|---------------|
| 1 | addcredit_06 | Adding exactly $1000.00, the per-session limit | Printed `Error: session credit limit exceeded.` instead of `Added 1000.00 credit to fulluser.`, and the `06` line was missing from the transaction file | Code error: `AddCreditTransaction` checked `alreadyAdded + amount >= MAX_CREDIT_PER_SESSION`, so an amount equal to the limit was refused | Changed `>=` to `>`. $1000.00 is now allowed and $1000.01 is not. |
| 2 | addcredit_09 | Admin adds $1000 to two different accounts in one session | Both adds refused with the session limit error. Both `06` lines missing. | Same `>=` error as #1 | Same fix as #1 |
| 3 | addcredit_10 | $1000 added to the same account in two separate sessions | Both sessions refused with the session limit error. Both `06` lines missing. | Same `>=` error as #1. A second error was hidden behind this one (Run 2, #9). | Same fix as #1 |
| 4 | addcredit_11 | Adding $1000 to an account holding $999,000 (the maximum balance is $999,999.99) | Printed `session credit limit exceeded` where the test expected `credit limit exceeded` | Same `>=` error as #1. The session limit is checked first, so it hid the balance-limit error. | Same fix as #1 |
| 5 | addcredit_16 | Adding $10.05, an amount with fewer than 10 cents | Printed `Added 10.5 credit`, and the transaction line had `0000010.5` instead of `000010.05` | Code error: `Formatter::formatMoney` only padded a cents value of exactly 0 (to `00`), so 1 to 9 cents lost their leading zero | Pad any cents value shorter than two digits with a leading zero |
| 6 | buy_13 | Admin sells a game, then tries to buy it in the same session | The purchase went ahead and asked `Enter seller username:` where the test expected `Error: game not available until next session.` The rest of the session then didn't line up, and the sell's `03` line was lost. | Code error: `BuyTransaction` never checked `Game::isListedThisSession()` | Added that check right after the game is found |
| 7 | sell_19 | A full-standard user sells `Celeste`, then tries to buy it in the same session | Same as #6 | Same missing check as #6 | Same fix as #6 |
| 8 | delete_11 | Admin deletes `buyuser` and logs out, then `buyuser` logs in again in the same run | Printed `Login successful. Welcome buyuser (BS).` where the test expected `Error: user does not exist.` The next `login` then gave `Error: already logged in.` and `admin` gave `Error: invalid command.` | Test error: the Phase 1 test assumed a delete carries over to the next session. The professor clarified that the Front End re-reads the accounts file at every login and only the Back End applies deletes, so `buyuser` can log in until then. `sell_20` relies on the same rule for new games. | Rewrote `delete_11`: after the delete and logout, `buyuser` logs in and logs out, and the test expects that login to succeed. The expected transaction file now has one `02` line and two `00` lines. |

## Run 2 (1 failure)

| # | Test | What it tests | How the output was wrong | Error (in code or test) | Fix |
|--|-----|-------------|---------------|---------------|---------------|
| 9 | addcredit_10 | $1000 added to the same account in two separate sessions | The first session now passed, but the second still printed `Error: session credit limit exceeded.` and its `06` line was missing | Code error: `Session::clear()` didn't reset `creditAddedThisSession`, so the $1000 from the first session still counted in the second. Run 1 couldn't show this because both sessions failed on the `>=` error. | Added `creditAddedThisSession.clear()` to `Session::clear()`, which runs at every login and logout |

## Run 3

All 147 tests passed, so no further changes were needed.

# 5. Changes made in Phase 3

## Program (`phase2/src/`)

- File names on the command line (handout step 4). `main.cpp` reads the four file names and
  passes them to `FileManager`, which is passed to `FrontEnd` and `Session`. The fixed names
  `users.txt`, `games.txt`, `collection.txt` and `transactions.txt` were removed from
  `Constants.h`.
- New `search` transaction (client update): `SearchTransaction.h` and `SearchTransaction.cpp`,
  plus `Session::getGamesForSale()`, which `list` now uses too.
- The four code fixes in the failure log (#1, #5, #6 and #9).

## Tests (`phase3/tests/`)

- The 122 Phase 1 tests were moved into the `inputs/` and `expected/` layout above. Only
  `delete_11` changed (failure #8).
- 14 new tests, `search_01` to `search_14`, with their own starting files in
  `tests/data/search/`. The shared files have no admin who sells a game, so they can't test
  the rule for hiding admins.
- 10 new tests for clarifications given after Phase 1 (section 6).
- `addcredit_16`. No earlier test used an amount with fewer than 10 cents, so that formatting
  was never checked.

## Phase 1 feedback

The feedback asked for "requirements problems" in the project plan, said that no code should
have been written in Phase 1, and asked for screenshots of our AI interactions. None of it was
about the test cases.

# 6. Requirement changes since Phase 1 and the tests that cover them

The client and professor answered several questions after Phase 1.

| Change or clarification | Source | Tests |
|---|---|---|
| The Front End never writes the accounts or games files. Each login re-reads them, so a user deleted in one session can still log in at the next login, until the Back End runs. | Professor | `delete_11` (rewritten, failure #8), `sell_20` |
| New admin-only transaction listing all active accounts (`listaccounts`). It shows username, type and credit, includes this session's changes and writes nothing to the transaction file. | Client | `listaccounts_01` to `listaccounts_06` (new) |
| A username freed by `delete` can be reused in the same session. | Client | `create_20` (new) |
| User types are entered as the abbreviations AA/FS/BS/SS. The client left case to us, and we made them case-sensitive. | Client | `create_21` (new) |
| If the input ends without `logout`, no daily transaction file is written. | Client | `logout_08` (new) |
| The $1000 per-session `addcredit` limit applies to every account, including credit added by an admin. | Professor | `addcredit_15` (new), `addcredit_09`, `addcredit_13` |
| Games can be free (price 0.00). | Professor | `sell_07` |
| A `buy` with the wrong seller name is invalid. | Professor | `buy_06` |
| New `search` transaction (Phase 3 update). | Client | `search_01` to `search_14` (new) |

`listaccounts` is still the name our team chose. If the client gives a required name, only
`Config::COMMAND_LIST_ACCOUNTS` in `Constants.h` and the six test inputs need to change.

# 7. How `search` behaves

The client asked for a `search` transaction that "outputs all items and all users whose names
contain the search query", where a non-admin "should not output any names of administrators who
are not selling games". The update left some details open, and we chose the following:

- Any logged-in user may search. It asks `Enter search query:` and writes nothing to the daily
  transaction file.
- Matching ignores upper and lower case and keeps spaces as typed. An empty query is refused
  with `Error: invalid search query.`
- "Items" are the games for sale, shown as `name - seller - price` (the same as `list`) under
  `Games matching "<query>":`. Games put up for sale in the current session are left out, as
  in `list`.
- Users are shown by name only, under `Users matching "<query>":`. Credit stays private, since
  `listaccounts` is admin only.
- An admin sees every matching user. A non-admin sees an admin only if that admin is the seller
  of at least one game for sale.
- If nothing matches, the section prints `No games found.` or `No users found.`
- `search` followed by other words on the same line (`search now`) is an invalid command
  (`search_14`).

Example (buy-standard user, with the files in `tests/data/search/`):

```
Enter command:
search
Enter search query:
admin
Games matching "admin":
Admin Shop Game - shopadmin - 30.00
Users matching "admin":
shopadmin
```
