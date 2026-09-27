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
# HELPER
# ============================================================

def safe_text(value):
    """
    Safely convert value to clean text.
    """

    if value is None:
        return ""

    return str(value).strip()


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
    """
    Generate Test Case candidates for one approved
    Acceptance Criterion.
    """

    feedback_text = ""

    if feedback:

        feedback_text = f"""
============================================================
PREVIOUS VALIDATION FEEDBACK
============================================================

Previous Test Case candidates were rejected.

Fix ONLY the problems identified below.

{feedback}

IMPORTANT:
- Do not repeat rejected behavior.
- Do not invent requirements.
- Keep every Test Case traceable to the approved
  Acceptance Criterion.
- Generate fewer Test Cases if fewer are supported.
"""


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are an experienced QA Engineer and SDLC Analyst.

Your task is to generate functional Test Cases for ONE
APPROVED Acceptance Criterion.

============================================================
ORIGINAL BUSINESS REQUIREMENT
============================================================

{business_requirement}

============================================================
APPROVED EPIC
============================================================

Title:
{approved_epic["title"]}

Description:
{approved_epic["description"]}

============================================================
APPROVED USER STORY
============================================================

Title:
{approved_user_story["title"]}

Story:
{approved_user_story["story"]}

============================================================
APPROVED ACCEPTANCE CRITERION
============================================================

Given:
{approved_ac["given"]}

When:
{approved_ac["when"]}

Then:
{approved_ac["then"]}

============================================================
TASK
============================================================

Generate UP TO {number_of_test_cases} distinct functional
Test Cases for the approved Acceptance Criterion.

{number_of_test_cases} is the MAXIMUM.

You do NOT need to generate exactly
{number_of_test_cases} Test Cases.

If only one valid Test Case is supported,
generate one.

If two valid Test Cases are supported,
generate two.

NEVER invent additional Test Cases simply to reach
the maximum.

============================================================
TEST CASE STRUCTURE
============================================================

Every Test Case MUST contain:

1. Title
2. Precondition
3. Steps
4. Expected Result

============================================================
TRACEABILITY RULES
============================================================

The APPROVED ACCEPTANCE CRITERION is the immediate
source of truth.

The User Story and Epic provide additional context.

The Original Business Requirement is the ultimate
source of business behavior.

============================================================
STRICT TRACEABILITY
============================================================

1. The Test Case must directly verify the
   Acceptance Criterion.

2. Precondition must be derived from Given.

3. Steps must perform the business action represented
   by When.

4. Expected Result must verify Then.

5. The Test Case must remain consistent with the
   approved User Story.

6. The Test Case must remain consistent with the
   approved Epic.

7. The Test Case must remain supported by the
   Original Business Requirement.

8. Do NOT infer missing requirements.

9. Do NOT use common industry practices as evidence.

============================================================
DO NOT INVENT
============================================================

Do NOT introduce unsupported:

- password reset pages
- login pages
- buttons
- forms
- UI screens
- emails
- reset links
- verification codes
- OTP
- security rules
- expiration times
- account verification
- database behavior
- APIs
- backend implementation
- frontend implementation
- technical architecture
- infrastructure
- technical error handling
- unsupported error messages

Do not assume a UI or technical implementation unless
it is explicitly supported by the source artifacts.

============================================================
NEGATIVE SCENARIOS
============================================================

Do NOT create negative Test Cases unless the negative
behavior is directly supported by the Acceptance Criterion
or Original Business Requirement.

============================================================
DUPLICATION
============================================================

Do not generate duplicate or equivalent Test Cases.

Prefer fewer valid Test Cases over unsupported
Test Cases.

Do not generate IDs.

============================================================
IMPORTANT
============================================================

The Test Case must verify the business behavior.

Do not turn the Test Case into a technical implementation
description.

{feedback_text}

============================================================
OUTPUT
============================================================

