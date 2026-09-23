"""AI-Powered SDLC Copilot.

Enter one business requirement; review the generated Epic -> User Story ->
Acceptance Criteria -> Test Case chain; trace it end to end; export it as CSV.

Prototype build: artifacts come from the bundled sample data in
``ui.mock_data``.
"""

from __future__ import annotations

import streamlit as st

from ui import theme
from ui.mock_data import get_sample_bundle
from ui.shell import render_header, render_nav
from ui.views import artifacts as artifacts_view
from ui.views import export as export_view
from ui.views import generating as generating_view
from ui.views import new_requirement as new_requirement_view
from ui.views import traceability as traceability_view
from app.pipeline import run_pipeline
from app.bundle_adapter import build_bundle_from_pipeline

PAGES = {
    "New Requirement": (
        "New Requirement",
        "Turn one business requirement into a complete, reviewable and "
        "traceable SDLC artifact chain.",
    ),
    "Artifacts": (
        "Artifacts",
        "Review the generated epics, stories, acceptance criteria and test cases.",
    ),
    "Traceability": (
        "Traceability",
        "Follow every test case back to the requirement it came from.",
    ),
    "Export": (
        "Export",
        "Download all artifacts with their IDs and parent references.",
    ),
}


def _init_state() -> None:
    defaults = {
        "page": "New Requirement",
        "bundle": None,
        "requirement_text": "",
        "error": None,
        "pending": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _generate(requirement: str) -> None:
    """Validate, then hand off to the generating screen on the next run."""
    if not requirement:
        st.session_state.error = (
            "Enter a business requirement before generating artifacts."
        )
        return
    st.session_state.error = None
    # Deferred to the next run so the sequence owns the whole screen instead of
    # rendering underneath the form it was launched from.
    st.session_state.pending = requirement
    st.rerun()


def _run_generation() -> None:
    """Run the real pipeline, store the result, and land on the artifacts."""
    requirement = st.session_state.pending
    with st.spinner("Calling the pipeline — this can take 30–90 seconds..."):
        try:
            result = run_pipeline(requirement, business_requirement_id="BR-001")
        except Exception as exc:
            st.session_state.error = f"Generation failed: {exc}"
            st.session_state.pending = None
            st.session_state.page = "New Requirement"
            st.rerun()
            return
    bundle = build_bundle_from_pipeline(result)
    generating_view.run(bundle, requirement)
    st.session_state.bundle = bundle
    st.session_state.requirement_text = requirement
    st.session_state.pending = None
    st.session_state.page = "Artifacts"
    st.rerun()



def main() -> None:
    st.set_page_config(
        page_title="SDLC Copilot",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    theme.inject()
    _init_state()

    bundle = st.session_state.bundle

    # A pending requirement takes over the screen for the generation sequence.
    # The floating nav still renders underneath so it's there the instant the
    # overlay clears.
    if st.session_state.pending:
        render_nav(st.session_state.page, bundle is not None)
        _run_generation()
        return

    chosen = render_nav(st.session_state.page, bundle is not None)
    if chosen != st.session_state.page:
        st.session_state.page = chosen
        st.rerun()

    page = st.session_state.page

    if page == "New Requirement":
        requirement, clicked = new_requirement_view.render(st.session_state.error)
        if clicked:
            _generate(requirement)
    elif page == "Artifacts":
        title, subtitle = PAGES[page]
        render_header(title, subtitle)
        artifacts_view.render(bundle, st.session_state.requirement_text)
    elif page == "Traceability":
        title, subtitle = PAGES[page]
        render_header(title, subtitle)
        traceability_view.render(bundle)
    elif page == "Export":
        title, subtitle = PAGES[page]
        render_header(title, subtitle)
        export_view.render(bundle)


if __name__ == "__main__":
    main()
