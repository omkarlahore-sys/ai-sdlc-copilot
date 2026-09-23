"""CSV export helpers for sample/generated artifact bundles."""

from __future__ import annotations

import csv
import io
from typing import Any


def artifacts_to_csv(bundle: dict[str, Any]) -> str:
    """Serialize a full artifact bundle into a single CSV string.

    Each row is one artifact (or the BR) with type, id, parent refs,
    and a concise text payload suitable for spreadsheet review.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "artifact_type",
            "id",
            "parent_br_id",
            "parent_ep_id",
            "parent_us_id",
            "parent_ac_id",
            "title",
            "content",
        ],
    )
    writer.writeheader()

    br = bundle["business_requirement"]
    writer.writerow(
        {
            "artifact_type": "Business Requirement",
            "id": br["id"],
            "parent_br_id": "",
            "parent_ep_id": "",
            "parent_us_id": "",
            "parent_ac_id": "",
            "title": "Business Requirement",
            "content": br["text"],
        }
    )

    for ep in bundle["epics"]:
        writer.writerow(
            {
                "artifact_type": "Epic",
                "id": ep["id"],
                "parent_br_id": ep.get("parent_br_id", ""),
                "parent_ep_id": "",
                "parent_us_id": "",
                "parent_ac_id": "",
                "title": ep["title"],
                "content": ep["description"],
            }
        )

    for us in bundle["user_stories"]:
        content = (
            f"As a {us['as_a']}, I want {us['i_want']}, "
            f"so that {us['so_that']}."
        )
        writer.writerow(
            {
                "artifact_type": "User Story",
                "id": us["id"],
                "parent_br_id": us.get("parent_br_id", ""),
                "parent_ep_id": us.get("parent_ep_id", ""),
                "parent_us_id": "",
                "parent_ac_id": "",
                "title": us["title"],
                "content": content,
            }
        )

    for ac in bundle["acceptance_criteria"]:
        content = (
            f"Given {ac['given']}; When {ac['when']}; Then {ac['then']}"
        )
        writer.writerow(
            {
                "artifact_type": "Acceptance Criteria",
                "id": ac["id"],
                "parent_br_id": ac.get("parent_br_id", ""),
                "parent_ep_id": ac.get("parent_ep_id", ""),
                "parent_us_id": ac.get("parent_us_id", ""),
                "parent_ac_id": "",
                "title": ac["id"],
                "content": content,
            }
        )

    for tc in bundle["test_cases"]:
        content = (
            f"Preconditions: {tc['preconditions']} | "
            f"Steps: {tc['steps'].replace(chr(10), ' ')} | "
            f"Expected: {tc['expected_result']}"
        )
        writer.writerow(
            {
                "artifact_type": "Test Case",
                "id": tc["id"],
                "parent_br_id": tc.get("parent_br_id", ""),
                "parent_ep_id": tc.get("parent_ep_id", ""),
                "parent_us_id": tc.get("parent_us_id", ""),
                "parent_ac_id": tc.get("parent_ac_id", ""),
                "title": tc["title"],
                "content": content,
            }
        )

    return buffer.getvalue()
