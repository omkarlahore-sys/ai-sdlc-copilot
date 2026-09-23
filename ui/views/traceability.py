"""Traceability: a connected chain diagram followed by the matrix table.

Every edge is drawn from a real ``parent_*_id`` on the artifact, so the
picture cannot disagree with the data behind it.
"""

from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from ui.mock_data import build_traceability_rows
from ui.theme import TYPE_COLORS

Bundle = dict[str, Any]

NODE_W = 168
NODE_H = 44
COL_GAP = 60
ROW_GAP = 12
PAD_X = 10
PAD_Y = 26

COLUMNS = [
    ("Business Requirement", "BR"),
    ("Epic", "EP"),
    ("User Story", "US"),
    ("Acceptance Criteria", "AC"),
    ("Test Case", "TC"),
]


def _layout(columns: list[list[tuple[str, str]]], height: int) -> dict[str, tuple[int, int]]:
    """Vertically centre each column; return id -> (left x, centre y)."""
    positions: dict[str, tuple[int, int]] = {}
    for index, items in enumerate(columns):
        if not items:
            continue
        x = PAD_X + index * (NODE_W + COL_GAP)
        block = len(items) * NODE_H + (len(items) - 1) * ROW_GAP
        top = PAD_Y + max(0, (height - PAD_Y - 16 - block) / 2)
        for row, (node_id, _label) in enumerate(items):
            positions[node_id] = (x, int(top + row * (NODE_H + ROW_GAP) + NODE_H / 2))
    return positions


def _node(
    x: int, cy: int, node_id: str, label: str, color: str, faded: bool, order: int = 0
) -> str:
    y = cy - NODE_H / 2
    text = label if len(label) <= 24 else label[:23] + "…"
    return (
        f'<g class="trace-node" style="animation-delay:{0.4 + order * 0.03:.2f}s" '
        f'opacity="{"0.25" if faded else "1"}">'
        f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" rx="6" '
        f'fill="#ffffff" stroke="{color}" stroke-width="1.3"/>'
        f'<rect x="{x}" y="{y}" width="3" height="{NODE_H}" rx="1.5" fill="{color}"/>'
        f'<text x="{x + 10}" y="{y + 16}" font-size="10" font-weight="700" fill="{color}" '
        f"font-family=\"'JetBrains Mono', monospace\">{escape(node_id)}</text>"
        f'<text x="{x + 10}" y="{y + 29}" font-size="9.5" fill="#5c5142" '
        f"font-family=\"'Inter Tight', sans-serif\">{escape(text)}</text>"
        f"</g>"
    )


def _edge(
    x1: int, y1: int, x2: int, y2: int, color: str, faded: bool, order: int = 0
) -> str:
    mid = (x1 + x2) / 2
    return (
        f'<path class="trace-edge" style="animation-delay:{order * 0.03:.2f}s" '
        f'd="M {x1} {y1} C {mid} {y1}, {mid} {y2}, {x2} {y2}" fill="none" '
        f'stroke="{color}" stroke-width="1.4" opacity="{"0.12" if faded else "0.55"}"/>'
    )


def _lit_path(bundle: Bundle, test_case_id: str) -> set[str]:
    """The five ids on one test case's path back to the requirement."""
    tc = next((t for t in bundle["test_cases"] if t["id"] == test_case_id), None)
    if tc is None:
        return set()
    return {
        bundle["business_requirement"]["id"],
        tc.get("parent_ep_id", ""),
        tc.get("parent_us_id", ""),
        tc.get("parent_ac_id", ""),
        tc["id"],
    } - {""}


