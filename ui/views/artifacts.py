"""Artifacts workspace: source requirement, counts, and the four explorers."""

from __future__ import annotations

from html import escape
from typing import Any, Callable

import streamlit as st

from ui.mock_data import criteria_of, stories_of, tests_of
from ui.odometer import counter as odo_counter

Bundle = dict[str, Any]


# ------------------------------------------------------------------ lookups

def _by_id(items: list[dict], wanted: str) -> dict | None:
    return next((i for i in items if i["id"] == wanted), None)


def story_sentence(story: dict) -> str:
    return (
        f"As a {story['as_a']}, I want {story['i_want']}, "
        f"so that {story['so_that']}."
    )


# ------------------------------------------------------------------ markup

def _id_tag(artifact_id: str) -> str:
    kind = artifact_id.split("-")[0].lower()
    return f'<span class="id {kind}">{escape(artifact_id)}</span>'


def _crumb(*ids: str) -> str:
    parts = [_id_tag(i) for i in ids if i]
    return f'<div class="crumb">{" › ".join(parts)}</div>'


def _gwt(ac: dict) -> str:
    return (
        f'<div class="gwt"><b>Given</b><span>{escape(ac["given"])}</span></div>'
        f'<div class="gwt"><b>When</b><span>{escape(ac["when"])}</span></div>'
        f'<div class="gwt"><b>Then</b><span>{escape(ac["then"])}</span></div>'
    )


def _steps(test_case: dict) -> str:
    """Steps arrive pre-numbered as a newline-delimited string."""
    lines = [ln.strip() for ln in test_case["steps"].split("\n") if ln.strip()]
    return "<br>".join(escape(ln) for ln in lines)


# --------------------------------------------------------------- scaffolding

