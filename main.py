# ============================================================
# AI SDLC COPILOT - END TO END PIPELINE TEST
# ============================================================

from app.services.user_story_service import (
    generate_and_validate_user_stories
)

from app.services.acceptance_criteria_service import (
    generate_and_validate_acceptance_criteria
)

from app.services.test_case_service import (
    generate_and_validate_test_cases
)


# ============================================================
# BUSINESS REQUIREMENT
# ============================================================

business_requirement = """
Customers should be able to reset their password
using their registered email address.
"""

business_requirement_id = "BR-001"


# ============================================================
# APPROVED EPIC
# ============================================================
# Temporary hard-coded Epic.
#
# This test focuses on:
#
# BR → Epic → User Story → AC → Test Case
#
# Epic generation can be tested separately.
# ============================================================

approved_epic = {

    "id": "EPIC-001",

    "title": (
        "Password reset via registered email"
    ),

    "description": (
        "Allow customers to reset their password "
        "by submitting their registered email address"
    )
}


# ============================================================
# STORAGE
# ============================================================

stories = []

all_acceptance_criteria = []

all_test_cases = []


# ============================================================
# STEP 1 — USER STORY GENERATION
# ============================================================

print("\n")
print("=" * 80)
print("                    USER STORY GENERATION")
print("=" * 80)


stories = generate_and_validate_user_stories(

    business_requirement,

    approved_epic,

    business_requirement_id=(
        business_requirement_id
    ),

    epic_id=(
        approved_epic["id"]
    )
)


if not stories:

    print(
        "\n❌ No User Stories approved."
    )

    print(
        "Pipeline stopped."
    )

    raise SystemExit(1)


print("\n")
print("=" * 80)
print("                    APPROVED USER STORIES")
print("=" * 80)


for story in stories:

    print("\nID:", story["id"])

    print(
        "Title:",
        story["title"]
    )

    print(
        "Story:",
        story["story"]
    )

    print(
        "Parent Epic:",
        story["parent_epic_id"]
    )

    print(
        "Source Requirement:",
        story["source_requirement_id"]
    )


# ============================================================
# STEP 2 — ACCEPTANCE CRITERIA GENERATION
# ============================================================

print("\n")
print("=" * 80)
print("                ACCEPTANCE CRITERIA GENERATION")
print("=" * 80)


for story in stories:

    print("\n")
    print("-" * 70)

    print(
        f"ACCEPTANCE CRITERIA FOR {story['id']}"
    )

    print("-" * 70)


    acs = generate_and_validate_acceptance_criteria(

        business_requirement,

        approved_epic,

        story,

        business_requirement_id=(
            business_requirement_id
        ),

        epic_id=(
            approved_epic["id"]
        ),

        user_story_id=(
            story["id"]
        )
    )


    if not acs:

        print(
            f"\n❌ No Acceptance Criterion "
            f"approved for {story['id']}."
        )

        continue


    print(
        "\n✅ APPROVED ACCEPTANCE CRITERIA"
    )


    for ac in acs:

        all_acceptance_criteria.append(ac)


        print("\nID:", ac["id"])

        print(
            "Given:",
            ac["given"]
        )

        print(
            "When:",
            ac["when"]
        )

        print(
            "Then:",
            ac["then"]
        )

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


if not all_acceptance_criteria:

    print(
        "\n❌ No Acceptance Criteria approved."
    )

    print(
        "Pipeline stopped."
    )

    raise SystemExit(1)


# ============================================================
# STEP 3 — TEST CASE GENERATION
# ============================================================

print("\n")
print("=" * 80)
print("                    TEST CASE GENERATION")
print("=" * 80)


