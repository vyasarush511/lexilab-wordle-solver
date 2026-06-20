# LexiLab: Explainable Wordle Solver

LexiLab is a Python Wordle solver that explains each guess using information
theory. It simulates Wordle feedback, filters possible answers, scores guesses
by expected information gain, and benchmarks solve performance on a
deterministic word sample.

## Highlights

- Correct green/yellow/gray feedback simulation for 5-letter Wordle words
- Two-pass repeated-letter handling that matches Wordle's letter consumption
  rules
- Candidate filtering by replaying feedback against every possible answer
- Entropy-based guess ranking with expected remaining candidates and worst-case
  bucket size
- CLI modes for ranking, solving, clue-based suggestions, and benchmarking
- Static HTML benchmark report generated at [`docs/index.html`](docs/index.html)
- Unit tests and GitHub Actions CI

## Benchmark Snapshot

The bundled benchmark report was generated with:

```powershell
lexilab benchmark --sample-size 250 --seed 7 --max-turns 6 --json reports\benchmark.json --html docs\index.html
```

Results on that deterministic 250-word sample:

| Metric | Value |
| --- | ---: |
| Success rate | 100.0% |
| Average guesses | 2.76 |
| Worst successful solve | 4 |
| Failures | 0 |

Guess distribution:

| Guesses | Answers |
| ---: | ---: |
| 1 | 1 |
| 2 | 71 |
| 3 | 164 |
| 4 | 14 |

## How The Algorithm Works

For a possible guess, LexiLab simulates that guess against every remaining
candidate answer. Each answer produces a feedback pattern such as `GYY..`.
Those patterns form buckets. A strong guess splits the candidate set into many
small buckets because the next feedback will remove more uncertainty.

Entropy is used to score that split:

```text
entropy = sum(probability(pattern) * log2(1 / probability(pattern)))
```

Higher entropy means the guess is expected to reveal more information.

The solver loop is:

```text
start with candidate answers
choose highest-entropy guess
score the guess against the hidden answer
keep only candidates that would produce the same feedback
repeat until solved
```

## Quick Start

```powershell
python -m pip install -e ".[dev]"
pytest
```

Show strong opening guesses over a deterministic sample:

```powershell
lexilab rank --top 5 --sample-size 750 --seed 7
```

Simulate a solve:

```powershell
lexilab solve cigar --sample-size 750 --seed 7
```

Use known clues to ask for the next best guess:

```powershell
lexilab suggest --clue saine:.YY.. --top 5
```

Generate benchmark reports:

```powershell
lexilab benchmark --sample-size 250 --seed 7 --max-turns 6
```

## Example Output

```text
Simulating answer: cigar
1. saine -> .YY..  entropy=5.860  19/751 candidates remain
2. gular -> Y..GG  entropy=3.642  1/19 candidates remain
3. cigar -> GGGGG  entropy=0.000  1/1 candidates remain
Solved in 3 guesses.
```

## Project Structure

```text
src/lexilab/feedback.py   Wordle feedback rules
src/lexilab/solver.py     Candidate filtering and entropy scoring
src/lexilab/benchmark.py  Solver simulation and benchmark summaries
src/lexilab/report.py     JSON and static HTML report generation
src/lexilab/cli.py        Command-line interface
tests/                    Unit tests
docs/index.html           Generated benchmark report
```

## Word Data

LexiLab bundles the MIT-licensed
[`tabatkins/wordle-list`](https://github.com/tabatkins/wordle-list) corpus.
See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for attribution.
