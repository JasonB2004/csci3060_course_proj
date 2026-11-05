---
title: "CSCI 3060U Phase 3: Front End Requirements Testing"
subtitle: "Group 35: Jason Badwal, Emma Zhu"
---

# 1. Running the Front End from the command line

The Front End is C++17 and builds with `make` on Linux (g++).

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

- Commands are read from standard input, one per line (`login`, `logout`, `create`, `delete`,
  `sell`, `buy`, `refund`, `addcredit`, `list`, `listaccounts`, `search`). Press Ctrl+D to end.
- Prompts and messages (the terminal log) go to standard output.
- The three input files are read at every login and never changed.
- The daily transaction file is appended to at every logout, so several sessions in one run all
  end up in the same file.
- A saved session can be replayed with input redirection:
  `./frontend users.txt games.txt collection.txt transout.atf < session.inp > session.out`
- If the program isn't given exactly four file names, it prints a usage line and exits with status 1.

# 2. Running all the tests

```bash
cd phase3
./run_tests.sh             # build the Front End, run every test, check every result
./run_tests.sh search      # only the tests whose names start with "search"
./check_outputs.sh         # re-check the most recent run without running it again
./check_outputs.sh outputs/2026-11-05_150242     # re-check one particular run
```

`run_tests.sh` does everything: it builds the Front End with `make`, runs all 146 tests, then
calls `check_outputs.sh`. No manual steps are needed. The scripts can be started from any
folder.

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

Test names are `<command>_<number>`, for example `sell_05`. A test's input, expected and
actual files all share that name, so the files for one test are easy to find.

## What the scripts do

For each `tests/inputs/<test>.inp`, `run_tests.sh` runs:

```bash
../phase2/frontend <data>/users.txt <data>/games.txt <data>/collection.txt \
    outputs/<run>/<test>.atf  < tests/inputs/<test>.inp  > outputs/<run>/<test>.out 2>&1
```

`<data>` is `tests/data/<command>/` if that folder exists, and `tests/data/` otherwise. A test
that never logs out gets an empty `.atf`, so both outputs can be compared for every test.

`check_outputs.sh` then makes two comparisons for every test:

1. Transaction file: `diff outputs/<run>/<test>.atf tests/expected/<test>.etf`
2. Terminal output: `diff outputs/<run>/<test>.out tests/expected/<test>.out`

Only a missing newline at the very end of a file is ignored. Every other difference counts as a
failure, including padding, spacing, wording and line order. Each test is reported as `PASS`,
`FAIL (transaction file)`, `FAIL (terminal output)` or both. The script exits with status 0 only
if every test passed.

# 3. Test suite executions

| Run | Results folder | Front End version | Tests | Passed | Failed |
|---|---|---|---|---|---|
| 0 | (Phase 1 script, not kept) | Phase 2 prototype, unchanged | 122 | 121 | 1 (`delete_11`) |
| 1 | `outputs/2026-11-05_150242` | Phase 2 prototype + file names on the command line (commit `75052ba`) | 136 | 122 | 14 |
| 2 | `outputs/2026-11-05_150425` | `search` added, `delete_11` corrected (commit `1d5c097`) | 136 | 136 | 0 |
| 3 | `outputs/2026-11-05_151420` | Same code, 10 tests added for client clarifications (commit `84705b8`) | 146 | 146 | 0 |

Run 0 was a first check of the unchanged Phase 2 prototype with the Phase 1 `run_tests.sh`. It
found the same `delete_11` failure as run 1, so that failure is logged once below. Run 1 was the
first run of the full Phase 3 suite. The 14 new `search` tests were written from the client's
requirement before `search` was programmed. Run 2 is the full suite again after every fix. Run 3
added 10 tests for client and professor answers given during Phase 2 that had no test yet
(section 6). They all passed on their first run, so they produced no failures to log.

# 4. Failure log

All failures below are from run 1. In every case the transaction file matched and only the
terminal output was wrong.