Return ONLY the structured Test Case list.
"""


    # ========================================================
    # JSON SCHEMA
    # ========================================================

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

                "maxItems": number_of_test_cases
            }
        },

        "required": [
            "test_cases"
        ],

        "additionalProperties": False
    }


    # ========================================================
    # LLM CALL
    # ========================================================

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


    # ========================================================
    # SAFE RESPONSE VALIDATION
    # ========================================================

    if not response:

        raise ValueError(
            "LLM returned no Test Case response."
        )


    if not response.choices:

        raise ValueError(
            "LLM returned no choices."
        )


    message = response.choices[0].message

    content = message.content


    if not content:

        raise ValueError(
            "LLM returned an empty Test Case response."
        )


    # ========================================================
    # JSON PARSING
    # ========================================================

    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by LLM: {error}"
        )


    if not isinstance(data, dict):

        raise ValueError(
            "LLM Test Case response is not a JSON object."
        )


    if "test_cases" not in data:

        raise ValueError(
            "LLM response does not contain 'test_cases'."
        )


    if not data["test_cases"]:

        raise ValueError(
            "LLM returned an empty Test Case list."
        )


    # ========================================================
    # PYDANTIC VALIDATION
    # ========================================================

    validated_test_cases = []


    for item in data["test_cases"]:

        test_case = TestCase.model_validate(item)

        validated_test_cases.append(
            test_case
        )


    return validated_test_cases


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_test_case(test_case):

    errors = []


    # ========================================================
    # TITLE
    # ========================================================

    if not safe_text(
        test_case.title
    ):

        errors.append(
            "Test Case title is empty."
        )


    # ========================================================
    # PRECONDITION
    # ========================================================

    if not safe_text(
        test_case.precondition
    ):

        errors.append(
            "Precondition is empty."
        )


    # ========================================================
    # STEPS
    # ========================================================

    if not test_case.steps:

        errors.append(
            "Test Case must contain at least one step."
        )

    else:

        for step in test_case.steps:

            if not isinstance(
                step,
                str
            ):

                errors.append(
                    "Test Case contains a non-string step."
                )

                break


            if not step.strip():

                errors.append(
                    "Test Case contains an empty step."
                )

                break


    # ========================================================
    # EXPECTED RESULT
    # ========================================================

    if not safe_text(
        test_case.expected_result
    ):

        errors.append(
            "Expected result is empty."
        )


    # ========================================================
    # RESULT
    # ========================================================

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
    """
    Detect exact duplicate Test Cases.
    """

    current = (

        safe_text(
            test_case.title
        ).lower(),

        safe_text(
            test_case.precondition
        ).lower(),

        tuple(
            safe_text(step).lower()
            for step in test_case.steps
        ),

        safe_text(
            test_case.expected_result
        ).lower()
    )


    for existing in approved_test_cases:

        existing_value = (

            safe_text(
                existing["title"]
            ).lower(),

            safe_text(
                existing["precondition"]
            ).lower(),

            tuple(
                safe_text(step).lower()
                for step in existing["steps"]
            ),

            safe_text(
                existing["expected_result"]
            ).lower()
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
    """
    LLM-based Test Case traceability validation.

    Returns:

        PASS

    OR

        FAIL: reason
    """

    validation_prompt = f"""
You are a STRICT but FAIR SDLC and QA
traceability validator.

Validate the Test Case against the complete
approved artifact chain.

============================================================
ORIGINAL BUSINESS REQUIREMENT
============================================================

{business_requirement}

============================================================
APPROVED EPIC
============================================================

Title:
{approved_epic["title"]}

Description:
{approved_epic["description"]}

============================================================
APPROVED USER STORY
============================================================

Title:
{approved_user_story["title"]}

Story:
{approved_user_story["story"]}

============================================================
APPROVED ACCEPTANCE CRITERION
============================================================

Given:
{approved_ac["given"]}

When:
{approved_ac["when"]}

Then:
{approved_ac["then"]}

