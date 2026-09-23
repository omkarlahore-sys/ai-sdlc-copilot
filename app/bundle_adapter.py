"""Adapter: convert app.pipeline.run_pipeline() output into the bundle
shape ui/ (originally built against ui/mock_data.py) expects."""

from __future__ import annotations

import re
from typing import Any


def _split_user_story(story_text: str) -> tuple[str, str, str]:
    """Split 'As a X, I want Y, so that Z.' into (as_a, i_want, so_that)."""
    match = re.search(
        r"as a\s+(.*?),\s*i want\s+(.*?),\s*so that\s+(.*?)\.?\s*$",
        story_text.strip(),
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip(),
        )
    return ("user", story_text.strip(), "the requirement is satisfied")


def build_bundle_from_pipeline(result: dict[str, Any]) -> dict[str, Any]:
    """Turn a run_pipeline() result into the bundle shape ui/ expects."""
    br = result["business_requirement"]

    epics = [
        {
            "id": epic["id"],
            "parent_br_id": epic["source_requirement_id"],
            "title": epic["title"],
            "description": epic["description"],
        }
        for epic in result["epics"]
    ]

    user_stories = []
    for story in result["user_stories"]:
        as_a, i_want, so_that = _split_user_story(story["story"])
        user_stories.append(
            {
                "id": story["id"],
                "parent_ep_id": story["parent_epic_id"],
                "parent_br_id": story["source_requirement_id"],
                "title": story["title"],
                "as_a": as_a,
                "i_want": i_want,
                "so_that": so_that,
                #"priority": "Medium",  # pipeline doesn't assign one yet
            }
        )

    acceptance_criteria = [
        {
            "id": ac["id"],
            "parent_us_id": ac["parent_story_id"],
            "parent_ep_id": ac["parent_epic_id"],
            "parent_br_id": ac["source_requirement_id"],
            "given": ac["given"],
            "when": ac["when"],
            "then": ac["then"],
        }
        for ac in result["acceptance_criteria"]
    ]

    test_cases = []
    for tc in result["test_cases"]:
        numbered_steps = "\n".join(
            f"{i}. {step}" for i, step in enumerate(tc["steps"], start=1)
        )
        test_cases.append(
            {
                "id": tc["id"],
                "parent_ac_id": tc["parent_acceptance_criteria_id"],
                "parent_us_id": tc["parent_story_id"],
                "parent_ep_id": tc["parent_epic_id"],
                "parent_br_id": tc["source_requirement_id"],
                "title": tc["title"],
                "preconditions": tc["precondition"],
                "steps": numbered_steps,
                "expected_result": tc["expected_result"],
            }
        )

    return {
        "business_requirement": {"id": br["id"], "text": br["text"], "is_sample": False},
        "epics": epics,
        "user_stories": user_stories,
        "acceptance_criteria": acceptance_criteria,
        "test_cases": test_cases,
    }
