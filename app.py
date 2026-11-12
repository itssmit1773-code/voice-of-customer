"""Streamlit product decision workspace."""
import json
from calendar import monthrange
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

from voc.generate import CHANNELS, END, REGIONS, SEGMENTS, START, library, read_csv
from voc.metrics import query
from voc.pipeline import DEFAULT_OUTPUT
from voc.roadmap import EFFORT_CASE, ranked_candidates

st.set_page_config(page_title="Voice of Customer | Relayboard", page_icon="📊", layout="wide")

DATABASE = DEFAULT_OUTPUT / "voc.sqlite"
EARLIEST = date(2026, 4, 1)
LATEST = date.fromisoformat(END)
COLORS = ["#147c70", "#406ea2", "#b06a35", "#697c9a", "#8861a4", "#a74f62", "#516c59", "#96a4b3"]
st.html("""
<style>
[data-testid="stMainBlockContainer"] {max-width: 1320px; padding-top: 2.6rem;}
[data-testid="stMetric"] {background: #fff; border: 1px solid #dbe4ed;
    border-radius: 12px; padding: 1rem 1.1rem;}
[data-testid="stMetricLabel"] p {font-weight: 600; font-size: .85rem; color: #38516a;}
[data-testid="stMetricValue"] {font-weight: 650; font-variant-numeric: tabular-nums;}
[data-testid="stSidebar"] h2 {font-size: 1.15rem; letter-spacing: .02em; margin-bottom: .4rem;}
.table-scroll {overflow: auto; max-width: 100%; max-height: 380px; border: 1px solid #dbe4ed;
    border-radius: 10px; background: #fff;}
.table-scroll table {width: 100%; border-collapse: collapse; margin: 0; font-size: .85rem;}
.table-scroll th, .table-scroll td {text-align: left; padding: .65rem .8rem; vertical-align: top;
    border: 0; border-bottom: 1px solid #e4eaf0;}
.table-scroll th {position: sticky; top: 0; background: #edf2f6; white-space: nowrap; z-index: 1;}
.table-scroll td:last-child {min-width: 9rem;}
.table-scroll tbody tr:nth-child(even) {background: #f7f9fb;}
h1 {letter-spacing: -.04em;}
h2, h3 {letter-spacing: -.02em;}
</style>
""")
if not DATABASE.is_file():
    st.error("Build the dataset with python -m voc.pipeline, then refresh this page.")
    st.stop()


@st.cache_data(show_spinner=False)
def read_metric(version, metric, start, end, **filters):
    return query(DATABASE, metric, start, end, **filters)


@st.cache_data(show_spinner=False)
def read_roadmap(version):
    return ranked_candidates(DATABASE)


@st.cache_data(show_spinner=False)
def theme_names():
    return {**{key: entry["label"] for key, entry in library()["topics"].items()},
            "review": "Unclassified"}


names = theme_names()
version = DATABASE.stat().st_mtime_ns


def label_frame(rows):
    frame = pd.DataFrame(rows)
    if "topic" in frame:
        frame["theme"] = frame["topic"].map(names)
    return frame


def chart_style(chart):
    return (alt.layer(chart).configure_view(stroke=None)
            .configure_axis(gridColor="#e0e7ef", labelColor="#324a61", titleColor="#324a61")
            .configure_legend(labelColor="#324a61", titleColor="#324a61"))


def show_chart(chart):
    # Keep the small aggregates inline in the Vega-Lite layer.
    with alt.data_transformers.enable("default", consolidate_datasets=False):
        spec = chart_style(chart).to_dict()
    if "data" in spec:
        spec["layer"][0]["data"] = spec.pop("data")
    st.vega_lite_chart(spec=spec, width="stretch")


def show_table(frame, *, index=False):
    markup = frame.to_html(index=index, border=0, escape=True, na_rep="—")
    st.html(f'<div class="table-scroll" tabindex="0">{markup}</div>')


