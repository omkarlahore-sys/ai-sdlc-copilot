from app.services.acceptance_criteria_service import (
    generate_and_validate_acceptance_criteria
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


acceptance_criteria = (
    generate_and_validate_acceptance_criteria(
        business_requirement,
        approved_epic,
        approved_user_story,
        business_requirement_id="BR-001",
        epic_id="EPIC-001",
        user_story_id="US-001",
        number_of_criteria=3,
        max_attempts=3
    )
)


print("\n===== FINAL ACCEPTANCE CRITERIA =====")

for ac in acceptance_criteria:

    print("\nID:", ac["id"])

    print("Given:", ac["given"])

    print("When:", ac["when"])

    print("Then:", ac["then"])

    print(
        "Parent Story:",
        ac["parent_story_id"]
    )

    print(
        "Parent Epic:",
        ac["parent_epic_id"]
    )

    print(
        "Source Requirement:",
        ac["source_requirement_id"]
    )