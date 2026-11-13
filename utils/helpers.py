"""
Utility helpers for the Mock Interview Coach system.
"""

import io
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def create_radar_chart(scores_summary: dict) -> go.Figure:
    """Create a radar chart of average scores across dimensions."""
    categories = ["Correctness", "Depth", "Communication"]
    values = [
        scores_summary.get("avg_correctness", 0),
        scores_summary.get("avg_depth", 0),
        scores_summary.get("avg_communication", 0),
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.2)',
        line=dict(color='rgb(99, 102, 241)', width=2),
        name='Your Scores',
        hovertemplate='%{theta}: %{r:.1f}/10<extra></extra>'
    ))

    # Add benchmark line (7.0 = "good")
    benchmark = [7.0] * 3
    fig.add_trace(go.Scatterpolar(
        r=benchmark + [benchmark[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.05)',
        line=dict(color='rgba(16, 185, 129, 0.5)', width=1, dash='dot'),
        name='Target (7.0)',
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=10, color="#94a3b8"),
                gridcolor="rgba(148,163,184,0.2)",
                linecolor="rgba(148,163,184,0.2)"
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#e2e8f0"),
                gridcolor="rgba(148,163,184,0.2)",
                linecolor="rgba(148,163,184,0.3)"
            ),
            bgcolor="rgba(15, 23, 42, 0.0)"
        ),
        showlegend=True,
        legend=dict(
            font=dict(color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(t=20, b=20, l=40, r=40)
    )

    return fig


def create_score_timeline(answers: list[dict]) -> go.Figure:
    """Create a line chart of score progression across questions."""
    if not answers:
        return go.Figure()

    questions = [f"Q{i+1}" for i in range(len(answers))]
    correctness = [a["evaluation"].get("correctness", 0) for a in answers]
    depth = [a["evaluation"].get("depth", 0) for a in answers]
    communication = [a["evaluation"].get("communication", 0) for a in answers]
    overall = [a["evaluation"].get("overall", 0) for a in answers]

    fig = go.Figure()

    colors = {
        "Correctness": "#6366f1",
        "Depth": "#10b981",
        "Communication": "#f59e0b",
        "Overall": "#f43f5e"
    }

    for label, data, color in [
        ("Correctness", correctness, colors["Correctness"]),
        ("Depth", depth, colors["Depth"]),
        ("Communication", communication, colors["Communication"]),
        ("Overall", overall, colors["Overall"])
    ]:
        fig.add_trace(go.Scatter(
            x=questions,
            y=data,
            mode='lines+markers',
            name=label,
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color),
            hovertemplate=f'{label}: %{{y:.1f}}/10<extra></extra>'
        ))

    fig.update_layout(
        xaxis=dict(
            title="Question",
            tickfont=dict(color="#94a3b8"),
            gridcolor="rgba(148,163,184,0.1)",
            linecolor="rgba(148,163,184,0.2)"
        ),
        yaxis=dict(
            title="Score (0-10)",
            range=[0, 10.5],
            tickfont=dict(color="#94a3b8"),
            gridcolor="rgba(148,163,184,0.1)",
            linecolor="rgba(148,163,184,0.2)"
        ),
        legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.4)",
        height=300,
        margin=dict(t=20, b=40, l=50, r=20)
    )

    return fig


def create_score_gauge(score: float, title: str = "Overall Score") -> go.Figure:
    """Create a gauge chart for a single score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#94a3b8'}},
        number={'font': {'size': 36, 'color': '#e2e8f0'}, 'suffix': '/10'},
        gauge={
            'axis': {'range': [0, 10], 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': _gauge_color(score)},
            'bgcolor': 'rgba(15,23,42,0.4)',
            'borderwidth': 1,
            'bordercolor': 'rgba(148,163,184,0.2)',
            'steps': [
                {'range': [0, 4], 'color': 'rgba(239,68,68,0.1)'},
                {'range': [4, 7], 'color': 'rgba(245,158,11,0.1)'},
                {'range': [7, 10], 'color': 'rgba(16,185,129,0.1)'},
            ],
            'threshold': {
                'line': {'color': '#6366f1', 'width': 2},
                'thickness': 0.75,
                'value': 7
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(t=30, b=10, l=30, r=30)
    )
    return fig


def _gauge_color(score: float) -> str:
    if score >= 7:
        return "#10b981"
    elif score >= 4:
        return "#f59e0b"
    return "#ef4444"


def format_score_badge(score: float) -> str:
    """Return HTML badge for a score."""
    if score >= 8:
        color = "#10b981"
        label = "Excellent"
    elif score >= 6:
        color = "#6366f1"
        label = "Good"
    elif score >= 4:
        color = "#f59e0b"
        label = "Fair"
    else:
        color = "#ef4444"
        label = "Needs Work"

    return f'<span style="background:{color}22;color:{color};border:1px solid {color}44;padding:2px 10px;border-radius:12px;font-size:0.8rem;font-weight:600">{score:.1f} — {label}</span>'


def export_report_txt(report_text: str, company: str, role: str) -> bytes:
    """Convert report markdown to plain text bytes for download."""
    # Strip basic markdown formatting for plain text
    import re
    text = re.sub(r'#{1,6}\s', '', report_text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    return text.encode('utf-8')