def overview():
    selected = st.sidebar.date_input("Report dates", (date.fromisoformat(START), LATEST),
                                     min_value=EARLIEST, max_value=LATEST, format="YYYY-MM-DD")
    segment = st.sidebar.multiselect("Segment", SEGMENTS, placeholder="All segments")
    region = st.sidebar.multiselect("Region", REGIONS, placeholder="All regions")
    channel = st.sidebar.multiselect("Channel", CHANNELS, placeholder="All channels")
    if len(selected) != 2:
        st.info("Select a start and end date to view feedback.")
        return
    start, end = selected
    filters = dict(segment=segment, region=region, channel=channel)
    total = read_metric(version, "overview", start, end, **filters)[0]
    if not total["reports"]:
        st.info("No reports match these dates and filters.")
        return

    for column, (title, key, description) in zip(st.columns(4), [
        ("Feedback reports", "reports", "Unique canonical reports after cross-channel deduplication."),
        ("Identified reporters", "known_reporters", "Distinct known user IDs across the selected reports."),
        ("Reporting accounts", "accounts", "Distinct account IDs, including anonymous reports."),
        ("Flagged for review", "review_queue", "Uncertain labels, possible blockers or possible access exposure."),
    ]):
        column.metric(title, f"{total[key]:,}", help=description)
    st.caption(f"{start:%d %b %Y} to {end:%d %b %Y} · "
               f"{total['anonymous_reports']:,} reports lack a user ID.")

    themes = label_frame(read_metric(version, "theme", start, end, **filters))
    history = label_frame(read_metric(version, "trend", start, end, **filters))
    leading = themes.loc[~themes["topic"].isin(("other", "review")), "theme"].tolist()
    left, right = st.columns((1, 1.2), gap="large")
    with left:
        st.subheader("Themes by share of feedback")
        bars = alt.Chart(themes).mark_bar(cornerRadiusEnd=4).encode(
            y=alt.Y("theme:N", sort="-x", title=None, axis=alt.Axis(labelLimit=200)),
            x=alt.X("report_share:Q", title="Share of reports", axis=alt.Axis(format="%")),
            color=alt.condition(alt.FieldOneOfPredicate(field="topic", oneOf=["other", "review"]),
                                alt.value("#a0afbd"), alt.value("#147c70")),
            tooltip=[alt.Tooltip("theme:N", title="Theme"), alt.Tooltip("reports:Q", title="Reports"),
                     alt.Tooltip("report_share:Q", title="Share", format=".1%"),
                     alt.Tooltip("known_reporters:Q", title="Identified reporters")],
        ).properties(height=270)
        show_chart(bars)
    with right:
        st.subheader("Monthly share of feedback")
        selected_themes = st.multiselect("Trend themes", themes["theme"].tolist(),
                                         default=(leading or themes["theme"].tolist())[:3])
        points = history[history["theme"].isin(selected_themes)].copy()
        points["period"] = pd.to_datetime(points["month"] + "-01")
        if points.empty:
            st.caption("Select a theme to show its monthly trend.")
        else:
            line = alt.Chart(points).mark_line(point=True, strokeWidth=2.5).encode(
                x=alt.X("period:T", title=None, axis=alt.Axis(format="%b %Y", tickCount="month"),
                        scale=alt.Scale(nice="month")),
                y=alt.Y("report_share:Q", title="Share of reports", axis=alt.Axis(format="%")),
                color=alt.Color("theme:N", title=None, scale=alt.Scale(range=COLORS),
                                legend=alt.Legend(orient="bottom", columns=2)),
                tooltip=[alt.Tooltip("period:T", title="Month", format="%B %Y"),
                         alt.Tooltip("theme:N", title="Theme"),
                         alt.Tooltip("reports:Q", title="Theme reports"),
                         alt.Tooltip("total_reports:Q", title="All reports"),
                         alt.Tooltip("report_share:Q", title="Share", format=".1%")],
            ).properties(height=225)
            show_chart(line)
        if start.day != 1 or end.day != monthrange(end.year, end.month)[1]:
            st.caption("Partial months use only days in the selected date range.")

    st.subheader("Segment comparison")
    focus = st.selectbox("Theme to investigate", (leading or []) +
                         [name for name in themes["theme"] if name not in leading])
    topic = next(key for key, label in names.items() if label == focus)
    segments = label_frame(read_metric(version, "segments", start, end, **filters))
    scope = segments[["segment", "segment_reports", "segment_known_reporters"]].drop_duplicates("segment")
    counts = segments[segments["theme"].eq(focus)][["segment", "reports", "known_reporters", "report_share"]]
    segment_table = scope.merge(counts, on="segment", how="left").fillna(0)
    segment_table["report_share"] = segment_table["report_share"].map(lambda value: f"{value:.1%}")
    segment_columns = {"segment": "Segment", "reports": "Theme reports", "segment_reports": "All segment reports",
                       "report_share": "Share of reports", "known_reporters": "Theme reporters",
                       "segment_known_reporters": "All identified reporters"}
    show_table(segment_table[list(segment_columns)].rename(columns=segment_columns))

    st.subheader("Feedback evidence")
    review_only = st.toggle("Flagged reports only")
    rows = label_frame(read_metric(version, "records", start, end, topic=[topic], **filters))
    if review_only:
        rows = rows[rows["needs_review"].eq(1)]
    breakdown = themes.loc[themes["topic"].eq(topic)].iloc[0]
    st.caption(f"{int(breakdown['predicted_negative']):,} negative · "
               f"{int(breakdown['predicted_blockers']):,} possible blockers · "
               f"{int(breakdown['unknown_severity']):,} with uncertain severity. Counts are text labels.")
    evidence_columns = {"event_id": "Report ID", "date": "Date", "channel": "Channel", "segment": "Segment",
                        "sentiment": "Sentiment", "severity": "Severity", "review_reason": "Review reason",
                        "text": "Feedback"}
    if rows.empty:
        st.caption("No flagged feedback in this selection.")
    else:
        page_size = 20
        pages = (len(rows) + page_size - 1) // page_size
        page = st.number_input("Evidence page", min_value=1, max_value=pages, value=1,
                               key=f"evidence_page_{topic}_{pages}")
        offset = (page - 1) * page_size
        st.caption(f"Reports {offset + 1}–{min(offset + page_size, len(rows))} of {len(rows)}")
        show_table(rows.iloc[offset:offset + page_size][list(evidence_columns)].rename(columns=evidence_columns))
    st.download_button("Download filtered evidence", rows.to_csv(index=False).encode("utf-8"),
                       "feedback-evidence.csv", "text/csv", disabled=rows.empty)