| # | Test | What it tests | How the output was wrong | Error (in code or test) | Fix |
|--|-----|-------------|---------------|---------------|---------------|
| 1 | delete_11 | Admin deletes `buyuser` and logs out, then `buyuser` logs in again in the same run | Printed `Login successful. Welcome buyuser (BS).` where the test expected `Error: user does not exist.` The rest of the session then didn't line up: the next `login` gave `Error: already logged in.` and `admin` gave `Error: invalid command.` | **Test error.** The expected output assumed a delete carries over to the next session in the same run. The Front End re-reads the accounts file at every login (Phase 2 design), and the Back End only applies deletes overnight, so `buyuser` is still in the file until then. `sell_20` relies on the same rule for new games. | Rewrote `delete_11`: after the delete and logout, `buyuser` logs in and logs out, and the test expects that login to succeed. The expected transaction file (one `02` line and two `00` lines) is unchanged. |
| 2 | search_01 | A full-standard user searches `dew`: the matching game is shown, no users match | `search` gave `Error: invalid command.`, then the query `dew` was read as a command and gave a second `Error: invalid command.` No results were printed. | **Code error.** No `search` transaction existed: it is a new client requirement (Phase 3 update). | Added `SearchTransaction` (`SearchTransaction.h/.cpp`), registered it in `FrontEnd`, and added `COMMAND_SEARCH = "search"` to `Constants.h`. |
| 3 | search_02 | Admin searches `user`: no games match, and the three standard users are listed | Same as #2: two `Error: invalid command.` lines (`search`, then `user`), no results | `search` not implemented | Same fix as #2 |
| 4 | search_03 | Admin searches `shop`: a game (`Admin Shop Game`) and a user (`shopadmin`) both match | Same as #2 (`search`, then `shop`) | `search` not implemented | Same fix as #2 |
| 5 | search_04 | Buy-standard user searches `admin`: the admin who sells a game (`shopadmin`) is shown, the admin who sells nothing (`admin`) is hidden | Same as #2 (`search`, then `admin`) | `search` not implemented | Same fix as #2. `SearchTransaction` skips an admin's name for a non-admin viewer unless that admin is the seller of a game for sale. |
| 6 | search_05 | Admin searches `admin`: an admin sees both admins | Same as #2 (`search`, then `admin`) | `search` not implemented | Same fix as #2 |
| 7 | search_06 | Sell-standard user searches `admin`: the same hiding rule applies to every non-admin type | Same as #2 (`search`, then `admin`) | `search` not implemented | Same fix as #2 |
| 8 | search_07 | Search for `STARDEW valley` finds `Stardew Valley`: case is ignored and spaces are kept | Same as #2 (`search`, then `STARDEW valley`) | `search` not implemented | Same fix as #2. Matching compares lower-case letters. |
| 9 | search_08 | Search for `zzz`: prints `No games found.` and `No users found.` | Same as #2 (`search`, then `zzz`) | `search` not implemented | Same fix as #2 |
| 10 | search_09 | An empty query is refused with `Error: invalid search query.` | `search` gave `Error: invalid command.`, then the empty line gave a second `Error: invalid command.` | `search` not implemented | Same fix as #2. An empty query is refused, since it would match every name. |
| 11 | search_10 | `search` before logging in gives `Error: you must log in first.` | Printed `Error: invalid command.` instead, because the unknown-command check runs before the login check | `search` not implemented | Same fix as #2. Once `search` is a known command, `FrontEnd`'s login check refuses it. |
| 12 | search_11 | A game put up for sale this session (`Celeste`) is not found until the next session, matching `list` | After the sell, `search` and `Celeste` each gave `Error: invalid command.` | `search` not implemented | Same fix as #2. Moved the "games that can be bought now" filter from `ListGamesTransaction` into `Session::getGamesForSale()`, so `list` and `search` show the same games. |
| 13 | search_12 | After admin deletes `selluser`, searches for `Stardew` and `selluser` find nothing (the user and their game are gone) | Both searches failed: four `Error: invalid command.` lines in total | `search` not implemented | Same fix as #2 |
| 14 | search_13 | A user created this session (`newfan`) is found by searching `fan` | After the create, `search` and `fan` each gave `Error: invalid command.` | `search` not implemented | Same fix as #2 |

