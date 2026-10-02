# CSCI3060U — Course Project Phase #1: Front End Requirements

**Due:** Friday, October 2nd, 2026, 8:00 PM (same day as Term Test 1 — see DEADLINES.md)
**Target finish:** Thu Oct 1 night (not started as of Sep 30, see crunch timeline). Oct 2 already has Term Test 1 and CSCI3052U PM2.

**Start here: `phase1-plan.md`** (full step-by-step plan)

## What it's asking
Analyze the requirements for the Front End of the Digital Games Distribution System
and, in true XP (Extreme Programming) fashion, represent those requirements as a
complete set of requirements tests — no code yet. Each test is a complete test-session
input stream in its own file, organized into directories.

## Super simple version
The class is building a fake Steam over the semester. Right now (Phase 1) you **don't build
anything**. Your job is to write the **answer key before the exam exists**.

Picture a vending machine you've only seen the manual for. You'd write down: "If I put in $2 and
press B4, I get chips and $0.50 change." "If I press B4 with no money, it says INSERT MONEY." Each of
those is a **test**: what you type in, and what should come out.

That's Phase 1 for the game store. For every command (`login`, `buy`, `sell`, …) you write:
1. **Input file:** exactly what a user would type, start to finish, as one session.
2. **Expected output:** what the screen should say, plus the file the program saves at logout.

Then you write down how you'll run all the tests automatically once the program exists (Phase 2+).

Marks come from covering **every rule** (each rule gets at least one test that follows it and one
that breaks it) and from **catching mistakes in the spec**. The spec has deliberate errors.

## The spec in plain English
Source: `project/Extreme Project - Games Distribution (2026).docx.pdf`

**The product:** a Steam-like game store, split in two:
- **Front End (C++)**: a command-line "terminal" where users log in and type transactions.
  It reads the accounts file and the games file, then writes a **daily transaction file** at logout.
- **Back End (Python)**: a nightly batch job. It takes the merged transaction files, applies them
  to yesterday's accounts/games/collection files, and writes new ones. **Phase 1 doesn't touch this.**

**Phase 1 = Front End only.** You write *tests* (input streams + expected output). No code.
You'll be testing a program that doesn't exist yet, so the tests *are* the requirements.

### Project-wide rules that matter now
- Teams of 2–3, **same lab section**. Private GitHub repo with the TA added. Everyone needs to commit (they check).
- Text in, text out only. Console apps.
- **Don't work ahead.** No front end code before Phase 2 or you lose marks.
- Mid-semester you **swap your Front End** for one of the top class submissions. Client changes come
  through the "Project Client" Slack account and your TA.

### User types
| Code | Type | Can do |
|---|---|---|
| AA | admin | everything |
| FS | full-standard | buy, sell, addcredit (for self) |
| BS | buy-standard | buy, addcredit (no sell) |
| SS | sell-standard | sell, addcredit (no buy) |

Admin-only ("privileged"): `create`, `delete`, `refund`.

### Transactions (what you need to test)
| Transaction | Asks for | Constraints to test |
|---|---|---|
| `login` | username | nothing else accepted before login · no second login until logout · non-admin can't run privileged transactions |
| `logout` | — | only while logged in · writes the daily transaction file · after it, only `login` works |
| `create` | new username, user type | admin only · name ≤ 15 chars · name must be unique · max credit 999,999 |
| `delete` | username | admin only · must exist · can't delete yourself · deleted user's games can't be traded afterwards |
| `sell` | game name, price | not BS · price ≤ 999.99 · name ≤ 25 chars · name must be unique · new game can't be bought until the next session |
| `buy` | game name, seller username | not SS · game must exist · buyer needs enough credit · buyer can't already own it |
| `refund` | buyer, seller, amount | admin only · both users must exist |
| `addcredit` | admin: amount + username · standard: amount only | admin: user must exist · max $1000.00 added per account per session |

**General:** the Front End never crashes and handles bad input politely. You can assume input
arrives as lines of text. So you also need garbage-input tests: unknown commands, letters where a
price should be, negative numbers, empty lines.

