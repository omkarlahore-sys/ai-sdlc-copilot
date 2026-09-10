import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.test_case import TestCase

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# GENERATE TEST CASE
# ============================================================

def generate_test_case(
    business_requirement,
    approved_epic,
    approved_user_story,
    approved_ac,
    feedback=None
):

    feedback_text = ""

    if feedback:
        feedback_text = f"""
The previous Test Case failed validation.

Validator feedback:
{feedback}

Generate a corrected Test Case.
Do not repeat the identified problem.
"""

    prompt = f"""
You are an experienced QA engineer.

Generate ONE functional Test Case for the
APPROVED Acceptance Criterion.

Original Business Requirement:
{business_requirement}

Approved Epic:
{approved_epic["title"]}
{approved_epic["description"]}

Approved User Story:
{approved_user_story["title"]}
{approved_user_story["story"]}

Approved Acceptance Criterion:

Given:
{approved_ac["given"]}

When:
{approved_ac["when"]}

Then:
{approved_ac["then"]}

Rules:

1. The Test Case must directly verify the
   Acceptance Criterion.

2. The precondition must be based on Given.

3. The test steps must represent the action
   described by When.

4. The expected result must verify Then.

5. The Test Case must remain consistent with
   the User Story, Epic, and Business Requirement.

6. Do not introduce unsupported business behavior.

7. Do not invent:
   - password reset pages
   - emails
   - reset links
   - verification codes
   - security rules
   - expiration times
   - database behavior
   - APIs
   - technical implementation details

8. Do not generate IDs.

{feedback_text}

Return only the structured Test Case.
"""

    schema = {
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
                "name": "functional_test_case",
                "schema": schema,
                "strict": True
            }
        },
        temperature=0
    )

    data = json.loads(
        response.choices[0].message.content
    )

    return TestCase.model_validate(data)


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_test_case(test_case):

    errors = []

    if not test_case.title.strip():
        errors.append("Test Case title is empty.")

    if not test_case.precondition.strip():
        errors.append("Precondition is empty.")

    if not test_case.steps:
        errors.append(
            "Test Case must contain at least one step."
        )

    if any(not step.strip() for step in test_case.steps):
        errors.append(
            "Test Case contains an empty step."
        )

    if not test_case.expected_result.strip():
        errors.append(
            "Expected result is empty."
        )

    if errors:
        return False, errors

    return True, []


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

{approved_epic["title"]}
{approved_epic["description"]}

==============================
APPROVED USER STORY
==============================

{approved_user_story["title"]}
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
STRICT RULES
==============================

1. The Test Case must directly test the
   Acceptance Criterion.

2. Precondition must be consistent with Given.

3. Test steps must actually perform the
   action described by When.

4. Expected Result must verify Then.

5. The Test Case must remain consistent with
   the User Story.

6. The Test Case must remain consistent with
   the Epic.

7. The Test Case must remain supported by the
   original Business Requirement.

8. Do not accept behavior simply because it is
   common in real-world password-reset systems.

9. Reject unsupported assumptions such as:
   - password reset pages
   - email sending
   - reset links
   - verification codes
   - security policies
   - expiration times
   - database operations
   - APIs
   - technical implementation details

10. Every business behavior introduced by the
    Test Case must be supported by the approved
    source artifacts.

Be STRICT.

If ANY unsupported behavior exists, return FAIL.

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

    return response.choices[0].message.content.strip()


# ============================================================
# GENERATE + VALIDATE
# ============================================================

def generate_and_validate_test_case(
    business_requirement,
    approved_epic,
    approved_user_story,
    approved_ac,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    user_story_id="US-001",
    acceptance_criteria_id="AC-001",
    max_attempts=3
):

    feedback = None

    for attempt in range(1, max_attempts + 1):

        print(
            f"\n===== TEST CASE ATTEMPT {attempt} ====="
        )

        # ----------------------------------------------------
        # Generation
        # ----------------------------------------------------

        try:

            test_case = generate_test_case(
                business_requirement,
                approved_epic,
                approved_user_story,
                approved_ac,
                feedback
            )

            print("\nGENERATED TEST CASE")
            print("Title:", test_case.title)
            print(
                "Precondition:",
                test_case.precondition
            )

            print("Steps:")

            for number, step in enumerate(
                test_case.steps,
                start=1
            ):
                print(f"{number}. {step}")

            print(
                "Expected Result:",
                test_case.expected_result
            )

        except Exception as error:

            print("\n❌ TEST CASE GENERATION ERROR")
            print("Error:", error)

            feedback = (
                "Previous generation failed because "
                "of an LLM error. Generate a valid "
                "structured Test Case."
            )

            continue


        # ----------------------------------------------------
        # Python validation
        # ----------------------------------------------------

        valid, errors = python_validate_test_case(
            test_case
        )

        if not valid:

            feedback = "; ".join(errors)

            print("\nPYTHON VALIDATION: FAIL")
            print("Reason:", feedback)

            continue

        print("\nPYTHON VALIDATION: PASS")


        # ----------------------------------------------------
        # Semantic validation
        # ----------------------------------------------------

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
                "\n❌ SEMANTIC VALIDATION ERROR"
            )
            print("Error:", error)

            feedback = (
                "Semantic validation failed because "
                "of an LLM error. Regenerate the "
                "Test Case."
            )

            continue


        print("\nSEMANTIC VALIDATION:")
        print(semantic_result)


        # ----------------------------------------------------
        # Approval
        # ----------------------------------------------------

        if semantic_result.startswith("PASS"):

            approved_test_case = {
                "id": "TC-001",
                "title": test_case.title,
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

            print("\n✅ TEST CASE APPROVED")

            return approved_test_case

        else:

            feedback = semantic_result

            print("\n❌ TEST CASE REJECTED")
            print("🔄 Regeneration required.")


    print("\n❌ TEST CASE GENERATION FAILED")
    print("Maximum attempts reached.")

    return None