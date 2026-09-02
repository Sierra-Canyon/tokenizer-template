# Honors Software Engineering — student workspace

**Section C-JD · Period C · Room U 108 · 2026–27**

One repository for the year. Every assignment writes into it, `git log` tells the whole
story by May, and it is the thing you hand a stranger at the symposium.

---

## First run

```
./setup.sh
```

That installs Python 3.12 and the dependencies, installs a git filter so notebook output
never reaches a commit, installs the secret guard, and runs the environment check. It
prints two things for you to verify by hand at the end. Do them. A filter that silently
failed to install is worse than no filter, because you will not find out until your
reviewer opens a four-thousand-line diff.

If `./setup.sh` says `uv: command not found`, you skipped A01's first line:

```
brew install uv nvm
```

## What is where

| Path | What |
|---|---|
| `notebooks/01_tokenizer_probe.ipynb` | A03. Measure a real tokenizer before you build one. |
| `notebooks/02_bpe_from_scratch.ipynb` | A04. Drive your own tokenizer and compare the two. |
| `bpe/tokenizer.py` | A04. **The file you write.** Four functions and two classes. |
| `tests/` | 68 tests against `bpe/tokenizer.py`. They are the spec. |
| `tokenlab/` | A03's `FINDINGS.md`. |
| `data/` | Your corpus. Git-ignored on purpose. |
| `scripts/check_env.py` | The Week 1 environment check. Re-run it whenever something breaks. |
| `scripts/install_secret_guard.sh` | Pre-commit hook that refuses staged keys. |
| `logs/` | Your daily log entries. |

## The tests are the assignment

`bpe/tokenizer.py` ships as a skeleton: every function raises `NotImplementedError` and
every docstring tells you the contract. Work smallest first.

```
pytest tests/test_helpers.py -q     # get_stats and merge — start here
pytest tests/test_basic.py -q       # BasicTokenizer
pytest tests/test_regex.py -q       # RegexTokenizer
pytest tests/ -q                    # all 68
pytest tests/ -x                    # stop at the first failure
```

Four of these tests exist because of bugs that let your code run and quietly produce the
wrong answer:

- **`test_merges_are_applied_lowest_index_first`** — training takes the pair with the
  highest *count*; encoding takes the pair with the lowest *merge index*. Swap them and
  everything still round-trips. Only the id sequence shows it.
- **`test_repeated_token_does_not_double_consume`** — after a match, `merge` steps by two.
- **`test_single_character_does_not_hang`** — your encode loop needs both the length
  guard and the `break`.
- **`test_decode_replaces_rather_than_raising_on_a_broken_sequence`** — a byte sequence
  mid-merge is often not valid UTF-8. Know why `errors="replace"` is correct rather than
  a workaround; you will be asked.

## Rules that apply all year

**Never commit a key.** The secret guard blocks the obvious cases. It is not a substitute
for knowing where your key is. If you ever push one, tell me the same day: there is no
penalty for reporting it and rotating it, and concealing it is a different conversation.

**Never enter a personal credit card** for any service this course uses. If something asks
for one, stop and come to me. Class keys are provisioned with hard caps.

**Branches.** `dev/<feature>` for work, `log/<feature>` for log entries. One pull request
per assignment, and the PR body says where the work is weakest.

**AI is allowed, and you say so.** Every log entry carries an `AI use:` line. Using it
costs you nothing. Not saying so is the only version that is a problem.
