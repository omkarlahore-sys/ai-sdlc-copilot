import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.acceptance_criteria import AcceptanceCriteria

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# GENERATE ACCEPTANCE CRITERIA
# ============================================================

def generate_acceptance_criteria(
    business_requirement,
    approved_epic,
    approved_user_story,
    feedback=None
):

    feedback_text = ""

    if feedback:
        feedback_text = f"""
The previous Acceptance Criterion failed validation.

Validator feedback:
{feedback}

Generate a corrected Acceptance Criterion.
Do not repeat the identified problem.
"""

    prompt = f"""
You are an experienced Agile Business Analyst.

Original Business Requirement:

{business_requirement}

Approved Epic:

Title: {approved_epic["title"]}
Description: {approved_epic["description"]}

Approved User Story:

Title: {approved_user_story["title"]}
Story: {approved_user_story["story"]}

Generate ONE Acceptance Criterion for this User Story.

The criterion MUST contain:

Given
When
Then

Rules:

- Given = initial condition.
- When = user action or event.
- Then = expected business outcome.
- It must directly validate the User Story.
- It must belong to the approved Epic.
- It must be supported by the original requirement.
- Every business behavior must be grounded in the original requirement.
- Do not introduce unsupported business rules.
- Do not invent email sending.
- Do not invent reset links.
- Do not invent verification codes.
- Do not invent security rules.
- Do not invent time limits.
- Do not invent database behavior.
- Do not add technical implementation details.
- Do not generate IDs.

{feedback_text}

Return only the structured Acceptance Criterion.
"""

    schema = {
        "type": "object",
        "properties": {
            "given": {
                "type": "string"
            },
            "when": {
                "type": "string"
            },
            "then": {
                "type": "string"
            }
        },
        "required": [
            "given",
            "when",
            "then"
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
                "name": "acceptance_criteria",
                "schema": schema,
                "strict": True
            }
        },
        temperature=0
    )

    data = json.loads(
        response.choices[0].message.content
    )

    return AcceptanceCriteria.model_validate(data)


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_acceptance_criteria(ac):

    errors = []

    if not ac.given.strip():
        errors.append("Given is empty.")

    if not ac.when.strip():
        errors.append("When is empty.")

    if not ac.then.strip():
        errors.append("Then is empty.")

    if errors:
        return False, errors

    return True, []


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_acceptance_criteria(
    business_requirement,
    approved_epic,
    approved_user_story,
    ac
):

    validation_prompt = f"""
You are a STRICT requirements traceability validator.

Your job is to determine whether EVERY business behavior
in the Acceptance Criterion is supported by the ORIGINAL
BUSINESS REQUIREMENT.

Do not judge whether the behavior is common or reasonable.

==============================
ORIGINAL BUSINESS REQUIREMENT
==============================

{business_requirement}

==============================
APPROVED EPIC
==============================

Title: {approved_epic["title"]}
Description: {approved_epic["description"]}

==============================
APPROVED USER STORY
==============================

Title: {approved_user_story["title"]}
Story: {approved_user_story["story"]}

==============================
ACCEPTANCE CRITERION
==============================

Given: {ac.given}

When: {ac.when}

Then: {ac.then}

==============================
STRICT RULES
==============================

1. The AC must directly validate the User Story.

2. The AC must belong logically to the Epic.

3. Every business behavior in Given, When, and Then
   must be supported by the ORIGINAL requirement.

4. The User Story and Epic provide context only.
   They cannot introduce new business requirements.

5. Do not infer common industry behavior.

6. Reject unsupported behavior such as:
   - email sending
   - reset links
   - verification codes
   - security requirements
   - expiration times
   - account verification
   - database behavior
   - APIs
   - technical implementation

7. If ANY unsupported business behavior exists,
   return FAIL.

==============================
OUTPUT
==============================

Return exactly:

PASS

OR

FAIL: <specific unsupported behavior and reason>
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

def generate_and_validate_acceptance_criteria(
    business_requirement,
    approved_epic,
    approved_user_story,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    user_story_id="US-001",
    max_attempts=3
):

    feedback = None

    for attempt in range(1, max_attempts + 1):

        print(
            f"\n===== AC ATTEMPT {attempt} ====="
        )

        # ----------------------------------------------------
        # Generation
        # ----------------------------------------------------

        try:

            ac = generate_acceptance_criteria(
                business_requirement,
                approved_epic,
                approved_user_story,
                feedback
            )

            print("\nGENERATED ACCEPTANCE CRITERIA")
            print("Given:", ac.given)
            print("When:", ac.when)
            print("Then:", ac.then)

        except Exception as error:

            print("\n❌ AC GENERATION ERROR")
            print("Error:", error)

            feedback = (
                "Previous generation failed because of "
                "an LLM error. Generate a valid structured "
                "Acceptance Criterion."
            )

            continue


        # ----------------------------------------------------
        # Python validation
        # ----------------------------------------------------

        valid, errors = (
            python_validate_acceptance_criteria(ac)
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
                semantic_validate_acceptance_criteria(
                    business_requirement,
                    approved_epic,
                    approved_user_story,
                    ac
                )
            )

        except Exception as error:

            print("\n❌ AC SEMANTIC VALIDATION ERROR")
            print("Error:", error)

            feedback = (
                "Semantic validation failed because of "
                "an LLM error. Regenerate the AC."
            )

            continue


        print("\nSEMANTIC VALIDATION:")
        print(semantic_result)


        # ----------------------------------------------------
        # Approval
        # ----------------------------------------------------

        if semantic_result.startswith("PASS"):

            approved_ac = {
                "id": "AC-001",
                "given": ac.given,
                "when": ac.when,
                "then": ac.then,
                "parent_story_id": user_story_id,
                "parent_epic_id": epic_id,
                "source_requirement_id":
                    business_requirement_id
            }

            print("\n✅ ACCEPTANCE CRITERIA APPROVED")

            return approved_ac

        else:

            feedback = semantic_result

            print("\n❌ ACCEPTANCE CRITERIA REJECTED")
            print("🔄 Regeneration required.")


    print("\n❌ ACCEPTANCE CRITERIA GENERATION FAILED")
    print("Maximum attempts reached.")

    return None