"""The generation sequence.

Rather than jumping straight to the results, the chain is shown assembling one
level at a time, with each stage's real count arriving as it completes. It is
the clearest possible statement of what this product does: one requirement in,
five linked levels out.
"""

from __future__ import annotations

import time
from html import escape
from typing import Any

import streamlit as st

Bundle = dict[str, Any]

# (label, level token, bundle key or None, whether a count is shown when done)
STAGES = [
    ("Reading the requirement", "l1", None, False),
    ("Deriving epics", "l2", "epics", True),
    ("Writing user stories", "l3", "user_stories", True),
    ("Defining acceptance criteria", "l4", "acceptance_criteria", True),
    ("Building functional test cases", "l5", "test_cases", True),
    ("Running semantic validation", "l3", None, False),
    ("Building traceability graph", "l2", None, False),
]

STEP_SECONDS = 0.48


def _stage_html(index: int, state: str, count: int | None) -> str:
    """One row of the sequence. state is 'done', 'active' or 'waiting'."""
    label, level, _key, has_count = STAGES[index]
    if state == "done":
        mark = f'<span class="gen-mark done" style="background:var(--{level})">&#10003;</span>'
    elif state == "active":
        mark = f'<span class="gen-mark spin" style="border-top-color:var(--{level})"></span>'
    else:
        mark = '<span class="gen-mark idle"></span>'

    if state == "done" and has_count:
        tail = f'<span class="gen-count">{count}</span>'
    elif state == "active":
        tail = '<span class="gen-dots"><i></i><i></i><i></i></span>'
    else:
        tail = ""

    return (
        f'<div class="gen-row {state}">{mark}'
        f'<span class="gen-label">{escape(label)}</span>{tail}</div>'
    )


def run(bundle: Bundle, requirement: str) -> None:
    """Play the sequence. Blocks for roughly two seconds, then returns."""
    slot = st.empty()

    def frame(done_upto: int) -> str:
        rows = []
        for i, (_label, _level, key, _has_count) in enumerate(STAGES):
            if i < done_upto:
                count = len(bundle[key]) if key else None
                rows.append(_stage_html(i, "done", count))
            elif i == done_upto:
                rows.append(_stage_html(i, "active", None))
            else:
                rows.append(_stage_html(i, "waiting", None))
        pct = int(done_upto / len(STAGES) * 100)
        return (
            f'<div class="gen">'
            f'<div class="gen-head">'
            f'<div class="gen-eyebrow">Generating</div>'
            f'<p class="gen-req">{escape(requirement)}</p></div>'
            f'<div class="gen-bar"><i style="width:{pct}%"></i></div>'
            f'<div class="gen-rows">{"".join(rows)}</div>'
            f"</div>"
        )

    for step in range(len(STAGES) + 1):
        slot.markdown(frame(step), unsafe_allow_html=True)
        time.sleep(STEP_SECONDS)

    slot.empty()
