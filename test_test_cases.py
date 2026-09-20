from app.services.test_case_service import (
    generate_and_validate_test_cases
)


business_requirement = """
Customers should be able to reset their password
using their registered email address.
"""


approved_epic = {
    "id": "EPIC-001",
    "title": "Password reset via registered email",
    "description": (
        "Allow customers to reset their password "
        "by submitting their registered email address"
    )
}


approved_user_story = {
    "id": "US-001",
    "title": "Password reset via registered email",
    "story": (
        "As a customer, I want to reset my password "
        "using my registered email address, "
        "so that I can regain access to my account."
    )
}


approved_ac = {
    "id": "AC-001",
    "given": (
        "The customer has a registered email address "
        "associated with their account"
    ),
    "when": (
        "the customer submits a password reset request "
        "using that registered email address"
    ),
    "then": (
        "the system enables the customer to reset "
        "their password"
    )
}


test_cases = generate_and_validate_test_cases(
    business_requirement,
    approved_epic,
    approved_user_story,
    approved_ac,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    user_story_id="US-001",
    acceptance_criteria_id="AC-001",
    number_of_test_cases=3,
    max_attempts=3
)


print("\n===== FINAL TEST CASES =====")

for tc in test_cases:

    print("\nID:", tc["id"])
    print("Title:", tc["title"])
    print("Precondition:", tc["precondition"])

    print("Steps:")

    for number, step in enumerate(
        tc["steps"],
        start=1
    ):
        print(f"{number}. {step}")

    print(
        "Expected Result:",
        tc["expected_result"]
    )

    print(
        "Parent AC:",
        tc["parent_acceptance_criteria_id"]
    )

    print(
        "Parent Story:",
        tc["parent_story_id"]
    )

    print(
        "Parent Epic:",
        tc["parent_epic_id"]
    )

    print(
        "Source Requirement:",
        tc["source_requirement_id"]
    )