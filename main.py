from app.services.user_story_service import (
    generate_and_validate_user_stories
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


stories = generate_and_validate_user_stories(
    business_requirement,
    approved_epic,
    business_requirement_id="BR-001",
    epic_id="EPIC-001"
)


print("\n===== FINAL USER STORIES =====")

for story in stories:

    print("\nID:", story["id"])
    print("Title:", story["title"])
    print("Story:", story["story"])
    print("Parent Epic:", story["parent_epic_id"])
    print(
        "Source Requirement:",
        story["source_requirement_id"]
    )