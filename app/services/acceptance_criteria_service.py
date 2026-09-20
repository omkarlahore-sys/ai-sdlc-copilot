import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.acceptance_criteria import AcceptanceCriteria


# ============================================================
# ENVIRONMENT / CLIENT
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# GENERATE ACCEPTANCE CRITERIA CANDIDATES
# ============================================================

def generate_acceptance_criteria(
    business_requirement,
    approved_epic,
    approved_user_story,
    feedback=None,
    number_of_criteria=3
):

    feedback_text = ""

    if feedback:

        feedback_text = f"""
Previous Acceptance Criteria were rejected during validation.

VALIDATOR FEEDBACK:
{feedback}

Generate corrected Acceptance Criteria.

IMPORTANT:
- Do not repeat the rejected unsupported behavior.
- Preserve all behavior that is explicitly stated in the
  ORIGINAL BUSINESS REQUIREMENT.
- Do not remove an explicitly required business outcome.
- Generate fewer criteria if fewer are supported.
- Do not invent additional behavior.
"""

    prompt = f"""
You are an experienced Agile Business Analyst.

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
TASK
============================================================

Generate up to {number_of_criteria} DISTINCT Acceptance
Criteria for the approved User Story.

{number_of_criteria} is the MAXIMUM number.

It is NOT necessary to generate exactly {number_of_criteria}.

If only one valid Acceptance Criterion is supported,
generate one.

If two are supported, generate two.

NEVER invent additional behavior just to reach the maximum.


============================================================
ACCEPTANCE CRITERION FORMAT
============================================================

Every criterion MUST contain:

Given:
Initial condition.

When:
User action or event.

Then:
Expected business outcome.


============================================================
IMPORTANT TRACEABILITY RULE
============================================================

The ORIGINAL BUSINESS REQUIREMENT is the highest authority.

The Epic and User Story provide context, but they must NOT
introduce new business behavior.

An Acceptance Criterion is valid when its behavior is:

1. Explicitly stated in the Business Requirement, OR
2. A direct logical restatement of behavior explicitly stated
   in the Business Requirement.

Do NOT reject behavior merely because the BR does not use the
exact same wording.

For example:

If the BR says:
"the customer receives an order confirmation"

Then an AC saying:
"the customer receives an order confirmation"

is VALID.

Do NOT reject it as a "confirmation message" because the
confirmation itself is explicitly required by the BR.


============================================================
STRICT RULES
============================================================

1. The AC must directly validate the User Story.

2. The AC must logically belong to the Epic.

3. Every business behavior must be traceable to the
   ORIGINAL BUSINESS REQUIREMENT.

4. The User Story and Epic cannot introduce new requirements.

5. Do NOT infer missing requirements.

6. Do NOT use common industry practices as evidence.

7. Do NOT invent:

   - email sending
   - reset links
   - verification codes
   - OTP
   - security rules
   - expiration times
   - account verification
   - database behavior
   - APIs
   - backend implementation
   - technical architecture
   - UI screens
   - buttons
   - forms
   - technical error handling
   - unsupported error messages

8. However, if any of the above behavior is explicitly stated
   in the ORIGINAL BUSINESS REQUIREMENT, it IS allowed.

9. Do not create negative scenarios unless explicitly supported
   by the original requirement.

10. Do not create implementation details.

11. Do not generate IDs.

12. Do not generate duplicate or equivalent criteria.

13. Prefer fewer valid criteria rather than unsupported ones.

14. Do not expand the requirement.

15. Preserve explicitly stated business outcomes.

16. Every Given, When and Then statement must be traceable to
    the original Business Requirement.

17. Do not reject an AC simply because it uses different wording
    from the BR.

18. If the BR explicitly requires a confirmation, notification,
    order creation, payment processing, status update, etc.,
    that behavior is allowed.

19. Do not confuse a business outcome with an implementation
    detail.


{feedback_text}


============================================================
OUTPUT
============================================================

Return ONLY the structured Acceptance Criteria list.
"""


    schema = {

        "type": "object",

        "properties": {

            "acceptance_criteria": {

                "type": "array",

                "items": {

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
                },

                "minItems": 1,

                "maxItems": number_of_criteria
            }
        },

        "required": [
            "acceptance_criteria"
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

                "name": "acceptance_criteria_list",

                "schema": schema,

                "strict": True
            }
        },

        temperature=0
    )


    data = json.loads(
        response.choices[0].message.content
    )


    validated_criteria = []

    for item in data["acceptance_criteria"]:

        ac = AcceptanceCriteria.model_validate(item)

        validated_criteria.append(ac)


    return validated_criteria


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_acceptance_criteria(ac):

    errors = []

    if not ac.given.strip():

        errors.append(
            "Given is empty."
        )

    if not ac.when.strip():

        errors.append(
            "When is empty."
        )

    if not ac.then.strip():

        errors.append(
            "Then is empty."
        )

    if errors:

        return False, errors

    return True, []


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate_acceptance_criteria(
    ac,
    approved_criteria
):

    current = (

        ac.given.strip().lower(),

        ac.when.strip().lower(),

        ac.then.strip().lower()
    )

    for existing in approved_criteria:

        existing_tuple = (

            existing["given"]
            .strip()
            .lower(),

            existing["when"]
            .strip()
            .lower(),

            existing["then"]
            .strip()
            .lower()
        )

        if current == existing_tuple:

            return True

    return False


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
You are a STRICT but FAIR requirements traceability validator.

