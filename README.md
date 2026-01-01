# my-python-project

A tiny Python CLI tool to analyze `clash_node_report.csv` and rank nodes by:
- risk_score (lower is better)
- error_count (lower is better)
- avg_latency_s (lower is better)

## Usage

Put `clash_node_report.csv` in the repo root, then run:

```bash
python main.py --csv clash_node_report.csv --top 10
```

## Platformer MVP (pygame)

### Install

```bash
python -m pip install -r requirements.txt
```

### Run

```bash
python -m game
```

or

```bash
python game/main.py
```

### Controls

- A/D or ←/→: Move
- Space: Jump
- R: Restart level
- Esc: Quit
