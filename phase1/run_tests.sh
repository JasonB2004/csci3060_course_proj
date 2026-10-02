#!/bin/bash
# Runs the Phase 1 front end requirements tests.
#
# Usage (from phase1/):
#   ./run_tests.sh          run every test
#   ./run_tests.sh sell     run only the tests in tests/sell/
#
# For each test, the script:
#   1. copies a fresh set of tests/data/ files so each test starts the same way
#   2. runs the front end with the input file as stdin
#   3. saves terminal output to outputs/<run>/<command>_NN_output.txt
#   4. saves the transaction file to outputs/<run>/<command>_NN_transactions.txt
#   5. compares both against the expected files and records PASS or FAIL

# Front end program to test, and the name of the transaction file it writes.
# Change these once the front end exists (Phase 2).
FRONTEND="${FRONTEND:-$(pwd)/frontend}"
TRANSACTION_FILE="transactions.txt"

TESTS_DIR="tests"
DATA_DIR="$TESTS_DIR/data"

# Each run gets its own folder, named by date and time
run=$(date +%Y-%m-%d_%H%M%S)
out_dir="outputs/$run"
mkdir -p "$out_dir"
report="$out_dir/report.txt"

# Which tests to run: one command's folder, or all of them
if [ -n "$1" ]; then
    inputs="$TESTS_DIR/$1/*_input.txt"
else
    inputs="$TESTS_DIR/*/*_input.txt"
fi

# Compare two files, ignoring a missing newline at the end of either one
same() {
    diff <(sed -e '$a\' "$1") <(sed -e '$a\' "$2") > /dev/null 2>&1
}

passed=0
failed=0

for input in $inputs; do
    [ -e "$input" ] || { echo "No tests found for: $inputs"; exit 1; }

    base=${input%_input.txt}          # tests/sell/sell_05
    name=$(basename "$base")          # sell_05

    # 1. Fresh copy of the data files in a temporary folder
    work=$(mktemp -d)
    cp "$DATA_DIR"/*.txt "$work"

    # 2 + 3. Run the front end with the input file as stdin, save terminal output
    (cd "$work" && "$FRONTEND") < "$input" > "$out_dir/${name}_output.txt" 2>&1

    # 4. Save the transaction file it wrote (empty if it wrote none)
    if [ -f "$work/$TRANSACTION_FILE" ]; then
        cp "$work/$TRANSACTION_FILE" "$out_dir/${name}_transactions.txt"
    else
        : > "$out_dir/${name}_transactions.txt"
    fi
    rm -rf "$work"

    # 5. Compare against the expected files
    result="PASS"
    same "${base}_output.txt" "$out_dir/${name}_output.txt" || result="FAIL (output)"
    if ! same "${base}_transactions.txt" "$out_dir/${name}_transactions.txt"; then
        [ "$result" = "PASS" ] && result="FAIL (transactions)" || result="FAIL (output, transactions)"
    fi

    if [ "$result" = "PASS" ]; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    echo "$name: $result" | tee -a "$report"
done

echo "Total: $((passed + failed))  Passed: $passed  Failed: $failed" | tee -a "$report"
echo "Results saved in $out_dir/"