============================================================
GENERATED TEST CASE
============================================================

Title:
{test_case.title}

Precondition:
{test_case.precondition}

Steps:
{test_case.steps}

Expected Result:
{test_case.expected_result}

============================================================
VALIDATION RULES
============================================================

1. The Test Case must directly test the
   Acceptance Criterion.

2. Precondition must be consistent with Given.

3. Steps must perform the business action
   represented by When.

4. Expected Result must verify Then.

5. The Test Case must remain consistent
   with the User Story.

6. The Test Case must remain consistent
   with the Epic.

7. The Test Case must remain supported by
   the Original Business Requirement.

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
   - OTP
   - security policies
   - expiration times
   - account verification
   - database operations
   - APIs
   - backend implementation
   - frontend implementation
   - technical architecture
   - infrastructure

10. Every business behavior introduced by the
    Test Case must be supported by the approved
    Acceptance Criterion.

11. Do not infer requirements that are not present
    in the source artifacts.

12. Do not introduce a new business workflow.

13. Do not introduce unsupported negative scenarios.

14. Do not introduce technical implementation details.

15. If ANY unsupported behavior exists,
    return FAIL.

16. If the complete Test Case is supported,
    return PASS.

============================================================
OUTPUT
============================================================

Return EXACTLY:

PASS

OR

