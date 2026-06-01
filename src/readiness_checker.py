from pathlib import Path
import csv
from collections import Counter
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ISSUE_LOG_FILE = PROJECT_ROOT / "templates" / "issue_log_template.csv"
RISK_REGISTER_FILE = PROJECT_ROOT / "templates" / "risk_register_template.csv"

REPORTS_DIR = PROJECT_ROOT / "reports"
SUMMARY_FILE = REPORTS_DIR / "launch_readiness_summary.csv"
REPORT_FILE = REPORTS_DIR / "launch_readiness_report.md"


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def is_open_status(status: str) -> bool:
    return status.strip().lower() in {"open", "in progress", "pending", "blocked"}


def normalize(value: str) -> str:
    return value.strip().upper()


def evaluate_launch_readiness(issues: list[dict], risks: list[dict]) -> dict:
    open_issues = [
        issue for issue in issues
        if is_open_status(issue.get("status", ""))
    ]

    open_risks = [
        risk for risk in risks
        if is_open_status(risk.get("status", ""))
    ]

    critical_open_issues = [
        issue for issue in open_issues
        if normalize(issue.get("severity", "")) == "CRITICAL"
    ]

    high_open_issues = [
        issue for issue in open_issues
        if normalize(issue.get("severity", "")) == "HIGH"
    ]

    critical_open_risks = [
        risk for risk in open_risks
        if normalize(risk.get("impact", "")) == "CRITICAL"
    ]

    high_open_risks = [
        risk for risk in open_risks
        if normalize(risk.get("impact", "")) == "HIGH"
    ]

    if critical_open_issues or critical_open_risks:
        decision = "NO-GO"
        reason = (
            "At least one critical open issue or critical open risk remains. "
            "Commercial launch should not proceed."
        )
    elif high_open_issues or high_open_risks:
        decision = "GO WITH MONITORING"
        reason = (
            "High-impact open issue or risk remains. Launch may proceed only "
            "with agreed mitigation, monitoring, and ownership."
        )
    else:
        decision = "GO"
        reason = "No blocking issue or high-impact open risk remains."

    return {
        "decision": decision,
        "reason": reason,
        "total_issues": len(issues),
        "open_issues": len(open_issues),
        "critical_open_issues": len(critical_open_issues),
        "high_open_issues": len(high_open_issues),
        "total_risks": len(risks),
        "open_risks": len(open_risks),
        "critical_open_risks": len(critical_open_risks),
        "high_open_risks": len(high_open_risks),
    }


def write_summary_csv(summary: dict) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    fieldnames = [
        "decision",
        "reason",
        "total_issues",
        "open_issues",
        "critical_open_issues",
        "high_open_issues",
        "total_risks",
        "open_risks",
        "critical_open_risks",
        "high_open_risks",
    ]

    with SUMMARY_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary)


def count_by_field(rows: list[dict], field: str) -> Counter:
    return Counter(row.get(field, "Unknown") for row in rows)


def write_markdown_report(
    summary: dict,
    issues: list[dict],
    risks: list[dict],
) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    issue_severity_counts = count_by_field(issues, "severity")
    risk_impact_counts = count_by_field(risks, "impact")

    lines = []

    lines.append("# MNO Roaming Launch Readiness Report")
    lines.append("")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Launch Decision")
    lines.append("")
    lines.append(f"**Decision:** {summary['decision']}")
    lines.append("")
    lines.append(f"**Reason:** {summary['reason']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total issues: {summary['total_issues']}")
    lines.append(f"- Open issues: {summary['open_issues']}")
    lines.append(f"- Critical open issues: {summary['critical_open_issues']}")
    lines.append(f"- High open issues: {summary['high_open_issues']}")
    lines.append(f"- Total risks: {summary['total_risks']}")
    lines.append(f"- Open risks: {summary['open_risks']}")
    lines.append(f"- Critical open risks: {summary['critical_open_risks']}")
    lines.append(f"- High open risks: {summary['high_open_risks']}")
    lines.append("")
    lines.append("## Issue Severity Breakdown")
    lines.append("")

    for severity, count in issue_severity_counts.items():
        lines.append(f"- {severity}: {count}")

    lines.append("")
    lines.append("## Risk Impact Breakdown")
    lines.append("")

    for impact, count in risk_impact_counts.items():
        lines.append(f"- {impact}: {count}")

    lines.append("")
    lines.append("## Open Issues")
    lines.append("")

    open_issues = [
        issue for issue in issues
        if is_open_status(issue.get("status", ""))
    ]

    if not open_issues:
        lines.append("No open issues.")
    else:
        for issue in open_issues:
            lines.append(
                f"- {issue.get('issue_id')} | {issue.get('severity')} | "
                f"{issue.get('workflow_area')} | {issue.get('description')}"
            )

    lines.append("")
    lines.append("## Open Risks")
    lines.append("")

    open_risks = [
        risk for risk in risks
        if is_open_status(risk.get("status", ""))
    ]

    if not open_risks:
        lines.append("No open risks.")
    else:
        for risk in open_risks:
            lines.append(
                f"- {risk.get('risk_id')} | {risk.get('impact')} | "
                f"{risk.get('risk_area')} | {risk.get('risk_description')}"
            )

    lines.append("")
    lines.append("## Recommended Next Actions")
    lines.append("")

    if summary["decision"] == "NO-GO":
        lines.append("- Do not proceed to commercial launch.")
        lines.append("- Close critical open issues and critical open risks first.")
        lines.append("- Repeat launch readiness review after mitigation.")
    elif summary["decision"] == "GO WITH MONITORING":
        lines.append("- Launch may proceed only with monitoring and mitigation plan.")
        lines.append("- Assign owners for all high-severity issues and high-impact risks.")
        lines.append("- Review post-launch monitoring window and escalation path.")
    else:
        lines.append("- Proceed to launch readiness approval.")
        lines.append("- Keep monitoring and escalation process active.")

    lines.append("")
    lines.append("## Disclaimer")
    lines.append("")
    lines.append(
        "This is a simulated portfolio report. It does not use real operator data, "
        "confidential partner information, or production roaming launch records."
    )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    issues = read_csv(ISSUE_LOG_FILE)
    risks = read_csv(RISK_REGISTER_FILE)

    summary = evaluate_launch_readiness(issues, risks)

    write_summary_csv(summary)
    write_markdown_report(summary, issues, risks)

    print("Launch readiness evaluation completed.")
    print(f"Decision: {summary['decision']}")
    print(f"Summary written to: {SUMMARY_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Report written to: {REPORT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()