### File formats (`_` = space)
**Daily transaction file** (the Front End's output, written at logout, ends with a `00` line):
| Code | Transaction | Line format |
|---|---|---|
| 01 / 02 / 06 / 00 | create / delete / addcredit / end-of-session | `XX_UUUUUUUUUUUUUUU_TT_CCCCCCCCC` |
| 05 | refund | `XX_UUUUUUUUUUUUUUU_SSSSSSSSSSSSSSS_CCCCCCCCC` (buyer, seller, amount) |
| 03 | sell | `XX_IIIIIIIIIIIIIIIIIII_SSSSSSSSSSSSS_PPPPPP` (game, seller, price) |
| 04 | buy | `XX_IIIIIIIIIIIIIIIIIII_SSSSSSSSSSSSSSS_UUUUUUUUUUUUUU_PPPPPP` (game, seller, buyer, price) |

Text is left-justified and space-padded. Numbers are zero-padded. Money gets `.00` appended.

**Input files the Front End reads:**
- **Current User Accounts:** `UUUUUUUUUUUUUUU_TT_CCCCCCCCC`, 28 chars/line, ends with an `END` user.
- **Available Games:** `IIII…_SSSS…_PPPPPP`, ends with an `END` game.
- **Game Collection:** game + owner. The Back End uses this. The spec doesn't say whether the Front End
  reads it, even though `buy` has to check "buyer doesn't already own it". That goes in the log.

### Heads-up: the spec has deliberate holes (worth 2 marks)
The formats section is internally inconsistent. Count the `I`s and `S`s in the boxes, compare them to
the stated line lengths and to the 25-char game-name limit, and check which transaction code `logout`
maps to. There are more beyond those. Every one you find goes in the requirements-problems log with
your assumption and the test that covers it.

## Hand in
1. A list of all test cases and what each is intended to test (table of test names +
   intentions, in English).
2. For each test case: the actual test input file and expected output file (as text
   printouts).
3. A test plan document: how tests are organized (directories etc.), how they'll be
   run (shell scripts / batch files), and how output will be stored/organized for
   reporting and comparison with later runs (include printouts of directory
   structures and scripts).

## Submission
- Electronically via Canvas by 8:00 PM on the due date: test case list (doc/pdf),
  input/output files (zip of txt files), test plan document (doc/pdf).
- Must also have all files committed to the team's GitHub repository by the due date.
- Generative AI use: submit the full prompt/response history if AI was used, or a
  separate signed statement that no AI was used. Missing both = grade of zero.
- Canvas allows **unlimited attempts**, so submit early and resubmit as you improve.
- Canvas stays open until **Sun Oct 4, 8:00 PM**. That's the late window: the syllabus
  says 1%/hour penalty for the first 48h, then not accepted.
- There's a **Group Feedback Form** on the Canvas page. Fill it in; it feeds the Group Effort marks.

## Marking scheme (out of 10 — this is Phase 1 of 6, ~10% of the overall course grade)
Marks are given in ½-mark steps.

| Category | Marks |
|---|---|
| Descriptions — table of test cases + what each tests | 2 |
| Completeness — covers majority of allowed cases + all constraints | 2 |
| Test Files — all provided, correct expected output | 2 |
| Test Input and Output Organization — plan to keep results organized | 1 |
| Test Run Plan — workable plan to run all test cases | 1 |
| Requirements Problems — problems found in requirements handled by test cases | 2 |
| Group Effort (X marks, +/-) | attendance, GitHub repo activity, group feedback forms — TA discretion. **Penalty for failing to present work to the TA "client" in lab** |
| **Total** | **10** |

## ⚠️ Blockers
1. ~~Front End requirements spec~~ ✅ found (2026-09-23), summarized above.
2. **Team GitHub repo.** Does it exist? It has to be private with the TA added.
3. **Partner contact + availability.** See the Discord setup below.
4. **Lab info you missed.** Example test file format, and what "presenting to the TA client" means.
   The spec doesn't say what filenames the Front End uses, so ask the TA or decide as a team.

## Step by step
1. **Today/tomorrow: sort the team stuff.** Message your partner, confirm you're in the same lab
   section, create the private GitHub repo, add the TA. Ask them about blockers 2–4.
2. **Read the "Transactions" table above together** (about 20 min). Split the 8 transactions,
   roughly 4 each. `login`/`logout` are small, so pair them with a bigger one.
3. **Make 2–3 small shared starter files** that every test uses: a user accounts file (one of each
   user type, one with low credit, one near the credit max) and a games file (a few games). Everyone
   uses the same ones so expected outputs agree.
4. **Full candidate list is in `phase1-test-cases.md`** (123 tests + 28 spec problems, with client answers). Split it
   by transaction, cut or merge as a team.
   **For each of your transactions, write the test list first. Just names and one line each:**
   - does it work normally? (one test per allowed user type)
   - one test per rule broken (name too long, price too high, wrong user type, …)
   - edges: exactly at the limit (15 chars, 999.99, $1000) and just over
   - junk input: letters for a price, negative numbers, blank lines
   - order: trying it before login, or after logout
5. **Every time something in the spec confuses you, write it in the problems log right away** with
   your guess and the test ID. Don't leave this for later. It's 2 marks.
6. **Write the actual files:** `.inp` (what's typed), expected screen output, expected transaction file.
   Getting the padding right is the hard part, so count characters carefully.
7. **Swap and check each other's tests** (Mon Sep 28). Wrong expected outputs lose marks.
8. **Write the test plan doc and `run_tests.sh`** (layout below). The script can't actually run
   anything yet. It only has to be a believable plan.
9. **Package and submit by Wed Sep 30:** test table PDF, zip of txt files, test plan PDF, GenAI
   disclosure, push to GitHub, fill in the group feedback form. You can resubmit until the deadline.

### Proposed test layout
```
tests/
  <transaction>/
    <transaction>_01.inp                  # session input stream
    <transaction>_01.out.expected         # expected terminal output
    <transaction>_01.<outfile>.expected   # expected output file (format per spec)
outputs/<run-date>/...                    # actual results per run, never overwritten
run_tests.sh                              # loops over tests/*/*.inp, feeds each to the program,
                                          # saves to outputs/<run-date>/, diffs against expected
test_cases.md                             # name → intention table (deliverable 1)
```
Use the same test IDs (e.g. `<transaction>_03`) in the table, the file names, and the problems log.

### Requirements-problems log
| # | Problem in spec | Our assumption | Test(s) covering it |
|---|---|---|---|
| | | | |

## Timeline (crunch: not started as of Wed Sep 30 evening)
Aim to submit **Thu Oct 1 night**. Fri Oct 2 is Term Test 1 + CSCI3052U PM2, so it's only for fixes before 8 PM.

| When | Do |
|---|---|
| Wed Sep 30 night | Repo (private, TA added) · message partner · confirm the "Client answers + team decisions" table in `phase1-test-cases.md` · agree on screen message wording · write `users.txt` + `games.txt` + `collection.txt` · split the transactions |
| Thu Oct 1 day | Each writes their tests (`.inp` / `.out` / `.etf`) and commits from their own account |
| Thu Oct 1 evening | Swap and check (run the line-length check) · test case table PDF · test plan PDF + `run_tests.sh` · zip · GenAI log · **submit** |
| Fri Oct 2 before 8 PM | Fix anything, resubmit if needed · both fill in the group feedback form |

## Task split
Fill in after the first call.

| Piece | Owner |
|---|---|
| Transactions (split ~evenly by count) | Me: ___ · Partner: ___ |
| Requirements-problems log | shared |
| Test plan document | ___ |
| Run script + directory printouts + packaging | ___ |
| Cross-review | each reviews the other's tests |

## GenAI disclosure
- [ ] AI (Claude) was used for **planning only**. Export this conversation (prompts + responses) as the disclosure file.
- [ ] Tell your partner, since the disclosure covers the whole group's submission.
- [ ] If anyone uses AI later on this phase, log that chat too.

## Stuck points / open questions
- Team GitHub repo: exists? who owns it?
- Filenames/paths the Front End reads and writes? (spec doesn't say)
- Does the Front End read the Game Collection file? (needed for buy's "already owns it" check)
- What does "presenting work to the TA client in lab" involve, and when?

## Log
- 2026-09-18: Phase 1 handout added to repo.
- 2026-09-22: Built work plan + Discord setup. Spec still missing.
- 2026-09-30: Added client Slack answers (`reqs.md`) + prof's new `list` transaction to `phase1-test-cases.md`. Not started yet, so switched to the crunch timeline.
- 2026-09-23: Drafted full test-case list in `phase1-test-cases.md` (with Claude, so disclose it).
- 2026-09-23: Found the spec, added a plain-English summary and a concrete step-by-step.

---

## Discord server setup
Takes about 5 minutes to build by hand. Afterwards you can go to Server Settings → Server Template
to save it as a reusable template link for other group projects.

**Server name:** `CSCI3060U Project`

| Category | Channels |
|---|---|
| INFO | `#announcements` (deadlines, pinned) · `#resources` (spec PDF, handout, repo link) |
| PHASE 1 | `#phase1-planning` · `#test-cases` · `#requirements-issues` · `#test-plan` |
| GENERAL | `#general` · `#github` (GitHub repo → Settings → Webhooks → Discord webhook URL + `/github`) |
| VOICE | `Work Session` |

- Roles: you don't need any with 2 people. A colour role each is optional.
- For later phases, duplicate the PHASE category (right-click → Clone) and rename it.

**Pin in `#announcements`:**
```
📌 Phase 1 — Front End Requirements tests
Due: Fri Oct 2, 8:00 PM (Canvas + GitHub). Internal target: Wed Sep 30.
⚠️ Oct 2 is also Term Test 1.
Hand in: test-case table (pdf) · input/expected-output files (zip of txt) · test plan (pdf) · GenAI disclosure
Marks /10: descriptions 2 · completeness 2 · test files 2 · organization 1 · run plan 1 · requirements problems 2 · group effort ±
Late window: until Oct 4 8 PM at 1%/hour.
```

**Pin in `#requirements-issues`:**
```
Format: [#] Problem in spec → Our assumption → Test ID(s)
```

**Opening message to your partner** (edit to taste):
```
Hey! I'm Jason, your partner for the CSCI3060U project. Phase 1 (requirements tests for the
front end) is due Fri Oct 2 at 8 PM, which is also Term Test 1, so I'd like to finish by Sep 30.
I set up a server for the project: <invite link>

I missed the lab. Do you have the front end requirements doc and do we have a GitHub repo yet?
Could you do a quick call Thursday (Sep 24) to go through the spec and split up the transactions?

FYI, I used Claude to help plan how we organize this (not to write the tests). The handout
says we have to submit that chat log, so I'll handle that part.
```
