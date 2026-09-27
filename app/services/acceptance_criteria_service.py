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
# HELPER
# ============================================================

def safe_text(value):
    """
    Safely convert any value to clean text.
    """

    if value is None:
        return ""

    return str(value).strip()


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
    """
    Generate Acceptance Criteria candidates.

    Maximum number of criteria is controlled by
    number_of_criteria.
    """

    # --------------------------------------------------------
    # Feedback
    # --------------------------------------------------------

    feedback_text = ""

    if feedback:

        feedback_text = f"""
============================================================
PREVIOUS VALIDATION FEEDBACK
============================================================

The previous Acceptance Criteria were rejected.

Fix ONLY the problems identified below.

{feedback}

IMPORTANT:
- Do not repeat rejected behavior.
- Do not invent new requirements.
- Preserve explicitly stated business behavior.
- Generate fewer criteria if fewer are supported.
- Do not force the maximum number.
"""


    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are an experienced Agile Business Analyst.

Your task is to generate Acceptance Criteria for ONE
approved User Story.

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

Generate UP TO {number_of_criteria} distinct Acceptance
Criteria for the approved User Story.

{number_of_criteria} is the MAXIMUM.

You do NOT need to generate exactly {number_of_criteria}.

If only one valid criterion is supported, generate one.

If two valid criteria are supported, generate two.

NEVER invent behavior simply to reach the maximum.

============================================================
ACCEPTANCE CRITERION FORMAT
============================================================

Each Acceptance Criterion MUST contain:

Given:
Initial business condition.

When:
Business action or event.

Then:
Expected business outcome.

============================================================
TRACEABILITY
============================================================

The ORIGINAL BUSINESS REQUIREMENT is the ultimate
source of truth.

The Epic and User Story provide context only.

They MUST NOT introduce new business behavior.

Every business behavior in the Acceptance Criterion
must be:

1. Explicitly stated in the Business Requirement, OR
2. A direct logical restatement of behavior explicitly
   stated in the Business Requirement.

Different wording is allowed.

Do NOT reject valid behavior merely because the wording
differs from the Business Requirement.

============================================================
STRICT RULES
============================================================

1. Every AC must directly validate the User Story.

2. Every AC must logically belong to the Epic.

3. Every business behavior must be traceable to the
   Original Business Requirement.

4. Do NOT infer missing requirements.

5. Do NOT use common industry practices as evidence.

6. Do NOT invent:

   - email sending
   - reset links
   - verification codes
   - OTP
   - security requirements
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

7. If any of the above behavior is explicitly stated in
   the Original Business Requirement, it IS allowed.

8. Do not create unsupported negative scenarios.

9. Do not create implementation details.

10. Do not generate IDs.

11. Do not generate duplicate or equivalent criteria.

12. Prefer fewer valid criteria over unsupported criteria.

13. Do not expand the requirement.

14. Preserve explicitly stated business outcomes.

15. Every Given, When and Then statement must be
    traceable to the Business Requirement.

16. Do not reject an AC merely because it uses different
    natural language.

17. If the Business Requirement explicitly requires:

    - confirmation
    - notification
    - order creation
    - payment processing
    - status update
    - delivery update

    then that behavior is allowed.

18. The Acceptance Criterion must describe a BUSINESS
    OUTCOME, not a technical implementation.

{feedback_text}

============================================================
OUTPUT
============================================================