def roadmap():
    st.caption("Fixed scoring period · 1 Jul to 30 Sep 2026 · All channels, regions and segments")
    rows = read_roadmap(version)
    top, second = rows[:2]
    st.subheader("Prototype approval recovery")
    st.write(f"{top['observed_reporters']:,} identified reporters across "
             f"{top['observed_accounts']:,} accounts raised approval handoffs. "
             f"The base score is {top['rice_base']:.1f}, compared with "
             f"{second['rice_base']:.1f} for {second['name'].lower()}.")
    st.info("Possible access exposure goes to security review as soon as it is flagged.")
    scenario = st.segmented_control("Assumptions", ["Low", "Base", "High"], default="Base") or "Base"
    case = scenario.lower()
    frame = pd.DataFrame(rows).sort_values([f"rice_{case}", "topic"], ascending=[False, True])
    frame.insert(0, "scenario_rank", range(1, len(frame) + 1))
    frame["eligible"] = (frame["observed_reporters"] * frame[f"eligible_{case}"]).map("{:.1f}".format)
    frame["score"] = frame[f"rice_{case}"].map("{:.1f}".format)
    columns = {"scenario_rank": "Rank", "name": "Opportunity", "observed_reporters": "Observed reporters",
               "eligible": "Modeled reach", "score": "RICE", "next_step": "Next step", "owner": "Proposed owner"}
    show_table(frame[list(columns)].rename(columns=columns))
    st.caption("RICE = estimated eligible reporters × impact × confidence ÷ person-months. "
               "Low and high use planning assumptions. Reach covers identified reporters in the scoring period.")
    chosen = st.selectbox("Inspect assumptions", [row["name"] for row in rows])
    candidate = next(row for row in rows if row["name"] == chosen)
    st.markdown(f"**Eligibility.** {candidate['eligibility_basis']}")
    st.markdown(f"**Effort covers.** {candidate['effort_basis']}.")
    effort_case = EFFORT_CASE[case]
    st.write(f"{candidate[f'eligible_{case}']:.0%} eligible · "
             f"{candidate[f'impact_{case}']:g} impact · "
             f"{candidate[f'confidence_{case}']:.0%} confidence · "
             f"{candidate[f'effort_{effort_case}']:g} person-months")
    with st.expander("Sensitivity and breakpoints"):
        crossover = (second["rice_base"] * top["effort_base"] /
                     (top["observed_reporters"] * top["impact_base"] * top["confidence_base"]))
        st.write(f"At base impact, confidence and effort, approval eligibility below "
                 f"{crossover:.1%} puts the notification digest first at its base score.")
        sensitivity = pd.DataFrame(read_csv(DEFAULT_OUTPUT / "sensitivity.csv"))
        columns = {"changed_input": "Changed input", "level": "Level",
                   "winner": "Higher score", "runner_up": "Lower score"}
        show_table(sensitivity[list(columns)].rename(columns=columns))
    st.download_button("Download roadmap inputs and scores",
                       (DEFAULT_OUTPUT / "roadmap.csv").read_bytes(), "roadmap.csv", "text/csv")


