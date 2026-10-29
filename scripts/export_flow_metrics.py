#!/usr/bin/env python3
"""Export real GitHub issue flow data without inventing tracker timestamps."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path


API = "https://api.github.com"
STATUSES = ["Backlog", "Ready", "In Progress", "Review", "Test", "Waiting for customer", "Done"]
STATUS_LABELS = {
    "status:backlog": "Backlog",
    "status:ready": "Ready",
    "status:in-progress": "In Progress",
    "status:review": "Review",
    "status:test": "Test",
    "status:waiting-customer": "Waiting for customer",
    "status:done": "Done",
}


def api_get(path: str, token: str | None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "fitclub-flow-export"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="owner/repository")
    p.add_argument("--sprint", required=True, help="GitHub milestone title")
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--start", required=True, type=date.fromisoformat, help="Sprint start date, YYYY-MM-DD")
    p.add_argument("--end", required=True, type=date.fromisoformat, help="Sprint end date, YYYY-MM-DD")
    return p.parse_args()


def event_time(event):
    value = event.get("created_at")
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def status_at(issue, events, snapshot):
    status = "Backlog"
    for event in sorted(events, key=lambda e: e.get("created_at") or ""):
        occurred = event_time(event)
        if not occurred or occurred > snapshot:
            continue
        label = (event.get("label") or {}).get("name")
        if event.get("event") == "labeled" and label in STATUS_LABELS:
            status = STATUS_LABELS[label]
        elif event.get("event") == "unlabeled" and label in STATUS_LABELS and status == STATUS_LABELS[label]:
            status = "Backlog"
    closed = issue.get("closed_at")
    if closed and datetime.fromisoformat(closed.replace("Z", "+00:00")) <= snapshot:
        return "Done"
    return status


def nearest_rank_p85(values):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[math.ceil(0.85 * len(ordered)) - 1]


def main() -> int:
    args = parse_args()
    if args.end < args.start:
        raise SystemExit("--end must not be earlier than --start")
    token = os.environ.get("GITHUB_TOKEN")
    issues = api_get(f"/repos/{args.repo}/issues?state=all&per_page=100", token)
    selected = [
        i for i in issues
        if "pull_request" not in i and i.get("milestone") and i["milestone"]["title"] == args.sprint
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    raw = []
    rows = []
    tracked = []
    for issue in selected:
        events = api_get(f"/repos/{args.repo}/issues/{issue['number']}/events?per_page=100", token)
        raw.append({"issue": issue, "events": events})
        tracked.append((issue, events))
        started = None
        for event in events:
            label = (event.get("label") or {}).get("name")
            if event.get("event") == "labeled" and label == "status:in-progress":
                started = started or event.get("created_at")
        closed = issue.get("closed_at")
        cycle_hours = None
        if started and closed:
            a = datetime.fromisoformat(started.replace("Z", "+00:00"))
            b = datetime.fromisoformat(closed.replace("Z", "+00:00"))
            cycle_hours = round((b - a).total_seconds() / 3600, 3)
        rows.append({
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "created_at": issue["created_at"],
            "first_in_progress_at": started or "",
            "closed_at": closed or "",
            "cycle_time_hours": "" if cycle_hours is None else cycle_hours,
            "labels": ";".join(sorted(x["name"] for x in issue.get("labels", []))),
            "url": issue["html_url"],
        })
    (args.out / "raw-issues-events.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    with (args.out / "work-items.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        fields = list(rows[0]) if rows else ["number", "title", "state", "created_at", "first_in_progress_at", "closed_at", "cycle_time_hours", "labels", "url"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    exported_at = datetime.now(timezone.utc)
    start_at = datetime.combine(args.start, time.min, tzinfo=timezone.utc)
    end_at = datetime.combine(args.end, time.max, tzinfo=timezone.utc)
    cfd_through = min(args.end, exported_at.date())
    cfd_rows = []
    day = args.start
    while day <= cfd_through:
        snapshot = datetime.combine(day, time.max, tzinfo=timezone.utc)
        counts = {status: 0 for status in STATUSES}
        for issue, events in tracked:
            counts[status_at(issue, events, snapshot)] += 1
        cfd_rows.append({"date": day.isoformat(), **counts})
        day += timedelta(days=1)
    with (args.out / "daily-cfd.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["date", *STATUSES])
        writer.writeheader()
        writer.writerows(cfd_rows)

    event_snapshots = {start_at}
    snapshot_ceiling = min(end_at, exported_at)
    for issue, events in tracked:
        for event in events:
            occurred = event_time(event)
            label = (event.get("label") or {}).get("name")
            if occurred and start_at <= occurred <= snapshot_ceiling and (
                (event.get("event") in {"labeled", "unlabeled"} and label in STATUS_LABELS)
                or event.get("event") in {"closed", "reopened"}
            ):
                event_snapshots.add(occurred)
    event_cfd_rows = []
    for snapshot in sorted(event_snapshots):
        counts = {status: 0 for status in STATUSES}
        for issue, events in tracked:
            counts[status_at(issue, events, snapshot)] += 1
        event_cfd_rows.append({"timestamp": snapshot.isoformat(), **counts})
    with (args.out / "event-cfd.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", *STATUSES])
        writer.writeheader()
        writer.writerows(event_cfd_rows)

    completed_in_window = []
    cycle_values = []
    for row in rows:
        if not row["closed_at"]:
            continue
        closed_at = datetime.fromisoformat(row["closed_at"].replace("Z", "+00:00"))
        if start_at <= closed_at <= end_at:
            completed_in_window.append(row)
            if row["cycle_time_hours"] != "":
                cycle_values.append(float(row["cycle_time_hours"]))
    summary = {
        "repository": args.repo,
        "milestone": args.sprint,
        "exported_at": exported_at.isoformat(),
        "work_item_count": len(rows),
        "sprint_start": args.start.isoformat(),
        "sprint_end": args.end.isoformat(),
        "cfd_through": cfd_through.isoformat(),
        "throughput": len(completed_in_window),
        "measured_cycle_time_count": len(cycle_values),
        "average_cycle_time_hours": round(sum(cycle_values) / len(cycle_values), 3) if cycle_values else None,
        "p85_cycle_time_hours": nearest_rank_p85(cycle_values),
        "note": "No value is imputed when a required GitHub event is absent.",
    }
    (args.out / "export-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        print(f"GitHub API error: {exc.code}", file=sys.stderr)
        raise SystemExit(2)