Return ONLY the structured Acceptance Criteria list.
"""


    # --------------------------------------------------------
    # JSON Schema
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # LLM CALL
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SAFE RESPONSE HANDLING
    # --------------------------------------------------------

    if not response:

        raise ValueError(
            "LLM returned no response."
        )


    if not response.choices:

        raise ValueError(
            "LLM returned no choices."
        )


    message = response.choices[0].message

    content = message.content


    if not content:

        raise ValueError(
            "LLM returned an empty Acceptance Criteria response."
        )


    # --------------------------------------------------------
    # JSON PARSING
    # --------------------------------------------------------

    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by LLM: {error}"
        )


    if not isinstance(data, dict):

        raise ValueError(
            "LLM response is not a JSON object."
        )


    if "acceptance_criteria" not in data:

        raise ValueError(
            "LLM response does not contain "
            "'acceptance_criteria'."
        )


    if not data["acceptance_criteria"]:

        raise ValueError(
            "LLM returned an empty Acceptance Criteria list."
        )


    # --------------------------------------------------------
    # PYDANTIC VALIDATION
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Given
    # --------------------------------------------------------

    if not safe_text(ac.given):

        errors.append(
            "Given is empty."
        )


    # --------------------------------------------------------
    # When
    # --------------------------------------------------------

    if not safe_text(ac.when):

        errors.append(
            "When is empty."
        )


    # --------------------------------------------------------
    # Then
    # --------------------------------------------------------

    if not safe_text(ac.then):

        errors.append(
            "Then is empty."
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

def is_duplicate_acceptance_criteria(
    ac,
    approved_criteria
):

    current = (

        safe_text(ac.given).lower(),

        safe_text(ac.when).lower(),

        safe_text(ac.then).lower()
    )


    for existing in approved_criteria:

        existing_tuple = (

            safe_text(
                existing["given"]
            ).lower(),

            safe_text(
                existing["when"]
            ).lower(),

            safe_text(
                existing["then"]
            ).lower()
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
    """
    LLM-based semantic traceability validation.

    Returns:

        PASS

    OR

        FAIL: reason
    """

    validation_prompt = f"""
You are a STRICT but FAIR SDLC requirements
traceability validator.

Your task is to determine whether the Acceptance
Criterion is supported by the ORIGINAL BUSINESS
REQUIREMENT.

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
- a direct logical restatement of behavior explicitly
  stated in the BR.

The AC does NOT need to use exactly the same words
as the BR.

Do NOT reject a valid criterion merely because it uses
different natural language.

============================================================
STRICT RULES
============================================================

1. The AC must directly validate the User Story.

2. The AC must logically belong to the Epic.

3. Every business behavior must be supported by the
   Original Business Requirement.

4. The User Story and Epic cannot introduce new
   requirements.

5. Do not infer missing requirements.

6. Do not use common industry practices as evidence.

7. Reject unsupported:

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

8. HOWEVER, if any such behavior is explicitly stated
   in the Original Business Requirement, it is VALID.

9. Do not reject explicitly stated business outcomes.

10. Do not reject explicitly stated notifications.

11. Do not reject explicitly stated confirmations.

12. Do not reject explicitly stated order creation.

13. Do not reject explicitly stated payment processing.

14. Reject unsupported negative scenarios.

15. Reject unsupported workflows.

16. Reject unnecessary expansion.

17. If ANY genuinely unsupported business behavior
    exists, return FAIL.

18. If the entire AC is supported, return PASS.

============================================================
OUTPUT
============================================================

