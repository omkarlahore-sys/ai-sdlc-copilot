"""Export: a single CSV of every artifact with its IDs and parent references."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from ui.export_csv import artifacts_to_csv

Bundle = dict[str, Any]


def render(bundle: Bundle) -> None:
    csv_text = artifacts_to_csv(bundle)
    rows = len(csv_text.strip().splitlines()) - 1  # minus the header

    st.markdown(
        '<p class="sec">Export artifacts</p>'
        '<p class="sec-s">One row per artifact, carrying its ID and every parent '
        "reference, so the chain survives outside this application.</p>",
        unsafe_allow_html=True,
    )

    button, meta = st.columns([1, 3.6], gap="medium")
    with button:
        st.download_button(
            "Export CSV",
            data=csv_text,
            file_name="sdlc_artifacts_sample.csv",
            mime="text/csv",
            type="primary",
            width="stretch",
            key="export_csv",
        )
    with meta:
        st.markdown(
            f"<div style='font-size:.8rem;color:var(--text-2);padding-top:.45rem'>"
            f"{rows} rows · 8 columns · sdlc_artifacts_sample.csv</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="sec" style="margin-top:1.3rem">File contents</p>'
        '<p class="sec-s">Exactly what the download contains.</p>',
        unsafe_allow_html=True,
    )

    import io

    st.dataframe(
        pd.read_csv(io.StringIO(csv_text)).fillna(""),
        width="stretch",
        hide_index=True,
        height=420,
    )