Your task is to determine whether the Acceptance Criterion is
supported by the ORIGINAL BUSINESS REQUIREMENT.


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
ACCEPTANCE CRITERION
============================================================

Given:
{ac.given}

When:
{ac.when}

Then:
{ac.then}


============================================================
VALIDATION PRINCIPLE
============================================================

The ORIGINAL BUSINESS REQUIREMENT is the source of truth.

The Acceptance Criterion is VALID if its behavior is:

- explicitly stated in the BR, OR
- a direct logical restatement of behavior explicitly stated
  in the BR.

The AC does NOT need to use exactly the same words as the BR.

Do NOT reject a criterion merely because it uses different
natural language wording.

IMPORTANT:

If the Business Requirement explicitly says that something
must happen, that behavior MUST be considered supported.

Example:

BR:
"After successful payment, an order is created and the
customer receives an order confirmation."

Valid AC:

Given: Payment has been successfully processed.
When: The payment process completes.
Then: An order is created and the customer receives an
order confirmation.

The confirmation is valid because it is explicitly stated
in the BR.


============================================================
STRICT VALIDATION RULES
============================================================

1. The AC must directly validate the User Story.

2. The AC must logically belong to the Epic.

3. Every business behavior must be supported by the
   ORIGINAL BUSINESS REQUIREMENT.

4. The User Story and Epic cannot introduce new requirements.

5. Do not infer missing requirements.

6. Do not use common industry practices as evidence.

7. Reject behavior that introduces unsupported:

   - email sending
   - reset links
   - verification codes
   - OTP
   - security requirements
   - expiration times
   - account verification
   - database behavior
   - APIs
   - technical implementation
   - backend architecture
   - UI screens
   - forms
   - buttons
   - technical error handling
   - unsupported error messages

8. BUT:

   If any of these behaviors are explicitly stated in the
   ORIGINAL BUSINESS REQUIREMENT, they are VALID.

9. Do not reject explicitly stated business outcomes.

10. Do not reject confirmation or notification behavior when
    the BR explicitly requires it.

11. Do not reject order creation when the BR explicitly
    requires order creation.

12. Do not reject payment processing when the BR explicitly
    requires payment processing.

13. Reject unsupported negative scenarios.

14. Reject unsupported workflows.

15. Reject implementation details that are not in the BR.

16. Reject unnecessary expansion.

17. If ANY genuinely unsupported business behavior exists,
    return FAIL.

18. If the entire AC is supported by the BR, return PASS.


============================================================
OUTPUT
============================================================

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
# GENERATE + VALIDATE ACCEPTANCE CRITERIA
# ============================================================