Return EXACTLY one of:

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


    # --------------------------------------------------------
    # SAFE RESPONSE HANDLING
    # --------------------------------------------------------

    if not response:

        return (
            "FAIL: Semantic validator returned no response."
        )


    if not response.choices:

        return (
            "FAIL: Semantic validator returned no choices."
        )


    result = response.choices[0].message.content


    # --------------------------------------------------------
    # IMPORTANT FIX
    # --------------------------------------------------------
    #
    # Previously an empty response was returned as:
    #
    # FAIL: Semantic validator returned an empty response.
    #
    # This makes the candidate fail, but does not provide
    # useful regeneration feedback.
    #
    # Now we return a clean failure message.
    #

    if not result:

        return (
            "FAIL: Semantic validation produced no result. "
            "Regenerate the Acceptance Criterion and keep "
            "it strictly grounded in the Business Requirement."
        )


    result = result.strip()


    if not result:

        return (
            "FAIL: Semantic validation produced an empty result. "
            "Regenerate the Acceptance Criterion."
        )


    return result


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
    max_attempts=5
):
    """
    Generate and validate Acceptance Criteria.

    IMPORTANT:

    Default maximum attempts = 5.

    The function always returns a list.

    Successful result:
        [
            {
                "id": "AC-001",
                ...
            }
        ]

    Failure:
        []
    """


    # ========================================================
    # SAFETY
    # ========================================================

    if max_attempts < 1:

        max_attempts = 1


    if number_of_criteria < 1:

        number_of_criteria = 1


    # ========================================================
    # APPROVED CRITERIA
    # ========================================================

    approved_criteria = []


    # ========================================================
    # FEEDBACK
    # ========================================================

    feedback = None


    # ========================================================
    # ATTEMPT LOOP
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
            f"AC GENERATION ATTEMPT "
            f"{attempt}/{max_attempts}"
        )

        print(
            "=" * 70
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


            # -----------------------------------------------
            # IMPORTANT
            # -----------------------------------------------
            #
            # Do NOT immediately stop.
            #
            # Give the next attempt a clean instruction.
            #

            feedback = (
                "The previous Acceptance Criteria generation "
                "failed because the LLM response was invalid, "
                "empty, or malformed.\n\n"
                "Generate a valid structured Acceptance "
                "Criteria list.\n"
                "Do not invent requirements."
            )


            if attempt < max_attempts:

                print(
                    f"\n🔄 Regenerating..."
                )

                print(
                    f"Next attempt: "
                    f"{attempt + 1}/{max_attempts}"
                )

                continue


            break


        # ====================================================
        # EMPTY GENERATION
        # ====================================================

        if not generated_criteria:

            print(
                "\n❌ NO AC CANDIDATES GENERATED"
            )


            feedback = (
                "No Acceptance Criteria were generated.\n"
                "Generate at least one valid Acceptance "
                "Criterion grounded in the Business Requirement."
            )


            if attempt < max_attempts:

                print(
                    "\n🔄 Regeneration required."
                )

                continue


            break


        print(
            f"\nGenerated "
            f"{len(generated_criteria)} "
            f"AC candidate(s)"
        )


        # ====================================================
        # REJECTED FEEDBACK
        # ====================================================

        rejected_feedback = []


        # ====================================================
        # VALIDATE EACH AC
        # ====================================================

        for index, ac in enumerate(
            generated_criteria,
            start=1
        ):

            print(
                "\n"
                + "-" * 60
            )

            print(
                f"AC CANDIDATE {index}"
            )

            print(
                "-" * 60
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
            # DUPLICATE CHECK
            # =================================================

            if is_duplicate_acceptance_criteria(
                ac,
                approved_criteria
            ):

                reason = (
                    "Equivalent Acceptance Criterion "
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

                # ---------------------------------------------
                # Store ONLY validated data
                # ---------------------------------------------

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
                    "\n✅ ACCEPTANCE CRITERION APPROVED"
                )


            else:

                print(
                    "\n❌ ACCEPTANCE CRITERION REJECTED"
                )


                rejected_feedback.append(
                    semantic_result
                )


        # ====================================================
        # SUCCESS CONDITION
        # ====================================================

        if approved_criteria:

            print(
                "\n"
                + "=" * 70
            )

            print(
                "✅ AC GENERATION SUCCESSFUL"
            )

            print(
                f"Approved Criteria: "
                f"{len(approved_criteria)}"
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
        # NO APPROVED CRITERIA
        # ====================================================

        print(
            "\n❌ NO ACCEPTANCE CRITERIA APPROVED "
            f"ON ATTEMPT {attempt}"
        )


        # ====================================================
        # BUILD FEEDBACK
        # ====================================================

        if rejected_feedback:

            # Limit feedback size so that regeneration
            # does not unnecessarily make the next prompt huge.

            feedback = "\n".join(
                rejected_feedback[:10]
            )


        else:

            feedback = (
                "All generated Acceptance Criteria were "
                "rejected.\n"
                "Generate new criteria strictly grounded "
                "in the Original Business Requirement."
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
                "\n⛔ MAXIMUM AC ATTEMPTS REACHED"
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    if not approved_criteria:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "❌ ACCEPTANCE CRITERIA GENERATION FAILED"
        )

        print(
            f"Maximum attempts reached: "
            f"{max_attempts}"
        )

        print(
            "=" * 70
        )


        # IMPORTANT:
        # Always return list.
        return []


    # ========================================================
    # ASSIGN IDs AFTER VALIDATION
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
        "\n"
        + "=" * 70
    )

    print(
        "APPROVED ACCEPTANCE CRITERIA"
    )

    print(
        "=" * 70
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