for ac in all_acceptance_criteria:


    # --------------------------------------------------------
    # Find parent User Story
    # --------------------------------------------------------

    parent_story = None


    for story in stories:

        if (
            story["id"]
            == ac["parent_story_id"]
        ):

            parent_story = story

            break


    if parent_story is None:

        print(
            f"\n❌ Parent User Story "
            f"{ac['parent_story_id']} "
            f"not found for {ac['id']}."
        )

        continue


    # --------------------------------------------------------
    # Generate Test Cases
    # --------------------------------------------------------

    print("\n")
    print("-" * 70)

    print(
        f"TEST CASES FOR {ac['id']}"
    )

    print("-" * 70)


    test_cases = generate_and_validate_test_cases(

        business_requirement,

        approved_epic,

        parent_story,

        ac,

        business_requirement_id=(
            business_requirement_id
        ),

        epic_id=(
            approved_epic["id"]
        ),

        user_story_id=(
            parent_story["id"]
        ),

        acceptance_criteria_id=(
            ac["id"]
        )
    )


    if not test_cases:

        print(
            f"\n❌ No Test Case approved "
            f"for {ac['id']}."
        )

        continue


    print(
        "\n✅ APPROVED TEST CASES"
    )


    # --------------------------------------------------------
    # Store multiple Test Cases
    # --------------------------------------------------------

    for test_case in test_cases:

        all_test_cases.append(
            test_case
        )


        print(
            "\nID:",
            test_case["id"]
        )

        print(
            "Title:",
            test_case["title"]
        )

        print(
            "Precondition:",
            test_case["precondition"]
        )

        print("Steps:")

        for number, step in enumerate(
            test_case["steps"],
            start=1
        ):

            print(
                f"{number}. {step}"
            )

        print(
            "Expected Result:",
            test_case["expected_result"]
        )

        print(
            "Parent Acceptance Criteria:",
            test_case[
                "parent_acceptance_criteria_id"
            ]
        )

        print(
            "Parent Story:",
            test_case[
                "parent_story_id"
            ]
        )

        print(
            "Parent Epic:",
            test_case[
                "parent_epic_id"
            ]
        )

        print(
            "Source Requirement:",
            test_case[
                "source_requirement_id"
            ]
        )


if not all_test_cases:

    print(
        "\n❌ No Test Cases approved."
    )

    print(
        "Pipeline stopped."
    )

    raise SystemExit(1)


# ============================================================
# STEP 4 — TRACEABILITY VALIDATION
# ============================================================

print("\n")
print("=" * 80)
print("                 TRACEABILITY VALIDATION")
print("=" * 80)


traceability_errors = []


# ============================================================
# VALIDATE USER STORY IDs
# ============================================================

story_ids = [
    story["id"]
    for story in stories
]


if len(story_ids) != len(set(story_ids)):

    traceability_errors.append(
        "Duplicate User Story IDs detected."
    )

else:

    print(
        "\n✅ User Story IDs are unique."
    )


# ============================================================
# VALIDATE ACCEPTANCE CRITERIA IDs
# ============================================================

ac_ids = [
    ac["id"]
    for ac in all_acceptance_criteria
]


if len(ac_ids) != len(set(ac_ids)):

    traceability_errors.append(
        "Duplicate Acceptance Criteria IDs detected."
    )

else:

    print(
        "✅ Acceptance Criteria IDs are unique."
    )


# ============================================================
# VALIDATE TEST CASE IDs
# ============================================================

test_case_ids = [
    tc["id"]
    for tc in all_test_cases
]


if (
    len(test_case_ids)
    != len(set(test_case_ids))
):

    traceability_errors.append(
        "Duplicate Test Case IDs detected."
    )

else:

    print(
        "✅ Test Case IDs are unique."
    )


# ============================================================
# VALIDATE USER STORY → EPIC
# ============================================================

for story in stories:

    if (
        story["parent_epic_id"]
        != approved_epic["id"]
    ):

        traceability_errors.append(

            f"User Story {story['id']} "
            f"has invalid parent Epic "
            f"{story['parent_epic_id']}."
        )


    if (
        story["source_requirement_id"]
        != business_requirement_id
    ):

        traceability_errors.append(

            f"User Story {story['id']} "
            f"has invalid source requirement."
        )


if not any(
    "User Story" in error
    and "invalid parent Epic" in error
    for error in traceability_errors
):

    print(
        "✅ User Story → Epic mapping is valid."
    )


# ============================================================
# VALIDATE AC → USER STORY → EPIC → BR
# ============================================================

for ac in all_acceptance_criteria:

    parent_story = None


    for story in stories:

        if (
            story["id"]
            == ac["parent_story_id"]
        ):

            parent_story = story

            break


    if parent_story is None:

        traceability_errors.append(

            f"Acceptance Criteria {ac['id']} "
            f"references missing User Story "
            f"{ac['parent_story_id']}."
        )

        continue


    if (
        ac["parent_epic_id"]
        != parent_story["parent_epic_id"]
    ):

        traceability_errors.append(

            f"Acceptance Criteria {ac['id']} "
            f"has inconsistent Epic mapping."
        )


    if (
        ac["source_requirement_id"]
        != business_requirement_id
    ):

        traceability_errors.append(

            f"Acceptance Criteria {ac['id']} "
            f"has invalid source requirement."
        )