def render_diagram(bundle: Bundle, focus: str = "") -> None:
    br = bundle["business_requirement"]
    columns: list[list[tuple[str, str]]] = [
        [(br["id"], "Business requirement")],
        [(e["id"], e["title"]) for e in bundle["epics"]],
        [(s["id"], s["title"]) for s in bundle["user_stories"]],
        [(a["id"], a["then"]) for a in bundle["acceptance_criteria"]],
        [(t["id"], t["title"]) for t in bundle["test_cases"]],
    ]

    tallest = max((len(c) for c in columns), default=1)
    height = int(PAD_Y + tallest * NODE_H + (tallest - 1) * ROW_GAP + 18)
    width = PAD_X * 2 + len(columns) * NODE_W + (len(columns) - 1) * COL_GAP

    positions = _layout(columns, height)
    lit = _lit_path(bundle, focus) if focus else set()

    def faded(*ids: str) -> bool:
        return bool(lit) and not all(i in lit for i in ids)

    edges: list[tuple[str, str, str]] = []
    edges += [(br["id"], e["id"], TYPE_COLORS["EP"]) for e in bundle["epics"]]
    edges += [
        (s["parent_ep_id"], s["id"], TYPE_COLORS["US"]) for s in bundle["user_stories"]
    ]
    edges += [
        (a["parent_us_id"], a["id"], TYPE_COLORS["AC"])
        for a in bundle["acceptance_criteria"]
    ]
    edges += [
        (t["parent_ac_id"], t["id"], TYPE_COLORS["TC"]) for t in bundle["test_cases"]
    ]

    edge_svg = "".join(
        _edge(
            positions[src][0] + NODE_W,
            positions[src][1],
            positions[dst][0],
            positions[dst][1],
            color,
            faded(src, dst),
            order,
        )
        for order, (src, dst, color) in enumerate(
            e for e in edges if e[0] in positions and e[1] in positions
        )
    )

    node_svg = "".join(
        _node(
            positions[node_id][0],
            positions[node_id][1],
            node_id,
            label,
            TYPE_COLORS[COLUMNS[index][1]],
            faded(node_id),
            index,
        )
        for index, items in enumerate(columns)
        for node_id, label in items
        if node_id in positions
    )

    headers = "".join(
        f'<text x="{PAD_X + i * (NODE_W + COL_GAP)}" y="12" font-size="9" '
        f'font-weight="700" fill="#82765f" letter-spacing="1" '
        f"font-family=\"'JetBrains Mono', monospace\">{name.upper()}</text>"
        for i, (name, _abbr) in enumerate(COLUMNS)
    )

    st.markdown(
        f'<div style="overflow-x:auto;background:var(--surface);'
        f'border:1px solid var(--card-line);border-radius:14px;padding:14px;box-shadow:0 6px 18px rgba(60,45,20,.05)">'
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" style="min-width:{width}px" '
        f'aria-label="Traceability chain from business requirement to test cases">'
        f"{headers}{edge_svg}{node_svg}</svg></div>",
        unsafe_allow_html=True,
    )


def render(bundle: Bundle) -> None:
    st.markdown(
        '<p style="font-size:22px;font-weight:700;margin:0 0 6px;'
        'letter-spacing:-.015em">Requirement to test chain</p>'
        '<p style="font-size:14px;color:var(--muted);margin:0 0 18px;'
        'max-width:70ch;line-height:1.55">Each line is a parent reference '
        "carried by the artifact. Pick a test case to trace a single path "
        "back to the requirement.</p>",
        unsafe_allow_html=True,
    )

    picker, _spacer = st.columns([1.1, 3], gap="medium")
    with picker:
        options = ["All artifacts"] + [t["id"] for t in bundle["test_cases"]]
        choice = st.selectbox(
            "Highlight path for",
            options,
            key="trace_focus",
            label_visibility="collapsed",
        )

    render_diagram(bundle, "" if choice == "All artifacts" else choice)

    if choice != "All artifacts":
        tc = next(t for t in bundle["test_cases"] if t["id"] == choice)
        st.markdown(
            f'<div class="note" style="margin-top:14px"><b>{escape(tc["id"])}</b> '
            f'— {escape(tc["title"])} — exists to prove '
            f'<b>{escape(tc["parent_ac_id"])}</b>, which comes from story '
            f'<b>{escape(tc["parent_us_id"])}</b> under epic '
            f'<b>{escape(tc["parent_ep_id"])}</b>, delivering '
            f'<b>{escape(tc["parent_br_id"])}</b>.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p style="font-size:19px;font-weight:700;margin:32px 0 6px;'
        'letter-spacing:-.01em">Traceability matrix</p>'
        '<p style="font-size:14px;color:var(--muted);margin:0 0 14px">'
        "One row per test case, resolved up to the requirement.</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        pd.DataFrame(build_traceability_rows(bundle)),
        width="stretch",
        hide_index=True,
    )
