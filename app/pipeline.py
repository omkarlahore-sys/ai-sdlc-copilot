from app.services.epic_service import (
    generate_and_validate_epic
)

from app.services.user_story_service import (
    generate_and_validate_user_story
)

from app.services.acceptance_criteria_service import (
    generate_and_validate_acceptance_criteria
)

from app.services.test_case_service import (
    generate_and_validate_test_case
)

from app.models.traceability import (
    TraceabilityRecord,
    TraceabilityReport
)


def run_pipeline(
    business_requirement,
    business_requirement_id="BR-001"
):

    print("\n========================================")
    print("       AI SDLC COPILOT PIPELINE")
    print("========================================")


    # ========================================================
    # STEP 1 — EPIC
    # ========================================================

    print("\n[1/4] GENERATING EPIC...")

    epic = generate_and_validate_epic(
        business_requirement,
        business_requirement_id=business_requirement_id
    )

    if epic is None:
        raise RuntimeError(
            "Pipeline stopped: Epic was not approved."
        )


    # ========================================================
    # STEP 2 — USER STORY
    # ========================================================

    print("\n[2/4] GENERATING USER STORY...")

    user_story = generate_and_validate_user_story(
        business_requirement,
        epic,
        business_requirement_id=business_requirement_id,
        epic_id=epic["id"]
    )

    if user_story is None:
        raise RuntimeError(
            "Pipeline stopped: User Story was not approved."
        )


    # ========================================================
    # STEP 3 — ACCEPTANCE CRITERIA
    # ========================================================

    print(
        "\n[3/4] GENERATING ACCEPTANCE CRITERIA..."
    )

    acceptance_criteria = (
        generate_and_validate_acceptance_criteria(
            business_requirement,
            epic,
            user_story,
            business_requirement_id=
                business_requirement_id,
            epic_id=epic["id"],
            user_story_id=user_story["id"]
        )
    )

    if acceptance_criteria is None:
        raise RuntimeError(
            "Pipeline stopped: Acceptance Criteria "
            "was not approved."
        )


    # ========================================================
    # STEP 4 — TEST CASE
    # ========================================================

    print("\n[4/4] GENERATING TEST CASE...")

    test_case = generate_and_validate_test_case(
        business_requirement,
        epic,
        user_story,
        acceptance_criteria,
        business_requirement_id=
            business_requirement_id,
        epic_id=epic["id"],
        user_story_id=user_story["id"],
        acceptance_criteria_id=
            acceptance_criteria["id"]
    )

    if test_case is None:
        raise RuntimeError(
            "Pipeline stopped: Test Case was not approved."
        )


    # ========================================================
    # TRACEABILITY
    # ========================================================

    traceability_record = TraceabilityRecord(
        business_requirement_id=
            business_requirement_id,
        epic_id=epic["id"],
        user_story_id=user_story["id"],
        acceptance_criteria_id=
            acceptance_criteria["id"],
        test_case_id=test_case["id"]
    )

    traceability_report = TraceabilityReport(
        records=[traceability_record]
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "business_requirement": {
            "id": business_requirement_id,
            "text": business_requirement
        },

        "epic": epic,

        "user_story": user_story,

        "acceptance_criteria":
            acceptance_criteria,

        "test_case": test_case,

        "traceability":
            traceability_report
    }