if not any(
    "Acceptance Criteria" in error
    for error in traceability_errors
):

    print(
        "✅ AC → User Story → Epic → BR mapping is valid."
    )


# ============================================================
# VALIDATE TC → AC → USER STORY → EPIC → BR
# ============================================================

for tc in all_test_cases:

    parent_ac = None


    for ac in all_acceptance_criteria:

        if (
            ac["id"]
            == tc[
                "parent_acceptance_criteria_id"
            ]
        ):

            parent_ac = ac

            break


    if parent_ac is None:

        traceability_errors.append(

            f"Test Case {tc['id']} "
            f"references missing Acceptance Criteria "
            f"{tc['parent_acceptance_criteria_id']}."
        )

        continue


    if (
        tc["parent_story_id"]
        != parent_ac["parent_story_id"]
    ):

        traceability_errors.append(

            f"Test Case {tc['id']} "
            f"has inconsistent User Story mapping."
        )


    if (
        tc["parent_epic_id"]
        != parent_ac["parent_epic_id"]
    ):

        traceability_errors.append(

            f"Test Case {tc['id']} "
            f"has inconsistent Epic mapping."
        )


    if (
        tc["source_requirement_id"]
        != business_requirement_id
    ):

        traceability_errors.append(

            f"Test Case {tc['id']} "
            f"has invalid source requirement."
        )


if not any(
    "Test Case" in error
    for error in traceability_errors
):

    print(
        "✅ TC → AC → User Story → Epic → BR mapping is valid."
    )


# ============================================================
# STEP 5 — DISPLAY COMPLETE TRACEABILITY
# ============================================================

print("\n")
print("=" * 80)
print("                    FINAL TRACEABILITY")
print("=" * 80)


print("\nBUSINESS REQUIREMENT")
print("-" * 80)

print(
    "ID:",
    business_requirement_id
)

print(
    "Requirement:",
    business_requirement.strip()
)


print("\nEPIC")
print("-" * 80)

print(
    "ID:",
    approved_epic["id"]
)

print(
    "Title:",
    approved_epic["title"]
)

print(
    "Description:",
    approved_epic["description"]
)


# ============================================================
# ACTUAL GENERATED TRACEABILITY CHAINS
# ============================================================

print("\nTRACEABILITY CHAINS")
print("-" * 80)


for tc in all_test_cases:

    print(
        f"{business_requirement_id}"
        f" → {tc['parent_epic_id']}"
        f" → {tc['parent_story_id']}"
        f" → {tc['parent_acceptance_criteria_id']}"
        f" → {tc['id']}"
    )


# ============================================================
# STEP 6 — FINAL VALIDATION RESULT
# ============================================================

print("\n")
print("=" * 80)
print("                 TRACEABILITY TEST RESULT")
print("=" * 80)


if traceability_errors:

    print(
        "\n❌ TRACEABILITY VALIDATION FAILED"
    )

    print(
        "\nErrors found:"
    )

    for number, error in enumerate(
        traceability_errors,
        start=1
    ):

        print(
            f"{number}. {error}"
        )


    print("\n")
    print("=" * 80)
    print(
        "❌ END-TO-END TEST FAILED"
    )
    print("=" * 80)

    raise SystemExit(1)


print(
    "\n✅ ALL TRACEABILITY CHECKS PASSED"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 80)
print("                         SUMMARY")
print("=" * 80)


print(
    "\nBusiness Requirement:",
    business_requirement_id
)

print(
    "Epic:",
    approved_epic["id"]
)

print(
    "User Stories:",
    len(stories)
)

print(
    "Acceptance Criteria:",
    len(all_acceptance_criteria)
)

print(
    "Test Cases:",
    len(all_test_cases)
)

print(
    "Unique User Story IDs:",
    len(set(story_ids))
)

print(
    "Unique Acceptance Criteria IDs:",
    len(set(ac_ids))
)

print(
    "Unique Test Case IDs:",
    len(set(test_case_ids))
)


print("\n")
print("=" * 80)
print("             ✅ END-TO-END PIPELINE TEST PASSED")
print("=" * 80)