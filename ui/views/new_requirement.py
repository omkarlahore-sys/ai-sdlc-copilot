"""Entry screen: enter a business requirement, or upload a PDF/TXT file."""

from __future__ import annotations

import io

import streamlit as st

from ui.shell import render_header

HERO_TITLE = "New business requirement"
HERO_SUB = (
    "Type it in, or upload a PDF or text file. You'll get epics, user "
    "stories, acceptance criteria and test cases, fully traceable back to "
    "what you entered."
)


def _extract_pdf_text(uploaded) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(uploaded.getvalue()))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())


def _extract_txt_text(uploaded) -> str:
    return uploaded.getvalue().decode("utf-8", errors="ignore")


def render(error: str | None) -> tuple[str, bool]:
    """Return (requirement_text, generate_clicked)."""
    st.session_state.setdefault("requirement_input", "")

    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        render_header(HERO_TITLE, HERO_SUB)

        with st.container(key="req_card"):
            st.markdown(
                '<div class="field-label">Input type</div>',
                unsafe_allow_html=True,
            )
            input_type = st.radio(
                "Input type",
                ["Text", "PDF", "TXT"],
                key="input_type",
                horizontal=True,
                label_visibility="collapsed",
            )

            st.markdown(
                '<div class="field-label">Business requirement</div>',
                unsafe_allow_html=True,
            )

            with st.container(key="actions_row"):
                clicked = st.button(
                    "Generate Artifacts",
                    type="primary",
                    width="stretch",
                    key="generate_btn",
                )

            text = ""
            if input_type == "Text":
                text = st.text_area(
                    "Business requirement",
                    max_chars=2000,
                    key="requirement_input",
                    label_visibility="collapsed",
                    placeholder=(
                        "Example: Users should be able to reset their password "
                        "using their registered email address."
                    ),
                )
                st.markdown(
                    f"<div class='hint'>{len(text or '')}/2000 characters</div>",
                    unsafe_allow_html=True,
                )
            else:
                uploaded = st.file_uploader(
                    f"Upload a {input_type} file",
                    type=["pdf"] if input_type == "PDF" else ["txt"],
                    key=f"upload_{input_type.lower()}",
                    label_visibility="collapsed",
                )
                if uploaded is not None:
                    try:
                        text = (
                            _extract_pdf_text(uploaded)
                            if input_type == "PDF"
                            else _extract_txt_text(uploaded)
                        )
                    except Exception as exc:
                        st.markdown(
                            '<div class="note err" style="margin-top:10px">'
                            f"Couldn't read that file: {exc}</div>",
                            unsafe_allow_html=True,
                        )
                        text = ""
                    else:
                        if text:
                            st.markdown(
                                '<div class="note" style="margin-top:10px">'
                                f"Read {len(text)} characters from "
                                f"{uploaded.name}.</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                '<div class="note err" style="margin-top:10px">'
                                "Couldn't find any text in that file.</div>",
                                unsafe_allow_html=True,
                            )

            if error:
                st.markdown(
                    '<div class="note err" style="margin-top:10px">'
                    "<b>Requirement needed.</b> Type a requirement or upload "
                    "a file.</div>",
                    unsafe_allow_html=True,
                )

    return (text or "").strip(), clicked