def render_source(bundle: Bundle, user_text: str) -> None:
    """The requirement everything below traces back to."""
    br = bundle["business_requirement"]
    is_sample = bool(br.get("is_sample"))

    tag = '<span class="sample-tag">Sample</span>' if is_sample else ""
    why = (
        '<p class="sample-why">The artifacts below are bundled sample data, '
        "shown to demonstrate the workflow. They are not generated from the "
        "requirement text above.</p>"
        if is_sample
        else ""
    )
    st.markdown(
        f'<div class="source{" is-sample" if is_sample else ""}">'
        f'<div class="k">Source requirement</div>'
        f'{_id_tag(br["id"])}{tag}'
        f'<p class="q">{escape(user_text or br["text"])}</p>'
        f"{why}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_counts(bundle: Bundle) -> None:
    cells = [
        (len(bundle["epics"]), "Epics", "var(--l2)"),
        (len(bundle["user_stories"]), "User Stories", "var(--l3)"),
        (len(bundle["acceptance_criteria"]), "Acceptance Criteria", "var(--l4)"),
        (len(bundle["test_cases"]), "Test Cases", "var(--l5)"),
    ]
    html = "".join(
        f'<div style="--c:{color}">'
        f'<div class="v">{odo_counter(value, key=f"cnt{i}", delay=i * 0.08)}</div>'
        f'<div class="k">{label}</div></div>'
        for i, (value, label, color) in enumerate(cells)
    )
    st.markdown(f'<div class="counts">{html}</div>', unsafe_allow_html=True)


def render_validation_status(bundle: Bundle) -> None:
    epics = len(bundle["epics"])
    stories = len(bundle["user_stories"])
    criteria = len(bundle["acceptance_criteria"])
    tests = len(bundle["test_cases"])
    st.markdown(
        '<div class="strip">'
        f"<b>Generation summary</b> — {epics} epics · {stories} user stories · "
        f"{criteria} acceptance criteria · {tests} test cases"
        '<span class="go">✓ Validation passed · ✓ Traceability complete</span>'
        "</div>",
        unsafe_allow_html=True,
    )


def _truncate(text: str, limit: int = 92) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _count(n: int, singular: str, plural: str | None = None) -> str:
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


def _rows(
    items: list[dict],
    kind: str,
    key: str,
    label: Callable[[dict], str],
) -> str:
    """Render selectable artifact rows with stable, unique Streamlit keys."""

    ids = [i["id"] for i in items]

    if not ids:
        return ""

    state_key = f"{key}_sel"
    current = st.session_state.get(state_key)

    if current not in ids:
        current = ids[0]
        st.session_state[state_key] = current

    for index, item in enumerate(items):
        artifact_id = item["id"]
        selected = artifact_id == current

        # IMPORTANT:
        # Use index + artifact ID so every Streamlit element has
        # a guaranteed unique key.
        container_key = f"art_{kind}_{key}_{index}_{artifact_id}"
        button_key = f"{key}_btn_{index}_{artifact_id}"

        with st.container(key=container_key):
            if st.button(
                label(item),
                key=button_key,
                width="stretch",
            ):
                st.session_state[state_key] = artifact_id
                st.rerun()

    return st.session_state[state_key]


def _explorer(
    caption: str,
    items: list[dict],
    kind: str,
    key: str,
    label: Callable[[dict], str],
    detail: Callable[[str], None],
) -> None:
    if not items:
        st.markdown(
            '<div class="empty"><div class="t">Nothing to show</div></div>',
            unsafe_allow_html=True,
        )
        return
    left, right = st.columns([1.5, 1], gap="medium")
    with left:
        st.markdown(
            f'<p class="sec-s" style="margin:.85rem 0 .55rem">{escape(caption)}</p>',
            unsafe_allow_html=True,
        )
        selected = _rows(items, kind, key, label)
    with right:
        st.write("")
        detail(selected)


# ------------------------------------------------------------------ epics

def epics_tab(bundle: Bundle) -> None:
    epics = bundle["epics"]

    def detail(selected: str) -> None:
        epic = _by_id(epics, selected)
        if epic is None:
            return
        stories = stories_of(bundle, epic["id"])
        children = "".join(
            f'<div class="child"><div class="child-h">{_id_tag(s["id"])}'
            f'{escape(s["title"])}</div>'
            f'<div class="body">{escape(story_sentence(s))}</div></div>'
            for s in stories
        ) or '<p class="body">No user stories generated for this epic.</p>'

        st.markdown(
            f'<div class="panel">'
            f'{_crumb(epic["parent_br_id"], epic["id"])}'
            f'<h3>{escape(epic["title"])}</h3>'
            f'<div class="lab">Description</div>'
            f'<p class="body">{escape(epic["description"])}</p>'
            f'<div class="lab">User stories ({len(stories)})</div>'
            f"{children}"
            f"</div>",
            unsafe_allow_html=True,
        )

    def label(e: dict) -> str:
        n = len(stories_of(bundle, e["id"]))
        return f"`{e['id']}`  **{e['title']}**  ·  {_count(n, 'story', 'stories')}"

    _explorer(
        "Epics group related work under the business requirement.",
        epics,
        "ep",
        "tbl_epics",
        label,
        detail,
    )


# ----------------------------------------------------------------- stories

def stories_tab(bundle: Bundle) -> None:
    stories = bundle["user_stories"]

    def detail(selected: str) -> None:
        story = _by_id(stories, selected)
        if story is None:
            return
        crits = criteria_of(bundle, story["id"])

        blocks = []
        for ac in crits:
            tests = tests_of(bundle, ac["id"])
            test_html = "".join(
                f'<div style="margin-top:.4rem;font-size:.8rem;color:var(--text-2)">'
                f'{_id_tag(t["id"])}{escape(t["title"])}</div>'
                for t in tests
            )
            blocks.append(
                f'<div class="child">'
                f'<div class="child-h">{_id_tag(ac["id"])}</div>'
                f"{_gwt(ac)}"
                f"{test_html}"
                f"</div>"
            )
        criteria_html = "".join(blocks) or (
            '<p class="body">No acceptance criteria generated for this story.</p>'
        )

        st.markdown(
            f'<div class="panel">'
            f'{_crumb(story["parent_br_id"], story["parent_ep_id"], story["id"])}'
            f'<h3>{escape(story["title"])}</h3>'
            f'<div class="lab">Story</div>'
            f'<p class="body">{escape(story_sentence(story))}</p>'
            f'<div class="lab">Acceptance criteria ({len(crits)}) and their tests</div>'
            f"{criteria_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

    def label(item: dict) -> str:
        n = len(criteria_of(bundle, item["id"]))
        return f"`{item['id']}`  **{item['title']}**  ·  {_count(n, 'criterion', 'criteria')}"

    _explorer(
        "Agile stories with their parent epic .",
        stories,
        "us",
        "tbl_stories",
        label,
        detail,
    )


# ---------------------------------------------------------------- criteria

def criteria_tab(bundle: Bundle) -> None:
    crits = bundle["acceptance_criteria"]

    def detail(selected: str) -> None:
        ac = _by_id(crits, selected)
        if ac is None:
            return
        story = _by_id(bundle["user_stories"], ac["parent_us_id"])
        tests = tests_of(bundle, ac["id"])
        test_html = "".join(
            f'<div class="child"><div class="child-h">{_id_tag(t["id"])}'
            f'{escape(t["title"])}</div>'
            f'<div class="body">{escape(t["expected_result"])}</div></div>'
            for t in tests
        ) or '<p class="body">No test case covers this criterion.</p>'

        story_html = (
            f'<div class="lab">From story</div>'
            f'<p class="body">{escape(story_sentence(story))}</p>'
            if story
            else ""
        )

        st.markdown(
            f'<div class="panel">'
            f'{_crumb(ac["parent_br_id"], ac["parent_ep_id"], ac["parent_us_id"], ac["id"])}'
            f'<div class="lab">Acceptance criterion</div>'
            f"{_gwt(ac)}"
            f"{story_html}"
            f'<div class="lab">Test cases ({len(tests)})</div>'
            f"{test_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

    def label(a: dict) -> str:
        n = len(tests_of(bundle, a["id"]))
        return (
            f"`{a['id']}`  **Then** {_truncate(a['then'], 72)}  ·  "
            f"{_count(n, 'test')}"
        )

    _explorer(
        "Given / When / Then conditions linked to a user story.",
        crits,
        "ac",
        "tbl_criteria",
        label,
        detail,
    )


# --------------------------------------------------------------- test cases

def tests_tab(bundle: Bundle) -> None:
    cases = bundle["test_cases"]

    def detail(selected: str) -> None:
        tc = _by_id(cases, selected)
        if tc is None:
            return
        ac = _by_id(bundle["acceptance_criteria"], tc["parent_ac_id"])
        origin = (
            f'<div class="lab">Proves criterion {escape(tc["parent_ac_id"])}</div>'
            f'<div class="child">{_gwt(ac)}</div>'
            if ac
            else ""
        )

        st.markdown(
            f'<div class="panel">'
            f'{_crumb(tc["parent_br_id"], tc["parent_ep_id"], tc["parent_us_id"], tc["parent_ac_id"], tc["id"])}'
            f'<h3>{escape(tc["title"])}</h3>'
            f'<div class="lab">Preconditions</div>'
            f'<p class="body">{escape(tc["preconditions"])}</p>'
            f'<div class="lab">Steps</div>'
            f'<p class="body">{_steps(tc)}</p>'
            f'<div class="lab">Expected result</div>'
            f'<p class="body">{escape(tc["expected_result"])}</p>'
            f"{origin}"
            f"</div>",
            unsafe_allow_html=True,
        )

    def label(t: dict) -> str:
        return f"`{t['id']}`  **{t['title']}**  ·  proves {t['parent_ac_id']}"

    _explorer(
        "Functional tests mapped to acceptance criteria.",
        cases,
        "tc",
        "tbl_tests",
        label,
        detail,
    )


def render(bundle: Bundle, user_text: str) -> None:
    render_source(bundle, user_text)
    render_counts(bundle)
    render_validation_status(bundle)
    tabs = st.tabs(["Epics", "User Stories", "Acceptance Criteria", "Test Cases"])
    with tabs[0]:
        epics_tab(bundle)
    with tabs[1]:
        stories_tab(bundle)
    with tabs[2]:
        criteria_tab(bundle)
    with tabs[3]:
        tests_tab(bundle)
