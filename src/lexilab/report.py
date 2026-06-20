from __future__ import annotations

import html
import json
from pathlib import Path

from lexilab.benchmark import BenchmarkSummary


def write_json_report(summary: BenchmarkSummary, path: str | Path) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")
    return report_path


def write_html_report(summary: BenchmarkSummary, path: str | Path) -> Path:
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    distribution_rows = "\n".join(
        _distribution_row(turns, count, summary.sample_size)
        for turns, count in summary.guess_distribution.items()
    )
    sample_rows = "\n".join(_result_row(result) for result in summary.results[:24])

    report_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LexiLab Wordle Solver Benchmark</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1d2939;
      --muted: #667085;
      --line: #d0d5dd;
      --green: #3f8f5f;
      --yellow: #c49a27;
      --gray: #667085;
      --bg: #f7f8fb;
      --panel: #ffffff;
    }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 40px 0 56px;
    }}
    h1, h2 {{
      margin: 0;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    h1 {{
      font-size: 40px;
    }}
    h2 {{
      font-size: 22px;
      margin-top: 34px;
    }}
    p {{
      color: var(--muted);
      max-width: 760px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 24px;
    }}
    .stat, table {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgb(16 24 40 / 6%);
    }}
    .stat {{
      padding: 16px;
    }}
    .label {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .value {{
      display: block;
      margin-top: 8px;
      font-size: 28px;
      font-weight: 750;
    }}
    .distribution {{
      display: grid;
      gap: 10px;
      margin-top: 16px;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 84px 1fr 56px;
      align-items: center;
      gap: 12px;
    }}
    .bar-track {{
      height: 14px;
      background: #e4e7ec;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: var(--green);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      overflow: hidden;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 14px;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    code {{
      background: #eef2f6;
      border: 1px solid #dde3ea;
      border-radius: 6px;
      padding: 2px 6px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>LexiLab Wordle Solver Benchmark</h1>
    <p>
      Entropy-based solver results over a deterministic sample of
      {summary.sample_size} five-letter words. Each guess is chosen by simulating
      possible feedback patterns and maximizing expected information gain.
    </p>

    <section class="stats" aria-label="Benchmark summary">
      <div class="stat"><span class="label">Success Rate</span><span class="value">{summary.success_rate:.1%}</span></div>
      <div class="stat"><span class="label">Average Guesses</span><span class="value">{summary.average_guesses:.2f}</span></div>
      <div class="stat"><span class="label">Worst Success</span><span class="value">{summary.worst_success_guesses}</span></div>
      <div class="stat"><span class="label">Failures</span><span class="value">{summary.failures}</span></div>
    </section>

    <h2>Guess Distribution</h2>
    <div class="distribution">
      {distribution_rows}
    </div>

    <h2>Sample Solves</h2>
    <table>
      <thead>
        <tr>
          <th>Answer</th>
          <th>Guesses</th>
          <th>Status</th>
          <th>Path</th>
        </tr>
      </thead>
      <tbody>
        {sample_rows}
      </tbody>
    </table>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return report_path


def _distribution_row(turns: int, count: int, total: int) -> str:
    percentage = count / total if total else 0
    width = max(percentage * 100, 2 if count else 0)
    return (
        '<div class="bar-row">'
        f"<strong>{turns} guesses</strong>"
        '<div class="bar-track">'
        f'<div class="bar-fill" style="width: {width:.1f}%"></div>'
        "</div>"
        f"<span>{count}</span>"
        "</div>"
    )


def _result_row(result) -> str:
    path = " / ".join(step.guess for step in result.steps)
    status = "Solved" if result.success else "Missed"
    return (
        "<tr>"
        f"<td><code>{html.escape(result.answer)}</code></td>"
        f"<td>{result.guesses}</td>"
        f"<td>{status}</td>"
        f"<td>{html.escape(path)}</td>"
        "</tr>"
    )