FAIL: <specific reason>
"""


    # ========================================================
    # LLM CALL
    # ========================================================

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


    # ========================================================
    # SAFE RESPONSE HANDLING
    # ========================================================

    if not response:

        return (
            "FAIL: Semantic validator returned no response. "
            "Regenerate the Test Case."
        )


    if not response.choices:

        return (
            "FAIL: Semantic validator returned no choices. "
            "Regenerate the Test Case."
        )


    result = response.choices[0].message.content


    if not result:

        return (
            "FAIL: Semantic validator produced no result. "
            "Regenerate the Test Case and keep it strictly "
            "grounded in the Acceptance Criterion."
        )


    result = result.strip()


    if not result:

        return (
            "FAIL: Semantic validator produced an empty result. "
            "Regenerate the Test Case."
        )


    return result


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
    max_attempts=5
):
    """
    Generate, validate and return Test Cases.

    Default maximum attempts = 5.

    Always returns a list.
    """


    # ========================================================
    # SAFETY
    # ========================================================

    if max_attempts < 1:

        max_attempts = 1


    if number_of_test_cases < 1:

        number_of_test_cases = 1


    # ========================================================
    # APPROVED TEST CASES
    # ========================================================

    approved_test_cases = []


    # ========================================================
    # FEEDBACK
    # ========================================================

    feedback = None


    # ========================================================
    # GENERATION / REGENERATION LOOP
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            "\n"
            + "=" * 70
        )

        print(
            f"TEST CASE GENERATION ATTEMPT "
            f"{attempt}/{max_attempts}"
        )

        print(
            "=" * 70
        )


        # ====================================================
        # GENERATE
        # ====================================================

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
                "The previous Test Case generation failed "
                "because the LLM response was empty, invalid, "
                "or malformed.\n\n"
                "Generate a valid structured Test Case list."
            )


            if attempt < max_attempts:

                print(
                    "\n🔄 Regeneration required."
                )

                print(
                    f"Next attempt: "
                    f"{attempt + 1}/{max_attempts}"
                )

                continue


            break


        # ====================================================
        # EMPTY RESULT
        # ====================================================

        if not generated_test_cases:

            print(
                "\n❌ NO TEST CASE CANDIDATES GENERATED"
            )


            feedback = (
                "No Test Cases were generated.\n"
                "Generate at least one valid Test Case "
                "strictly grounded in the approved "
                "Acceptance Criterion."
            )


            if attempt < max_attempts:

                print(
                    "\n🔄 Regeneration required."
                )

                continue


            break


        print(
            f"\nGenerated "
            f"{len(generated_test_cases)} "
            f"Test Case candidate(s)"
        )


        # ====================================================
        # REJECTED FEEDBACK
        # ====================================================

        rejected_feedback = []


        # ====================================================
        # VALIDATE EACH CANDIDATE
        # ====================================================

        for index, test_case in enumerate(
            generated_test_cases,
            start=1
        ):

            print(
                "\n"
                + "-" * 60
            )

            print(
                f"TEST CASE CANDIDATE {index}"
            )

            print(
                "-" * 60
            )


            print(
                "Title:",
                test_case.title
            )


            print(
                "Precondition:",
                test_case.precondition
            )


            print(
                "Steps:"
            )


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

                reason = "; ".join(
                    errors
                )


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
                    "\n❌ TEST CASE SEMANTIC "
                    "VALIDATION ERROR"
                )


                print(
                    "Error:",
                    error
                )


                rejected_feedback.append(
                    "Semantic validation failed because "
                    "the validator encountered an error."
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

            if semantic_result.upper().startswith(
                "PASS"
            ):

                approved_test_cases.append(
                    {
                        "title":
                            test_case.title,

                        "precondition":
                            test_case.precondition,

                        "steps":
                            test_case.steps,

                        "expected_result":
                            test_case.expected_result
                    }
                )


                print(
                    "\n✅ TEST CASE APPROVED"
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
                "\n"
                + "=" * 70
            )

            print(
                "✅ TEST CASE GENERATION SUCCESSFUL"
            )

            print(
                f"Approved Test Cases: "
                f"{len(approved_test_cases)}"
            )

            print(
                f"Completed on attempt: "
                f"{attempt}/{max_attempts}"
            )

            print(
                "=" * 70
            )


            break


        # ====================================================
        # NO TEST CASE APPROVED
        # ====================================================

        print(
            "\n❌ NO TEST CASES APPROVED "
            f"ON ATTEMPT {attempt}"
        )


        # ====================================================
        # BUILD FEEDBACK
        # ====================================================

        if rejected_feedback:

            # Keep feedback bounded so that the next
            # generation prompt does not grow indefinitely.

            feedback = "\n".join(
                rejected_feedback[:10]
            )

        else:

            feedback = (
                "All generated Test Cases were rejected.\n"
                "Generate new Test Cases strictly grounded "
                "in the approved Acceptance Criterion."
            )


        # ====================================================
        # REGENERATION
        # ====================================================

        if attempt < max_attempts:

            print(
                "\n🔄 REGENERATION REQUIRED"
            )

            print(
                f"Next attempt: "
                f"{attempt + 1}/{max_attempts}"
            )

        else:

            print(
                "\n⛔ MAXIMUM TEST CASE "
                "ATTEMPTS REACHED"
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    if not approved_test_cases:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "❌ TEST CASE GENERATION FAILED"
        )

        print(
            f"Maximum attempts reached: "
            f"{max_attempts}"
        )

        print(
            "=" * 70
        )


        # IMPORTANT:
        # Always return a list.

        return []


    # ========================================================
    # ASSIGN IDs AFTER APPROVAL
    # ========================================================

    final_test_cases = []


    for index, test_case in enumerate(
        approved_test_cases,
        start=1
    ):

        final_test_cases.append(
            {
                "id":
                    f"TC-{index:03d}",

                "title":
                    test_case["title"],

                "precondition":
                    test_case["precondition"],

                "steps":
                    test_case["steps"],

                "expected_result":
                    test_case["expected_result"],

                "parent_acceptance_criteria_id":
                    acceptance_criteria_id,

                "parent_story_id":
                    user_story_id,

                "parent_epic_id":
                    epic_id,

                "source_requirement_id":
                    business_requirement_id
            }
        )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "APPROVED TEST CASES"
    )

    print(
        "=" * 70
    )


    for tc in final_test_cases:

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


        print(
            "Steps:"
        )


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


    return final_test_cases