def quality():
    st.caption("English-only text labels from a simulated corpus and hand-labeled fictional feedback.")
    evaluation = json.loads((DEFAULT_OUTPUT / "evaluation.json").read_text(encoding="utf-8"))
    sources = {"Hand-labeled audit": "audit", "Statistical baseline (same audit)": "baseline_audit",
               "Development examples": "challenge", "Full simulation": "simulation",
               "Support only": "Support", "In-app only": "In-app", "Reviews only": "Review"}
    selected = st.selectbox("Evaluation set", list(sources))
    results = evaluation[sources[selected]]
    summary = pd.DataFrame([
        {"Task": axis.title(), "Examples": result["n"], "Accuracy": result["accuracy"],
         "Macro F1": result["macro_f1"], "Coverage": result["coverage"],
         "Accepted accuracy": result["accepted_accuracy"], "Majority accuracy": result["majority_accuracy"]}
        for axis, result in results.items()
    ])
    for label in ("Accuracy", "Macro F1", "Coverage", "Accepted accuracy", "Majority accuracy"):
        summary[label] = summary[label].map(lambda value: f"{value:.1%}" if pd.notna(value) else "—")
    show_table(summary)
    st.caption("Coverage is the share receiving a label. Accuracy includes correctly routed ambiguous "
               "cases. Accepted accuracy is calculated over rows receiving a label.")
    axis = st.selectbox("Confusion matrix", list(results), format_func=str.title)
    matrix = pd.DataFrame.from_dict(results[axis]["confusion"], orient="index")
    matrix.index.name = "Expected"
    show_table(matrix, index=True)
    st.subheader("Review the misses")
    cases = pd.DataFrame(read_csv(DEFAULT_OUTPUT / "audit_predictions.csv"))
    misses = cases[[f"expected_{axis}" for axis in results]].to_numpy() != cases[
        [f"predicted_{axis}" for axis in results]].to_numpy()
    show_table(cases.loc[misses.any(axis=1)].drop(columns="channel"))
    st.caption("Examples above come from the hand-labeled audit. A review flag requires human triage.")


st.sidebar.header("Relayboard")
page = st.sidebar.radio("Workspace", ["Feedback", "Roadmap", "Model quality"])
st.sidebar.caption("Simulated product · English feedback")
st.title({"Feedback": "Voice of Customer", "Roadmap": "Product roadmap", "Model quality": "Classification quality"}[page])
st.caption("Fictional workflow SaaS · Synthetic data")
{"Feedback": overview, "Roadmap": roadmap, "Model quality": quality}[page]()
