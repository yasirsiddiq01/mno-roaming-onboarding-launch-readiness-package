from pathlib import Path
from datetime import datetime
import subprocess
import sys

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RUN_PROJECT_FILE = PROJECT_ROOT / "run_project.py"

ISSUE_LOG_FILE = PROJECT_ROOT / "templates" / "issue_log_template.csv"
RISK_REGISTER_FILE = PROJECT_ROOT / "templates" / "risk_register_template.csv"

SUMMARY_FILE = PROJECT_ROOT / "reports" / "launch_readiness_summary.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "launch_readiness_report.md"

INTEGRATION_PLAN_FILE = PROJECT_ROOT / "docs" / "integration_plan.md"
TEST_PLAN_FILE = PROJECT_ROOT / "docs" / "end_to_end_test_plan.md"
LAUNCH_CHECKLIST_FILE = PROJECT_ROOT / "docs" / "launch_readiness_checklist.md"
BILLING_CHECKLIST_FILE = PROJECT_ROOT / "docs" / "billing_validation_checklist.md"


st.set_page_config(
    page_title="MNO Roaming Launch Readiness Package",
    layout="wide",
)


OPEN_STATUSES = {"open", "in progress", "pending", "blocked"}


def run_pipeline():
    result = subprocess.run(
        [sys.executable, str(RUN_PROJECT_FILE)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    output_parts = []

    if result.stdout:
        output_parts.append(result.stdout)

    if result.stderr:
        output_parts.append("STDERR:\n" + result.stderr)

    return result.returncode == 0, "\n".join(output_parts)


def read_csv_file(path):
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not read CSV file: {path.name}. Error: {exc}")
        return pd.DataFrame()


def read_markdown_file(path):
    if not path.exists():
        return "File not found."

    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Could not read Markdown file: {path.name}. Error: {exc}"


def is_open_status(value):
    return str(value).strip().lower() in OPEN_STATUSES


def open_rows(df):
    if df.empty or "status" not in df.columns:
        return pd.DataFrame()

    mask = df["status"].apply(is_open_status)
    return df[mask]


def count_open_rows(df):
    return len(open_rows(df))


def count_open_by_value(df, value_column, target_value):
    if df.empty or "status" not in df.columns or value_column not in df.columns:
        return 0

    open_df = open_rows(df)

    return int(
        (
            open_df[value_column]
            .astype(str)
            .str.strip()
            .str.upper()
            == target_value.upper()
        ).sum()
    )


def evaluate_decision(issue_df, risk_df):
    critical_open_issues = count_open_by_value(issue_df, "severity", "CRITICAL")
    high_open_issues = count_open_by_value(issue_df, "severity", "HIGH")

    critical_open_risks = count_open_by_value(risk_df, "impact", "CRITICAL")
    high_open_risks = count_open_by_value(risk_df, "impact", "HIGH")

    if critical_open_issues > 0 or critical_open_risks > 0:
        return (
            "NO-GO",
            "At least one critical open issue or critical open risk remains. Commercial launch should not proceed.",
        )

    if high_open_issues > 0 or high_open_risks > 0:
        return (
            "GO WITH MONITORING",
            "High-impact open issue or risk remains. Launch may proceed only with agreed mitigation, monitoring, and ownership.",
        )

    return (
        "GO",
        "No blocking issue or high-impact open risk remains.",
    )


def get_last_updated_text(path):
    if not path.exists():
        return "Last report updated: not available"

    modified_time = path.stat().st_mtime
    last_updated = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
    return f"Last report updated: {last_updated}"


def render_pipeline_output():
    if "pipeline_message" not in st.session_state:
        return

    if st.session_state.get("last_pipeline_success"):
        st.success(st.session_state["pipeline_message"])
    else:
        st.error(st.session_state["pipeline_message"])

    with st.expander("Pipeline Output", expanded=False):
        st.code(st.session_state.get("last_pipeline_output", ""))


def render_issue_chart(issue_df):
    if issue_df.empty:
        st.warning("No issue data available.")
        return

    if "severity" in issue_df.columns:
        st.write("Issues by Severity")
        counts = issue_df["severity"].value_counts().reset_index()
        counts.columns = ["severity", "count"]
        st.bar_chart(counts.set_index("severity"))

    if "workflow_area" in issue_df.columns:
        st.write("Issues by Workflow Area")
        counts = issue_df["workflow_area"].value_counts().reset_index()
        counts.columns = ["workflow_area", "count"]
        st.bar_chart(counts.set_index("workflow_area"))


def render_risk_chart(risk_df):
    if risk_df.empty:
        st.warning("No risk data available.")
        return

    if "impact" in risk_df.columns:
        st.write("Risks by Impact")
        counts = risk_df["impact"].value_counts().reset_index()
        counts.columns = ["impact", "count"]
        st.bar_chart(counts.set_index("impact"))

    if "risk_area" in risk_df.columns:
        st.write("Risks by Area")
        counts = risk_df["risk_area"].value_counts().reset_index()
        counts.columns = ["risk_area", "count"]
        st.bar_chart(counts.set_index("risk_area"))


st.title("MNO Roaming Onboarding and Launch Readiness Package")

st.write(
    "Interactive dashboard for a simulated MNO roaming partner onboarding and "
    "commercial launch readiness workflow. The app evaluates open issues and risks, "
    "then generates a Go / Go-with-Monitoring / No-Go launch readiness decision."
)

st.divider()

with st.sidebar:
    st.header("Pipeline Control")

    run_button = st.button("Run Launch Readiness Check")

    st.divider()

    st.header("Project Files")
    st.write(f"Issue log: `{ISSUE_LOG_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Risk register: `{RISK_REGISTER_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Summary: `{SUMMARY_FILE.relative_to(PROJECT_ROOT)}`")
    st.write(f"Report: `{REPORT_FILE.relative_to(PROJECT_ROOT)}`")

    with st.expander("Debug file check", expanded=False):
        st.write(f"Issue log exists: `{ISSUE_LOG_FILE.exists()}`")
        st.write(f"Risk register exists: `{RISK_REGISTER_FILE.exists()}`")
        st.write(f"Summary exists: `{SUMMARY_FILE.exists()}`")
        st.write(f"Report exists: `{REPORT_FILE.exists()}`")


if run_button:
    with st.spinner("Running launch readiness checker..."):
        success, output = run_pipeline()

    st.session_state["last_pipeline_output"] = output
    st.session_state["last_pipeline_success"] = success

    if success:
        st.session_state["pipeline_message"] = "Launch readiness check completed successfully."
    else:
        st.session_state["pipeline_message"] = "Launch readiness check failed."


render_pipeline_output()

issue_df = read_csv_file(ISSUE_LOG_FILE)
risk_df = read_csv_file(RISK_REGISTER_FILE)
summary_df = read_csv_file(SUMMARY_FILE)

decision, reason = evaluate_decision(issue_df, risk_df)

st.subheader("Launch Readiness Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Launch Decision", decision)

with col2:
    st.metric("Open Issues", count_open_rows(issue_df))

with col3:
    st.metric("Open Risks", count_open_rows(risk_df))

with col4:
    st.metric("Total Risks", len(risk_df))

st.caption(get_last_updated_text(SUMMARY_FILE))

if decision == "NO-GO":
    st.error(reason)
elif decision == "GO WITH MONITORING":
    st.warning(reason)
else:
    st.success(reason)

st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Readiness Summary",
        "Issue Log",
        "Risk Register",
        "Charts",
        "Generated Report",
        "Documentation",
    ]
)

