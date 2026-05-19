import html
import json
from pathlib import Path


def write_summary(run_dir, *, started_at, concurrency, results):
    run_dir = Path(run_dir)
    payload = {
        "started_at": started_at,
        "concurrency": concurrency,
        "results": [result.to_dict() for result in results],
    }
    summary_path = run_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return summary_path


def write_index_html(run_dir, *, started_at, concurrency, results):
    run_dir = Path(run_dir)
    rows = []
    instance_rowspans = []
    index = 0
    while index < len(results):
        instance = results[index].instance
        count = 1
        while index + count < len(results) and results[index + count].instance == instance:
            count += 1
        instance_rowspans.extend([count] + [0] * (count - 1))
        index += count

    for result, instance_rowspan in zip(results, instance_rowspans):
        report = result.report or ""
        error = getattr(result, "error", None) or ""
        report_cell = f'<a href="{html.escape(report)}">report</a>' if report else ""
        instance_cell = ""
        if instance_rowspan:
            instance_cell = (
                f'<td class="instance-cell" rowspan="{instance_rowspan}">'
                f"{html.escape(result.instance)}"
                "</td>"
            )
        rows.append(
            "<tr>"
            f"{instance_cell}"
            f"<td>{html.escape(result.case or '-')}</td>"
            f"<td>{html.escape(result.status)}</td>"
            f"<td>{html.escape(result.stage)}</td>"
            f"<td>{html.escape(str(result.duration_seconds or ''))}</td>"
            f"<td>{report_cell}</td>"
            f"<td>{html.escape(error)}</td>"
            "</tr>"
        )

    passed = sum(1 for result in results if result.status == "passed")
    failed = sum(1 for result in results if result.status == "failed")
    index_path = run_dir / "index.html"
    document = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Spark Airtest Runner 汇总报告</title>
  <style>
    body {{ margin: 0; padding: 32px; font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif; color: #1f2937; background: #f7f8fa; }}
    main {{ max-width: 1180px; margin: 0 auto; }}
    h1 {{ margin: 0 0 12px; font-size: 28px; }}
    .meta {{ margin-bottom: 20px; color: #5f6b7a; }}
    .summary {{ display: flex; gap: 12px; margin: 18px 0; }}
    .summary div {{ background: #fff; border: 1px solid #d8dee8; border-radius: 8px; padding: 12px 16px; min-width: 120px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #d8dee8; }}
    th, td {{ border: 1px solid #d8dee8; padding: 9px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #eef2f7; }}
    .instance-cell {{ background: #fafcff; font-weight: 600; }}
    a {{ color: #2563eb; }}
  </style>
</head>
<body>
<main>
  <h1>Spark Airtest Runner 汇总报告</h1>
  <div class="meta">开始时间：{html.escape(started_at)}；并发数：{html.escape(str(concurrency))}</div>
  <section class="summary">
    <div>总数<br><strong>{len(results)}</strong></div>
    <div>通过<br><strong>{passed}</strong></div>
    <div>失败<br><strong>{failed}</strong></div>
  </section>
  <table>
    <thead>
      <tr>
        <th>实例</th>
        <th>用例</th>
        <th>状态</th>
        <th>阶段</th>
        <th>耗时秒</th>
        <th>报告</th>
        <th>错误</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</main>
</body>
</html>
"""
    with index_path.open("w", encoding="utf-8") as file:
        file.write(document)
    return index_path
