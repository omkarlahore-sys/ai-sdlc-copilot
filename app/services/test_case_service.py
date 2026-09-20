import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.test_case import TestCase


# ============================================================
# ENVIRONMENT / LLM CLIENT
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# GENERATE TEST CASE CANDIDATES
# ============================================================

def generate_test_case_candidates(
    business_requirement,
    approved_epic,
    approved_user_story,
    approved_ac,
    feedback=None,
    number_of_test_cases=3
):

    feedback_text = ""

    if feedback:
        feedback_text = f"""
Previous Test Case candidates failed validation.

Validator feedback:

{feedback}

Generate corrected Test Cases.
Do not repeat the identified problems.
"""

    prompt = f"""
You are an experienced QA engineer and SDLC analyst.

Your task is to generate functional Test Case candidates
for the APPROVED Acceptance Criterion.

==============================
ORIGINAL BUSINESS REQUIREMENT
==============================

{business_requirement}

==============================
APPROVED EPIC
==============================

Title:
{approved_epic["title"]}

Description:
{approved_epic["description"]}

==============================
APPROVED USER STORY
==============================

Title:
{approved_user_story["title"]}

Story:
{approved_user_story["story"]}

==============================
APPROVED ACCEPTANCE CRITERION
==============================

Given:
{approved_ac["given"]}

When:
{approved_ac["when"]}

Then:
{approved_ac["then"]}

==============================
TASK
==============================

Generate UP TO {number_of_test_cases} distinct functional
Test Case candidates.

The number {number_of_test_cases} is a MAXIMUM.

Do NOT create additional Test Cases merely to reach
the requested number.

If the Acceptance Criterion supports only one valid
Test Case, generate only one.

==============================
TEST CASE STRUCTURE
==============================

Each Test Case must contain:

1. Title
2. Precondition
3. Steps
4. Expected Result

==============================
TRACEABILITY RULES
==============================

1. The Test Case must directly verify the
   Acceptance Criterion.

2. Precondition must be derived from Given.

3. Steps must perform the action represented by When.

4. Expected Result must verify Then.

5. The Test Case must remain consistent with
   the approved User Story.

6. The Test Case must remain consistent with
   the approved Epic.

7. The Test Case must remain supported by the
   original Business Requirement.

==============================
STRICT GROUNDING RULES
==============================

Do NOT introduce unsupported business behavior.

Do NOT assume common industry behavior.

Do NOT invent:

- password reset pages
- login pages
- buttons
- forms
- UI screens
- emails
- reset links
- verification codes
- security rules
- expiration times
- account verification
- database behavior
- APIs
- backend implementation
- frontend implementation
- technical architecture
- infrastructure details

Do not assume a UI or technical implementation unless
it is explicitly supported by the approved artifacts.

Do not create negative scenarios unless they are directly
supported by the Acceptance Criterion or original
Business Requirement.

Do not generate IDs.

Do not generate duplicate or equivalent Test Cases.

Prefer fewer valid Test Cases over unsupported
Test Cases.

==============================
IMPORTANT
==============================

The Acceptance Criterion is the immediate source of truth
for the Test Case.

The User Story and Epic provide additional traceability
context.

The original Business Requirement is the ultimate source
for business behavior.

{feedback_text}

Return only the structured Test Case list.
"""

    schema = {
        "type": "object",
        "properties": {
            "test_cases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "precondition": {
                            "type": "string"
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "expected_result": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "title",
                        "precondition",
                        "steps",
                        "expected_result"
                    ],
                    "additionalProperties": False
                },
                "minItems": 1,
                "maxItems": 5
            }
        },
        "required": [
            "test_cases"
        ],
        "additionalProperties": False
    }

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "functional_test_cases",
                "schema": schema,
                "strict": True
            }
        },

        temperature=0
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned an empty response."
        )

    data = json.loads(content)

    validated_test_cases = []

    for item in data["test_cases"]:

        test_case = TestCase.model_validate(item)

        validated_test_cases.append(test_case)

    return validated_test_cases


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_test_case(test_case):

    errors = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    if not test_case.title.strip():
        errors.append(
            "Test Case title is empty."
        )

    # --------------------------------------------------------
    # Precondition
    # --------------------------------------------------------

    if not test_case.precondition.strip():
        errors.append(
            "Precondition is empty."
        )

    # --------------------------------------------------------
    # Steps
    # --------------------------------------------------------

    if not test_case.steps:

        errors.append(
            "Test Case must contain at least one step."
        )

    else:

        if any(
            not isinstance(step, str)
            or not step.strip()
            for step in test_case.steps
        ):

            errors.append(
                "Test Case contains an empty step."
            )

    # --------------------------------------------------------
    # Expected Result
    # --------------------------------------------------------

    if not test_case.expected_result.strip():

        errors.append(
            "Expected result is empty."
        )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    if errors:
        return False, errors

    return True, []


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate_test_case(
    test_case,
    approved_test_cases
):

    current = (
        test_case.title.strip().lower(),

        test_case.precondition.strip().lower(),

        tuple(
            step.strip().lower()
            for step in test_case.steps
        ),

        test_case.expected_result.strip().lower()
    )

    for existing in approved_test_cases:

        existing_value = (
            existing["title"].strip().lower(),

            existing["precondition"].strip().lower(),

            tuple(
                step.strip().lower()
                for step in existing["steps"]
            ),

            existing["expected_result"]
            .strip()
            .lower()
        )

        if current == existing_value:

            return True

    return False


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_test_case(
    business_requirement,
    approved_epic,
    approved_user_story,
    approved_ac,
    test_case
):

    validation_prompt = f"""
You are a STRICT SDLC and QA traceability validator.

Validate the Test Case against the complete
approved artifact chain.

==============================
BUSINESS REQUIREMENT
==============================

{business_requirement}

==============================
APPROVED EPIC
==============================

Title:
{approved_epic["title"]}

Description:
{approved_epic["description"]}

==============================
APPROVED USER STORY
==============================

Title:
{approved_user_story["title"]}

Story:
{approved_user_story["story"]}

==============================
APPROVED ACCEPTANCE CRITERION
==============================

Given:
{approved_ac["given"]}

When:
{approved_ac["when"]}

Then:
{approved_ac["then"]}

==============================
GENERATED TEST CASE
==============================

Title:
{test_case.title}

Precondition:
{test_case.precondition}

Steps:
{test_case.steps}

Expected Result:
{test_case.expected_result}

==============================
VALIDATION RULES
==============================

1. The Test Case must directly test the
   Acceptance Criterion.

2. Precondition must be consistent with Given.

3. Test Steps must perform the action represented
   by When.

4. Expected Result must verify Then.

5. The Test Case must remain consistent with
   the User Story.

6. The Test Case must remain consistent with
   the Epic.

7. The Test Case must remain supported by the
   original Business Requirement.

8. Do not accept behavior merely because it is
   common in real-world systems.

9. Reject unsupported assumptions such as:

   - password reset pages
   - login pages
   - buttons
   - forms
   - UI screens
   - emails
   - reset links
   - verification codes
   - security policies
   - expiration times
   - account verification
   - database operations
   - APIs
   - backend implementation
   - frontend implementation
   - technical implementation

10. Every business behavior introduced by the
    Test Case must be supported by the approved
    Acceptance Criterion and source artifacts.

11. Do not infer requirements that are not present
    in the source artifacts.

12. Do not introduce a new business workflow.

13. Do not introduce unsupported negative scenarios.

14. If ANY unsupported behavior exists,
    return FAIL.

Be STRICT.

==============================
OUTPUT
==============================

Return exactly:

PASS

OR

FAIL: <specific reason>
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "user",
                "content": validation_prompt
            }
        ],

        temperature=0
    )

    result = response.choices[0].message.content

    if not result:
        raise ValueError(
            "Semantic validator returned an empty response."
        )

    return result.strip()


# ============================================================
# GENERATE + VALIDATE TEST CASES
# ============================================================

def generate_and_validate_test_cases(
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
):

    approved_test_cases = []

    feedback = None

    # ========================================================
    # GENERATION / REGENERATION LOOP
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            f"\n===== TEST CASE GENERATION "
            f"ATTEMPT {attempt} ====="
        )

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        try:

            generated_test_cases = (
                generate_test_case_candidates(
                    business_requirement,
                    approved_epic,
                    approved_user_story,
                    approved_ac,
                    feedback,
                    number_of_test_cases
                )
            )

        except Exception as error:

            print(
                "\n❌ TEST CASE GENERATION ERROR"
            )

            print(
                "Error:",
                error
            )

            feedback = (
                "Test Case generation failed. "
                "Generate a valid structured Test Case list."
            )

            continue

        if not generated_test_cases:

            print(
                "\n❌ NO TEST CASE CANDIDATES GENERATED"
            )

            feedback = (
                "No Test Cases were generated. "
                "Generate at least one valid Test Case."
            )

            continue

        print(
            f"\nGenerated "
            f"{len(generated_test_cases)} "
            f"Test Case candidate(s)"
        )

        rejected_feedback = []

        # ----------------------------------------------------
        # VALIDATE EACH CANDIDATE
        # ----------------------------------------------------

        for index, test_case in enumerate(
            generated_test_cases,
            start=1
        ):

            print(
                f"\n--- TEST CASE CANDIDATE "
                f"{index} ---"
            )

            print(
                "Title:",
                test_case.title
            )

            print(
                "Precondition:",
                test_case.precondition
            )

            print("Steps:")

            for number, step in enumerate(
                test_case.steps,
                start=1
            ):

                print(
                    f"{number}. {step}"
                )

            print(
                "Expected Result:",
                test_case.expected_result
            )

            # =================================================
            # PYTHON VALIDATION
            # =================================================

            valid, errors = (
                python_validate_test_case(
                    test_case
                )
            )

            if not valid:

                reason = "; ".join(errors)

                print(
                    "\nPYTHON VALIDATION: FAIL"
                )

                print(
                    "Reason:",
                    reason
                )

                rejected_feedback.append(
                    reason
                )

                continue

            print(
                "\nPYTHON VALIDATION: PASS"
            )

            # =================================================
            # DUPLICATE CHECK
            # =================================================

            if is_duplicate_test_case(
                test_case,
                approved_test_cases
            ):

                reason = (
                    "Equivalent Test Case "
                    "already approved."
                )

                print(
                    "\nDUPLICATE CHECK: FAIL"
                )

                print(
                    "Reason:",
                    reason
                )

                rejected_feedback.append(
                    reason
                )

                continue

            print(
                "\nDUPLICATE CHECK: PASS"
            )

            # =================================================
            # SEMANTIC VALIDATION
            # =================================================

            try:

                semantic_result = (
                    semantic_validate_test_case(
                        business_requirement,
                        approved_epic,
                        approved_user_story,
                        approved_ac,
                        test_case
                    )
                )

            except Exception as error:

                print(
                    "\n❌ SEMANTIC "
                    "VALIDATION ERROR"
                )

                print(
                    "Error:",
                    error
                )

                rejected_feedback.append(
                    "Semantic validation failed."
                )

                continue

            print(
                "\nSEMANTIC VALIDATION:"
            )

            print(
                semantic_result
            )

            # =================================================
            # APPROVAL
            # =================================================

            if semantic_result.startswith("PASS"):

                tc_id = (
                    f"TC-"
                    f"{len(approved_test_cases) + 1:03d}"
                )

                approved_test_case = {

                    "id":
                        tc_id,

                    "title":
                        test_case.title,

                    "precondition":
                        test_case.precondition,

                    "steps":
                        test_case.steps,

                    "expected_result":
                        test_case.expected_result,

                    "parent_acceptance_criteria_id":
                        acceptance_criteria_id,

                    "parent_story_id":
                        user_story_id,

                    "parent_epic_id":
                        epic_id,

                    "source_requirement_id":
                        business_requirement_id
                }

                approved_test_cases.append(
                    approved_test_case
                )

                print(
                    f"\n✅ TEST CASE APPROVED: "
                    f"{tc_id}"
                )

            else:

                print(
                    "\n❌ TEST CASE REJECTED"
                )

                rejected_feedback.append(
                    semantic_result
                )

        # ====================================================
        # SUCCESS
        # ====================================================

        if approved_test_cases:

            print(
                "\n✅ At least one valid "
                "Test Case approved."
            )

            break

        # ====================================================
        # REGENERATION FEEDBACK
        # ====================================================

        if rejected_feedback:

            feedback = "\n".join(
                rejected_feedback
            )

        else:

            feedback = (
                "All generated Test Cases were rejected. "
                "Generate new Test Cases strictly grounded "
                "in the approved Acceptance Criterion."
            )

        if attempt < max_attempts:

            print(
                "\n🔄 Additional Test Case "
                "generation required."
            )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    if not approved_test_cases:

        print(
            "\n❌ NO TEST CASES APPROVED"
        )

        print(
            f"Maximum attempts reached: "
            f"{max_attempts}"
        )

        return []

    # ========================================================
    # FINAL APPROVED TEST CASES
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "APPROVED TEST CASES"
    )

    print(
        "========================================"
    )

    for tc in approved_test_cases:

        print(
            f"\nID: {tc['id']}"
        )

        print(
            "Title:",
            tc["title"]
        )

        print(
            "Precondition:",
            tc["precondition"]
        )

        print("Steps:")

        for number, step in enumerate(
            tc["steps"],
            start=1
        ):

            print(
                f"{number}. {step}"
            )

        print(
            "Expected Result:",
            tc["expected_result"]
        )

        print(
            "Parent Acceptance Criteria:",
            tc[
                "parent_acceptance_criteria_id"
            ]
        )

        print(
            "Parent Story:",
            tc[
                "parent_story_id"
            ]
        )

        print(
            "Parent Epic:",
            tc[
                "parent_epic_id"
            ]
        )

        print(
            "Source Requirement:",
            tc[
                "source_requirement_id"
            ]
        )

    return approved_test_cases