with tab1:
    st.subheader("Launch Readiness Summary")

    if summary_df.empty:
        st.warning("No generated summary found. Click 'Run Launch Readiness Check' first.")
    else:
        st.dataframe(summary_df, use_container_width=True)

with tab2:
    st.subheader("Issue Log")

    if issue_df.empty:
        st.warning("No issue log data found.")
    else:
        st.dataframe(issue_df, use_container_width=True)

with tab3:
    st.subheader("Risk Register")

    if risk_df.empty:
        st.warning("No risk register data found.")
    else:
        st.dataframe(risk_df, use_container_width=True)

with tab4:
    st.subheader("Issue and Risk Charts")

    col_left, col_right = st.columns(2)

    with col_left:
        render_issue_chart(issue_df)

    with col_right:
        render_risk_chart(risk_df)

with tab5:
    st.subheader("Generated Launch Readiness Report")
    st.markdown(read_markdown_file(REPORT_FILE))

with tab6:
    st.subheader("Project Documentation")

    doc_choice = st.selectbox(
        "Select document",
        [
            "Integration Plan",
            "End-to-End Test Plan",
            "Launch Readiness Checklist",
            "Billing Validation Checklist",
        ],
    )

    if doc_choice == "Integration Plan":
        st.markdown(read_markdown_file(INTEGRATION_PLAN_FILE))
    elif doc_choice == "End-to-End Test Plan":
        st.markdown(read_markdown_file(TEST_PLAN_FILE))
    elif doc_choice == "Launch Readiness Checklist":
        st.markdown(read_markdown_file(LAUNCH_CHECKLIST_FILE))
    elif doc_choice == "Billing Validation Checklist":
        st.markdown(read_markdown_file(BILLING_CHECKLIST_FILE))