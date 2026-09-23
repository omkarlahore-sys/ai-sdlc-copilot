"""Sample/mock SDLC artifacts for UI demonstration only."""

from __future__ import annotations

from typing import Any

SAMPLE_BUSINESS_REQUIREMENT = (
    "User should be able to reset their password using their "
    "registered email address."
)

SAMPLE_BR_ID = "BR-001"

SAMPLE_EPICS: list[dict[str, Any]] = [
    {
        "id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Password Reset Capability",
        "description": (
            "Enable registered users to securely initiate and complete a "
            "password reset via their verified email address."
        ),
    },
    {
        "id": "EP-002",
        "parent_br_id": "BR-001",
        "title": "Reset Security & Abuse Prevention",
        "description": (
            "Protect the password reset flow against account enumeration "
            "and misuse while preserving a clear recovery experience."
        ),
    },
]

SAMPLE_USER_STORIES: list[dict[str, Any]] = [
    {
        "id": "US-001",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Request password reset link",
        "as_a": "registered user",
        "i_want": "to request a password reset link using my registered email",
        "so_that": "I can regain access to my account when I forget my password",
        "priority": "High",
    },
    {
        "id": "US-002",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Set a new password via reset link",
        "as_a": "registered user",
        "i_want": "to set a new password after opening a valid reset link",
        "so_that": "I can securely update my credentials and sign in again",
        "priority": "High",
    },
    {
        "id": "US-003",
        "parent_ep_id": "EP-002",
        "parent_br_id": "BR-001",
        "title": "Avoid revealing account existence",
        "as_a": "security-conscious product owner",
        "i_want": "reset responses to remain generic for unknown emails",
        "so_that": "attackers cannot enumerate registered accounts",
        "priority": "Medium",
    },
]

SAMPLE_ACCEPTANCE_CRITERIA: list[dict[str, Any]] = [
    {
        "id": "AC-001",
        "parent_us_id": "US-001",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "given": "the user has a registered email address",
        "when": "the user submits a password reset request with that email",
        "then": (
            "the system sends a password reset link to the registered "
            "email address"
        ),
    },
    {
        "id": "AC-002",
        "parent_us_id": "US-003",
        "parent_ep_id": "EP-002",
        "parent_br_id": "BR-001",
        "given": "the submitted email is not registered in the system",
        "when": "the user submits a password reset request",
        "then": (
            "the system shows a generic confirmation message without "
            "revealing whether the email exists"
        ),
    },
    {
        "id": "AC-003",
        "parent_us_id": "US-002",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "given": "the user opened a valid, unexpired password reset link",
        "when": "the user submits a new password that meets policy rules",
        "then": (
            "the system updates the password and confirms the change "
            "was successful"
        ),
    },
    {
        "id": "AC-004",
        "parent_us_id": "US-002",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "given": "the password reset link is expired or invalid",
        "when": "the user attempts to open the link",
        "then": (
            "the system blocks the reset and prompts the user to "
            "request a new link"
        ),
    },
    {
        "id": "AC-005",
        "parent_us_id": "US-001",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "given": "the user has already requested a reset within the rate limit window",
        "when": "the user submits another reset request",
        "then": (
            "the system applies rate limiting and still returns a "
            "generic confirmation message"
        ),
    },
]

