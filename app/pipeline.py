# ============================================================
# AI SDLC COPILOT - PIPELINE SERVICE
# ============================================================

from app.services.epic_service import (
    generate_and_validate_epics
)

from app.services.user_story_service import (
    generate_and_validate_user_stories
)

from app.services.acceptance_criteria_service import (
    generate_and_validate_acceptance_criteria
)

from app.services.test_case_service import (
    generate_and_validate_test_cases
)

from app.models.traceability import (
    TraceabilityRecord,
    TraceabilityReport
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_epic_by_id(epics, epic_id):
    """
    Find an Epic using its stable ID.
    """

    for epic in epics:

        if epic["id"] == epic_id:
            return epic

    return None


def find_user_story_by_id(user_stories, user_story_id):
    """
    Find a User Story using its stable ID.
    """

    for story in user_stories:

        if story["id"] == user_story_id:
            return story

    return None


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline(
    business_requirement,
    business_requirement_id="BR-001"
):

    print("\n" + "=" * 80)
    print("                 AI SDLC COPILOT PIPELINE")
    print("=" * 80)

    # ========================================================
    # STEP 1 — GENERATE EPICS
    # ========================================================

    print("\n[1/4] GENERATING EPICS...")

    epics = generate_and_validate_epics(
        business_requirement,
        business_requirement_id=business_requirement_id
    )

    if not epics:

        raise RuntimeError(
            "Pipeline stopped: No Epic was approved."
        )

    print("\n" + "=" * 70)
    print("APPROVED EPICS")
    print("=" * 70)

    for epic in epics:

        print("\nID:", epic["id"])

        print(
            "Title:",
            epic["title"]
        )

        print(
            "Description:",
            epic["description"]
        )

        print(
            "Source Requirement:",
            epic["source_requirement_id"]
        )

    # ========================================================
    # STEP 2 — GENERATE USER STORIES
    # ========================================================

    print("\n[2/4] GENERATING USER STORIES...")

    all_user_stories = []

    for epic in epics:

        print("\n" + "=" * 70)
        print(
            f"USER STORIES FOR {epic['id']}"
        )
        print("=" * 70)

        user_stories = (
            generate_and_validate_user_stories(
                business_requirement,
                epic,
                business_requirement_id=(
                    business_requirement_id
                ),
                epic_id=epic["id"]
            )
        )

        if not user_stories:

            raise RuntimeError(
                f"Pipeline stopped: No User Stories "
                f"approved for {epic['id']}."
            )

        for story in user_stories:

            all_user_stories.append(story)

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

    if not all_user_stories:

        raise RuntimeError(
            "Pipeline stopped: No User Stories "
            "were approved."
        )

    # ========================================================
    # STEP 3 — GENERATE ACCEPTANCE CRITERIA
    # ========================================================

    print(
        "\n[3/4] GENERATING ACCEPTANCE CRITERIA..."
    )

    all_acceptance_criteria = []

    for story in all_user_stories:

        # ----------------------------------------------------
        # Find Parent Epic
        # ----------------------------------------------------

        parent_epic = find_epic_by_id(
            epics,
            story["parent_epic_id"]
        )

        if parent_epic is None:

            raise RuntimeError(
                f"Pipeline stopped: Parent Epic "
                f"{story['parent_epic_id']} "
                f"not found for User Story "
                f"{story['id']}."
            )

        # ----------------------------------------------------
        # Generate Acceptance Criteria
        # ----------------------------------------------------

        print("\n" + "=" * 70)

        print(
            f"ACCEPTANCE CRITERIA FOR {story['id']}"
        )

        print("=" * 70)

        acceptance_criteria = (
            generate_and_validate_acceptance_criteria(

                business_requirement,

                parent_epic,

                story,

                business_requirement_id=(
                    business_requirement_id
                ),

                epic_id=(
                    parent_epic["id"]
                ),

                user_story_id=(
                    story["id"]
                )
            )
        )

        if not acceptance_criteria:

            raise RuntimeError(
                f"Pipeline stopped: No Acceptance "
                f"Criteria approved for {story['id']}."
            )

        for ac in acceptance_criteria:

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

        raise RuntimeError(
            "Pipeline stopped: No Acceptance "
            "Criteria were approved."
        )

    # ========================================================
    # STEP 4 — GENERATE TEST CASES
    # ========================================================

    print("\n[4/4] GENERATING TEST CASES...")

    all_test_cases = []

    for ac in all_acceptance_criteria:

        # ----------------------------------------------------
        # Find Parent User Story
        # ----------------------------------------------------

        parent_story = find_user_story_by_id(
            all_user_stories,
            ac["parent_story_id"]
        )

        if parent_story is None:

            raise RuntimeError(
                f"Pipeline stopped: Parent User Story "
                f"{ac['parent_story_id']} "
                f"not found for AC {ac['id']}."
            )

        # ----------------------------------------------------
        # Find Parent Epic
        # ----------------------------------------------------

        parent_epic = find_epic_by_id(
            epics,
            parent_story["parent_epic_id"]
        )

        if parent_epic is None:

            raise RuntimeError(
                f"Pipeline stopped: Parent Epic "
                f"{parent_story['parent_epic_id']} "
                f"not found for User Story "
                f"{parent_story['id']}."
            )

        # ----------------------------------------------------
        # Additional Traceability Consistency Check
        # ----------------------------------------------------

        if ac["parent_epic_id"] != parent_epic["id"]:

            raise RuntimeError(
                f"Traceability mismatch: AC {ac['id']} "
                f"belongs to Epic "
                f"{ac['parent_epic_id']}, but its parent "
                f"User Story belongs to Epic "
                f"{parent_epic['id']}."
            )

        # ----------------------------------------------------
        # Generate Test Cases
        # ----------------------------------------------------

        print("\n" + "=" * 70)

        print(
            f"TEST CASES FOR {ac['id']}"
        )

        print("=" * 70)

        test_cases = (
            generate_and_validate_test_cases(

                business_requirement,

                parent_epic,

                parent_story,

                ac,

                business_requirement_id=(
                    business_requirement_id
                ),

                epic_id=(
                    parent_epic["id"]
                ),

                user_story_id=(
                    parent_story["id"]
                ),

                acceptance_criteria_id=(
                    ac["id"]
                )
            )
        )

        if not test_cases:

            raise RuntimeError(
                f"Pipeline stopped: No Test Case "
                f"approved for {ac['id']}."
            )

        for test_case in test_cases:

            # ------------------------------------------------
            # Verify generated traceability
            # ------------------------------------------------

            if (
                test_case[
                    "parent_acceptance_criteria_id"
                ]
                != ac["id"]
            ):

                raise RuntimeError(
                    f"Traceability mismatch: Test Case "
                    f"{test_case['id']} does not belong "
                    f"to Acceptance Criterion {ac['id']}."
                )

            if (
                test_case["parent_story_id"]
                != parent_story["id"]
            ):

                raise RuntimeError(
                    f"Traceability mismatch: Test Case "
                    f"{test_case['id']} does not belong "
                    f"to User Story "
                    f"{parent_story['id']}."
                )

            if (
                test_case["parent_epic_id"]
                != parent_epic["id"]
            ):

                raise RuntimeError(
                    f"Traceability mismatch: Test Case "
                    f"{test_case['id']} does not belong "
                    f"to Epic {parent_epic['id']}."
                )

            if (
                test_case["source_requirement_id"]
                != business_requirement_id
            ):

                raise RuntimeError(
                    f"Traceability mismatch: Test Case "
                    f"{test_case['id']} has incorrect "
                    f"Business Requirement ID."
                )

            all_test_cases.append(test_case)

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

        raise RuntimeError(
            "Pipeline stopped: No Test Cases "
            "were approved."
        )

    # ========================================================
    # STEP 5 — BUILD TRACEABILITY
    # ========================================================

    print("\n" + "=" * 80)
    print("                       TRACEABILITY")
    print("=" * 80)

    traceability_records = []

    for test_case in all_test_cases:

        record = TraceabilityRecord(

            business_requirement_id=(
                test_case[
                    "source_requirement_id"
                ]
            ),

            epic_id=(
                test_case[
                    "parent_epic_id"
                ]
            ),

            user_story_id=(
                test_case[
                    "parent_story_id"
                ]
            ),

            acceptance_criteria_id=(
                test_case[
                    "parent_acceptance_criteria_id"
                ]
            ),

            test_case_id=(
                test_case["id"]
            )
        )

        traceability_records.append(
            record
        )

        print(
            f"\n{record.business_requirement_id}"
            f" → {record.epic_id}"
            f" → {record.user_story_id}"
            f" → {record.acceptance_criteria_id}"
            f" → {record.test_case_id}"
        )

    # ========================================================
    # TRACEABILITY REPORT
    # ========================================================

    traceability_report = TraceabilityReport(
        records=traceability_records
    )

    # ========================================================
    # PIPELINE SUMMARY
    # ========================================================

    print("\n" + "=" * 80)
    print("                         SUMMARY")
    print("=" * 80)

    print(
        "\nBusiness Requirement:",
        business_requirement_id
    )

    print(
        "Epics:",
        len(epics)
    )

    print(
        "User Stories:",
        len(all_user_stories)
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
        "Traceability Records:",
        len(traceability_records)
    )

    print("\n" + "=" * 80)
    print("             ✅ END-TO-END PIPELINE COMPLETED")
    print("=" * 80)

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "business_requirement": {

            "id": business_requirement_id,

            "text": business_requirement
        },

        "epics": epics,

        "user_stories": all_user_stories,

        "acceptance_criteria": (
            all_acceptance_criteria
        ),

        "test_cases": (
            all_test_cases
        ),

        "traceability": (
            traceability_report
        )
    }