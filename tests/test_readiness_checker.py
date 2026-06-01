from pathlib import Path
import sys
import unittest


sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from readiness_checker import evaluate_launch_readiness


def make_issue(issue_id="ISS-TEST", severity="High", status="Open"):
    return {
        "issue_id": issue_id,
        "date_opened": "2026-06-01",
        "partner": "Simulated MNO Partner",
        "test_case_id": "TC-001",
        "severity": severity,
        "workflow_area": "Authentication",
        "description": "Test issue",
        "owner": "Roaming Integration Engineer",
        "status": status,
        "target_resolution_date": "2026-06-05",
        "resolution_notes": "Pending",
    }


def make_risk(risk_id="RISK-TEST", impact="High", status="Open"):
    return {
        "risk_id": risk_id,
        "risk_area": "Launch Readiness",
        "risk_description": "Test risk",
        "impact": impact,
        "likelihood": "Medium",
        "mitigation": "Test mitigation",
        "owner": "Roaming Integration Engineer",
        "status": status,
    }


class TestReadinessChecker(unittest.TestCase):

    def test_go_when_no_open_issues_or_risks(self):
        issues = [
            make_issue(severity="Critical", status="Closed"),
            make_issue(severity="High", status="Closed"),
        ]

        risks = [
            make_risk(impact="Critical", status="Closed"),
            make_risk(impact="High", status="Closed"),
        ]

        summary = evaluate_launch_readiness(issues, risks)

        self.assertEqual(summary["decision"], "GO")
        self.assertEqual(summary["open_issues"], 0)
        self.assertEqual(summary["open_risks"], 0)

    def test_no_go_when_critical_issue_is_open(self):
        issues = [
            make_issue(severity="Critical", status="Open"),
        ]

        risks = []

        summary = evaluate_launch_readiness(issues, risks)

        self.assertEqual(summary["decision"], "NO-GO")
        self.assertEqual(summary["critical_open_issues"], 1)

    def test_no_go_when_critical_risk_is_open(self):
        issues = []

        risks = [
            make_risk(impact="Critical", status="Open"),
        ]

        summary = evaluate_launch_readiness(issues, risks)

        self.assertEqual(summary["decision"], "NO-GO")
        self.assertEqual(summary["critical_open_risks"], 1)

    def test_go_with_monitoring_when_high_issue_is_open(self):
        issues = [
            make_issue(severity="High", status="Open"),
        ]

        risks = []

        summary = evaluate_launch_readiness(issues, risks)

        self.assertEqual(summary["decision"], "GO WITH MONITORING")
        self.assertEqual(summary["high_open_issues"], 1)

    def test_go_with_monitoring_when_high_risk_is_open(self):
        issues = []

        risks = [
            make_risk(impact="High", status="Open"),
        ]

        summary = evaluate_launch_readiness(issues, risks)

        self.assertEqual(summary["decision"], "GO WITH MONITORING")
        self.assertEqual(summary["high_open_risks"], 1)


if __name__ == "__main__":
    unittest.main()