SAMPLE_TEST_CASES: list[dict[str, Any]] = [
    {
        "id": "TC-001",
        "parent_ac_id": "AC-001",
        "parent_us_id": "US-001",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Valid email receives reset link",
        "preconditions": "User account exists with a verified email.",
        "steps": (
            "1. Open the password reset page.\n"
            "2. Enter the registered email.\n"
            "3. Submit the request."
        ),
        "expected_result": (
            "A password reset email with a valid link is delivered "
            "to the registered address."
        ),
    },
    {
        "id": "TC-002",
        "parent_ac_id": "AC-002",
        "parent_us_id": "US-003",
        "parent_ep_id": "EP-002",
        "parent_br_id": "BR-001",
        "title": "Unregistered email shows generic response",
        "preconditions": "Email address is not associated with any account.",
        "steps": (
            "1. Open the password reset page.\n"
            "2. Enter an unregistered email.\n"
            "3. Submit the request."
        ),
        "expected_result": (
            "UI shows a generic confirmation; no account existence "
            "is disclosed."
        ),
    },
    {
        "id": "TC-003",
        "parent_ac_id": "AC-003",
        "parent_us_id": "US-002",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Valid link allows password update",
        "preconditions": "A valid, unexpired reset link was issued.",
        "steps": (
            "1. Open the reset link.\n"
            "2. Enter a policy-compliant new password.\n"
            "3. Confirm and submit."
        ),
        "expected_result": (
            "Password is updated and a success confirmation is shown."
        ),
    },
    {
        "id": "TC-004",
        "parent_ac_id": "AC-004",
        "parent_us_id": "US-002",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Expired link blocks reset",
        "preconditions": "Reset link has expired or is otherwise invalid.",
        "steps": (
            "1. Open the expired/invalid reset link.\n"
            "2. Observe the response."
        ),
        "expected_result": (
            "Reset is blocked and the user is prompted to request a new link."
        ),
    },
    {
        "id": "TC-005",
        "parent_ac_id": "AC-005",
        "parent_us_id": "US-001",
        "parent_ep_id": "EP-001",
        "parent_br_id": "BR-001",
        "title": "Repeated requests are rate limited",
        "preconditions": "User already submitted a reset within the limit window.",
        "steps": (
            "1. Submit a password reset request.\n"
            "2. Immediately submit another request with the same email."
        ),
        "expected_result": (
            "Rate limiting is applied and the UI still shows a generic "
            "confirmation message."
        ),
    },
]


def get_sample_bundle() -> dict[str, Any]:
    """Return the full sample artifact bundle for UI and export demos."""
    return {
        "business_requirement": {
            "id": SAMPLE_BR_ID,
            "text": SAMPLE_BUSINESS_REQUIREMENT,
            "is_sample": True,
        },
        "epics": SAMPLE_EPICS,
        "user_stories": SAMPLE_USER_STORIES,
        "acceptance_criteria": SAMPLE_ACCEPTANCE_CRITERIA,
        "test_cases": SAMPLE_TEST_CASES,
    }


def build_traceability_rows(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Flatten sample artifacts into BR → EP → US → AC → TC rows."""
    br_id = bundle["business_requirement"]["id"]

    rows: list[dict[str, str]] = []
    for tc in bundle["test_cases"]:
        rows.append(
            {
                "BR": br_id,
                "EP": tc.get("parent_ep_id", ""),
                "US": tc.get("parent_us_id", ""),
                "AC": tc.get("parent_ac_id", ""),
                "TC": tc["id"],
                "Scenario": tc["title"],
            }
        )
    return rows


def stories_of(bundle: dict[str, Any], epic_id: str) -> list[dict[str, Any]]:
    return [s for s in bundle["user_stories"] if s.get("parent_ep_id") == epic_id]


def criteria_of(bundle: dict[str, Any], story_id: str) -> list[dict[str, Any]]:
    return [a for a in bundle["acceptance_criteria"] if a.get("parent_us_id") == story_id]


def tests_of(bundle: dict[str, Any], ac_id: str) -> list[dict[str, Any]]:
    return [t for t in bundle["test_cases"] if t.get("parent_ac_id") == ac_id]


def build_example_trace_chain(bundle: dict[str, Any]) -> list[dict[str, str]]:
    """Return a representative BR→EP→US→AC→TC chain for visual display."""
    tc = bundle["test_cases"][0]
    return [
        {"label": "Business Requirement", "id": bundle["business_requirement"]["id"]},
        {"label": "Epic", "id": tc.get("parent_ep_id", "")},
        {"label": "User Story", "id": tc.get("parent_us_id", "")},
        {"label": "Acceptance Criteria", "id": tc.get("parent_ac_id", "")},
        {"label": "Test Case", "id": tc["id"]},
    ]