def generate_and_validate_acceptance_criteria(
    business_requirement,
    approved_epic,
    approved_user_story,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    user_story_id="US-001",
    number_of_criteria=3,
    max_attempts=3
):

    approved_criteria = []

    feedback = None


    # ========================================================
    # REGENERATION LOOP
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            f"\n===== AC GENERATION ATTEMPT "
            f"{attempt} ====="
        )


        # ====================================================
        # GENERATE
        # ====================================================

        try:

            generated_criteria = (
                generate_acceptance_criteria(

                    business_requirement,

                    approved_epic,

                    approved_user_story,

                    feedback,

                    number_of_criteria
                )
            )

        except Exception as error:

            print(
                "\n❌ AC GENERATION ERROR"
            )

            print(
                "Error:",
                error
            )

            feedback = (
                "Previous generation failed because "
                "of an LLM or structured-output error. "
                "Generate valid Acceptance Criteria."
            )

            continue


        print(
            f"\nGenerated "
            f"{len(generated_criteria)} "
            f"AC candidate(s)"
        )


        # ====================================================
        # CANDIDATE VALIDATION
        # ====================================================

        rejected_feedback = []


        for index, ac in enumerate(
            generated_criteria,
            start=1
        ):

            print(
                f"\n--- AC CANDIDATE {index} ---"
            )

            print(
                "Given:",
                ac.given
            )

            print(
                "When:",
                ac.when
            )

            print(
                "Then:",
                ac.then
            )


            # =================================================
            # PYTHON VALIDATION
            # =================================================

            valid, errors = (
                python_validate_acceptance_criteria(
                    ac
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
            # DUPLICATE VALIDATION
            # =================================================

            if is_duplicate_acceptance_criteria(
                ac,
                approved_criteria
            ):

                print(
                    "\nDUPLICATE CHECK: FAIL"
                )

                reason = (
                    "Equivalent Acceptance Criterion "
                    "already approved."
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
                    semantic_validate_acceptance_criteria(

                        business_requirement,

                        approved_epic,

                        approved_user_story,

                        ac
                    )
                )

            except Exception as error:

                print(
                    "\n❌ AC SEMANTIC "
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
            # APPROVE
            # =================================================

            if semantic_result.startswith(
                "PASS"
            ):

                approved_criteria.append(
                    {
                        "given":
                            ac.given,

                        "when":
                            ac.when,

                        "then":
                            ac.then,

                        "parent_story_id":
                            user_story_id,

                        "parent_epic_id":
                            epic_id,

                        "source_requirement_id":
                            business_requirement_id
                    }
                )


                print(
                    "\n✅ ACCEPTANCE CRITERIA "
                    "APPROVED"
                )

            else:

                print(
                    "\n❌ ACCEPTANCE CRITERIA "
                    "REJECTED"
                )

                rejected_feedback.append(
                    semantic_result
                )


        # ====================================================
        # SUCCESS CONDITION
        # ====================================================

        if approved_criteria:

            print(
                "\n✅ At least one valid "
                "Acceptance Criterion approved."
            )

            break


        # ====================================================
        # REGENERATION
        # ====================================================

        feedback = "\n".join(
            rejected_feedback
        )


        if not feedback:

            feedback = (
                "All Acceptance Criteria were rejected. "
                "Generate new criteria strictly grounded "
                "in the original Business Requirement."
            )


        if attempt < max_attempts:

            print(
                "\n🔄 Regeneration required."
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    if not approved_criteria:

        print(
            "\n❌ NO ACCEPTANCE CRITERIA APPROVED"
        )

        print(
            f"Maximum attempts reached: "
            f"{max_attempts}"
        )

        return []


    # ========================================================
    # ASSIGN IDs ONLY AFTER APPROVAL
    # ========================================================

    final_criteria = []


    for index, ac in enumerate(
        approved_criteria,
        start=1
    ):

        final_criteria.append(
            {
                "id":
                    f"AC-{index:03d}",

                "given":
                    ac["given"],

                "when":
                    ac["when"],

                "then":
                    ac["then"],

                "parent_story_id":
                    ac["parent_story_id"],

                "parent_epic_id":
                    ac["parent_epic_id"],

                "source_requirement_id":
                    ac["source_requirement_id"]
            }
        )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print(
        "\n========================================"
    )

    print(
        "APPROVED ACCEPTANCE CRITERIA"
    )

    print(
        "========================================"
    )


    for ac in final_criteria:

        print(
            f"\nID: {ac['id']}"
        )

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


    return final_criteria