`search_14` (`search now` with extra words is an invalid command) passed in run 1 too, since
`search now` was rejected as an unknown command either way. It still passes in runs 2 and 3.

# 5. Changes made in Phase 3

**Program (`phase2/src/`)**

- File names on the command line (handout step 4). `main.cpp` reads the four file names and
  passes them to `FileManager`, which is passed to `FrontEnd` and `Session`. The fixed names
  `users.txt`, `games.txt`, `collection.txt` and `transactions.txt` were removed from
  `Constants.h`.
- New `search` transaction (client update): new files `SearchTransaction.h` and
  `SearchTransaction.cpp`, plus `Session::getGamesForSale()`, which `list` now uses too.

**Tests (`phase3/tests/`)**

- The 122 Phase 1 tests were moved into the `inputs/` and `expected/` layout above. Their
  contents are unchanged, except for `delete_11` (failure #1).
- 14 new tests, `search_01` to `search_14`, with their own starting files in `tests/data/search/`.
  The shared files have no admin who sells a game, so they can't test the hiding rule.
- 10 new tests for client clarifications given after Phase 1 (section 6).

# 6. Requirement changes since Phase 1 and the tests that cover them

The client and professor answered several questions after Phase 1. This table shows how the
tests now reflect each answer.

| Change or clarification | Source | Tests |
|---|---|---|
| The Front End never writes the accounts or games files. Each login re-reads them, so a user deleted in one session can still log in at the next login, until the Back End runs. | Professor | `delete_11` (corrected, failure #1), `sell_20` |
| New admin-only transaction listing all active accounts (`listaccounts`). It shows username, type and credit, includes this session's changes and writes nothing to the transaction file. | Client | `listaccounts_01` to `listaccounts_06` (new) |
| A username freed by `delete` can be reused in the same session. | Client | `create_20` (new) |
| User types are entered as the abbreviations AA/FS/BS/SS, and our team chose to make them case-sensitive. | Client (left to us) | `create_21` (new) |
| If the input ends without `logout`, no daily transaction file is written. | Client | `logout_08` (new) |
| The $1000 per-session `addcredit` limit applies to every account, including credit added by an admin. | Professor | `addcredit_15` (new), `addcredit_09`, `addcredit_13` |
| Games can be free (price 0.00). | Professor | `sell_07` |
| A `buy` with the wrong seller name is invalid. | Professor | `buy_06` |
| New `search` transaction (Phase 3 update). | Client | `search_01` to `search_14` (new) |

`listaccounts` is still the name our team chose. If the client gives a required name, only
`Config::COMMAND_LIST_ACCOUNTS` in `Constants.h` and the six test inputs need to change.

# 7. How `search` behaves (our reading of the client's update)

The client asked for a `search` transaction that "outputs all items and all users whose names
contain the search query", where a non-admin "should not output any names of administrators who
are not selling games". Where the update left details open, we chose the following:

- Any logged-in user may search. It asks `Enter search query:` and writes nothing to the daily
  transaction file.
- Matching ignores upper and lower case and keeps spaces as typed. An empty query is refused
  with `Error: invalid search query.`
- "Items" are the games for sale. They are shown as `name - seller - price` (the same as `list`),
  under `Games matching "<query>":`. Games put up for sale in the current session are left out,
  as in `list`.
- Users are shown by name only, under `Users matching "<query>":`. Credit stays private, since
  `listaccounts` is admin only.
- An admin sees every matching user. A non-admin does not see an admin unless that admin is the
  seller of at least one game for sale.
- If nothing matches, the section prints `No games found.` or `No users found.`

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
