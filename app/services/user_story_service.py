import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.user_story import UserStory


# ============================================================
# ENVIRONMENT / CLIENT
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_VALIDATOR_RETRIES = 3


# ============================================================
# USER STORY CANDIDATE GENERATION
# ============================================================

def generate_user_story_candidates(
    business_requirement,
    approved_epic,
    feedback=None
):
    """
    Generate distinct User Story candidates for ONE approved Epic.

    Returns:
        list[UserStory]
    """

    feedback_text = ""

    if feedback:

        feedback_text = f"""
Previous User Story candidates had validation problems.

VALIDATOR FEEDBACK:
{feedback}

Generate corrected User Stories.

IMPORTANT:
- Fix only the identified problems.
- Do not introduce new business requirements.
- Do not repeat unsupported behavior.
- Preserve behavior explicitly supported by the
  Original Business Requirement.
- If only one User Story is supported, generate one.
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
TASK
============================================================

Generate all DISTINCT User Stories required for this
approved Epic.


============================================================
STRICT RULES
============================================================

1. Generate only genuinely distinct User Stories.

2. Do not create duplicate User Stories.

3. Do not artificially split one simple capability.

4. Every User Story must directly support the approved Epic.

5. Every User Story must be supported by the ORIGINAL
   Business Requirement.

6. The Epic cannot introduce business behavior that is
   not supported by the Original Business Requirement.

7. Do not infer missing requirements.

8. Do not use common industry practices as evidence.

9. Do not add unsupported:

   - security rules
   - validation rules
   - emails
   - reset links
   - verification codes
   - OTP
   - expiration times
   - account verification
   - notifications
   - additional workflows
   - APIs
   - databases
   - backend implementation
   - frontend implementation
   - technical architecture

10. Use exactly this Agile format:

    As a <user>, I want <goal>, so that <benefit>.

11. The User Story must describe a business goal,
    not technical implementation.

12. If the Epic requires only one User Story,
    generate exactly one.

13. If the Epic genuinely requires multiple distinct
    User Stories, generate all supported stories.

14. Do not generate IDs.

15. Do not add explanations outside the structured output.

16. Do not create a User Story only to increase the count.

17. Prefer fewer valid User Stories over unsupported ones.

18. Different wording is allowed when the business meaning
    remains supported by the Original Business Requirement.

19. Preserve explicitly stated business outcomes.

20. Do not introduce new behavior through the "so that"
    portion of the User Story.

{feedback_text}


============================================================
OUTPUT
============================================================

Return only the structured User Story list.
"""


    schema = {

        "type": "object",

        "properties": {

            "user_stories": {

                "type": "array",

                "items": {

                    "type": "object",

                    "properties": {

                        "title": {
                            "type": "string"
                        },

                        "story": {
                            "type": "string"
                        }
                    },

                    "required": [
                        "title",
                        "story"
                    ],

                    "additionalProperties": False
                }
            }
        },

        "required": [
            "user_stories"
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

                "name": "multiple_user_stories",

                "schema": schema,

                "strict": True
            }
        },

        temperature=0,

        max_tokens=2000
    )


    content = response.choices[0].message.content


    if not content:

        raise ValueError(
            "LLM returned empty User Story response."
        )


    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Invalid JSON returned by User Story generator: "
            f"{error}"
        )


    if "user_stories" not in data:

        raise ValueError(
            "LLM response does not contain 'user_stories'."
        )


    validated_stories = []


    for story in data["user_stories"]:

        validated_stories.append(
            UserStory.model_validate(story)
        )


    return validated_stories


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_user_story(user_story):
    """
    Basic deterministic validation.

    Returns:
        (bool, list[str])
    """

    errors = []


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    if not user_story.title.strip():

        errors.append(
            "User Story title is empty."
        )


    # --------------------------------------------------------
    # Story
    # --------------------------------------------------------

    if not user_story.story.strip():

        errors.append(
            "User Story is empty."
        )

    else:

        story_lower = (
            user_story.story
            .strip()
            .lower()
        )


        if "as a" not in story_lower:

            errors.append(
                "Missing 'As a'."
            )


        if "i want" not in story_lower:

            errors.append(
                "Missing 'I want'."
            )


        if "so that" not in story_lower:

            errors.append(
                "Missing 'so that'."
            )


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    if errors:

        return False, errors


    return True, []


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def is_duplicate_user_story(
    user_story,
    approved_stories
):
    """
    Detect exact duplicate title or story.

    Returns:
        True  -> duplicate
        False -> unique
    """

    new_title = (
        user_story.title
        .strip()
        .lower()
    )


    new_story = (
        user_story.story
        .strip()
        .lower()
    )


    for approved in approved_stories:

        existing_title = (
            approved["title"]
            .strip()
            .lower()
        )


        existing_story = (
            approved["story"]
            .strip()
            .lower()
        )


        # Exact title match
        if new_title == existing_title:

            return True


        # Exact story match
        if new_story == existing_story:

            return True


    return False


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_user_story(
    business_requirement,
    approved_epic,
    user_story,
    validator_retries=DEFAULT_VALIDATOR_RETRIES
):
    """
    LLM-based semantic traceability validation.

    IMPORTANT:

    An empty response from the semantic validator is NOT
    treated as a business rejection.

    The validator itself is retried.

    Returns:
        PASS
        OR
        FAIL: reason

    Raises:
        RuntimeError if the validator cannot provide a valid
        response after all validator retries.
    """


    validation_prompt = f"""
You are a STRICT but FAIR requirements traceability validator.


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
CANDIDATE USER STORY
============================================================

Title:
{user_story.title}

Story:
{user_story.story}


============================================================
VALIDATION PRINCIPLE
============================================================

The ORIGINAL BUSINESS REQUIREMENT is the highest authority.

The User Story is VALID when:

1. It directly supports the approved Epic.

2. Its business intent is supported by the Original
   Business Requirement.

3. Every business behavior in the User Story is supported
   by the Original Business Requirement.

4. It does not introduce a new business requirement.

5. It follows:

   As a <user>, I want <goal>, so that <benefit>.


============================================================
IMPORTANT
============================================================

Do NOT require exact wording.

Different natural language wording is acceptable when
the business meaning is supported.

For example:

Business Requirement:
"Customers can search the product catalog."

User Story:
"As a customer, I want to search the product catalog,
so that I can find products I need."

This is VALID because the business behavior is supported.


============================================================
STRICT RULES
============================================================

Reject unsupported:

- security requirements
- emails
- reset links
- verification codes
- OTP
- expiration times
- account verification
- notifications
- additional workflows
- APIs
- databases
- backend implementation
- frontend implementation
- technical architecture
- infrastructure behavior

However:

If a behavior is explicitly stated in the ORIGINAL
BUSINESS REQUIREMENT, it IS allowed.

Do not reject an explicitly stated business outcome.

Do not infer missing requirements.

Do not use common industry practices as evidence.

Do not reject merely because the wording is different.

Focus on business semantics and traceability.


============================================================
OUTPUT
============================================================

Return EXACTLY one of the following:

PASS

OR

FAIL: <specific unsupported business behavior and reason>

Do not return anything else.
"""


    last_error = None


    # ========================================================
    # VALIDATOR RETRY LOOP
    # ========================================================

    for retry in range(
        1,
        validator_retries + 1
    ):

        print(
            f"\nSemantic validator attempt "
            f"{retry}/{validator_retries}"
        )


        try:

            response = client.chat.completions.create(

                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "user",
                        "content": validation_prompt
                    }
                ],

                temperature=0,

                max_tokens=300
            )


            # ------------------------------------------------
            # SAFE RESPONSE EXTRACTION
            # ------------------------------------------------

            if not response.choices:

                last_error = (
                    "Semantic validator returned "
                    "no choices."
                )

                print(
                    f"⚠️ {last_error}"
                )

                continue


            message = response.choices[0].message


            result = message.content


            # ------------------------------------------------
            # EMPTY RESPONSE
            # ------------------------------------------------

            if not result or not result.strip():

                last_error = (
                    "Semantic validator returned "
                    "an empty response."
                )

                print(
                    f"⚠️ {last_error}"
                )

                continue


            result = result.strip()


            # ------------------------------------------------
            # VALID PASS
            # ------------------------------------------------

            if result == "PASS":

                return "PASS"


            # ------------------------------------------------
            # VALID FAIL
            # ------------------------------------------------

            if result.startswith("FAIL:"):

                return result


            # ------------------------------------------------
            # HANDLE UNEXPECTED OUTPUT
            # ------------------------------------------------

            last_error = (
                "Unexpected semantic validator output: "
                f"{result}"
            )

            print(
                f"⚠️ {last_error}"
            )


        except Exception as error:

            last_error = str(error)

            print(
                "\n⚠️ Semantic validator exception:"
            )

            print(
                error
            )


    # ========================================================
    # VALIDATOR FAILED
    # ========================================================

    raise RuntimeError(
        "Semantic validator failed after "
        f"{validator_retries} retries. "
        f"Last error: {last_error}"
    )


# ============================================================
# USER STORY PIPELINE
# ============================================================

def generate_and_validate_user_stories(
    business_requirement,
    approved_epic,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    max_attempts=DEFAULT_MAX_ATTEMPTS,
    validator_retries=DEFAULT_VALIDATOR_RETRIES
):
    """
    Generate, validate and return User Stories
    for ONE approved Epic.

    IMPORTANT:

    max_attempts controls User Story regeneration.

    validator_retries controls retries of the semantic
    validator itself.

    These are intentionally separate.

    Example:

        max_attempts = 5
        validator_retries = 3

    Means:

        Up to 5 User Story generation attempts.

        Each semantic validation can independently retry
        up to 3 times.

    Returns:

        list[dict]
    """


    feedback = None


    approved_stories = []


    generation_errors = []


    semantic_validation_errors = []


    # ========================================================
    # MAX ATTEMPTS PROTECTION
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):


        print(
            "\n========================================================"
        )

        print(
            f"USER STORY GENERATION ATTEMPT "
            f"{attempt}/{max_attempts}"
        )

        print(
            "========================================================"
        )


        # ====================================================
        # GENERATE CANDIDATES
        # ====================================================

        try:

            candidates = (
                generate_user_story_candidates(

                    business_requirement,

                    approved_epic,

                    feedback
                )
            )


        except Exception as error:

            print(
                "\n❌ USER STORY GENERATION ERROR"
            )

            print(
                "Error:",
                error
            )


            generation_errors.append(
                str(error)
            )


            feedback = (
                "Previous User Story generation failed "
                "because of an LLM or structured-output "
                "problem. Generate a valid structured "
                "User Story list."
            )


            if attempt < max_attempts:

                print(
                    "\n🔄 Regeneration required."
                )

            continue


        # ====================================================
        # EMPTY RESULT
        # ====================================================

        if not candidates:

            print(
                "\n❌ NO USER STORY CANDIDATES"
            )


            feedback = (
                "No User Stories were generated. "
                "Generate at least one valid User Story "
                "for the approved Epic."
            )


            if attempt < max_attempts:

                print(
                    "\n🔄 Regeneration required."
                )

            continue


        print(
            f"\nGenerated {len(candidates)} "
            f"User Story candidate(s)"
        )


        # ====================================================
        # REJECTION FEEDBACK
        # ====================================================

        rejected_feedback = []


        # ====================================================
        # VALIDATE EACH CANDIDATE
        # ====================================================

        for index, story in enumerate(
            candidates,
            start=1
        ):


            print(
                f"\n--- CANDIDATE USER STORY {index} ---"
            )


            print(
                "Title:",
                story.title
            )


            print(
                "Story:",
                story.story
            )


            # =================================================
            # PYTHON VALIDATION
            # =================================================

            valid, errors = (
                python_validate_user_story(
                    story
                )
            )


            if not valid:

                reason = "; ".join(
                    errors
                )


                print(
                    "PYTHON VALIDATION: FAIL"
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
                "PYTHON VALIDATION: PASS"
            )


            # =================================================
            # DUPLICATE VALIDATION
            # =================================================

            if is_duplicate_user_story(
                story,
                approved_stories
            ):


                print(
                    "DUPLICATE CHECK: FAIL"
                )


                reason = (
                    f"Duplicate User Story: "
                    f"{story.title}"
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
                "DUPLICATE CHECK: PASS"
            )


            # =================================================
            # SEMANTIC VALIDATION
            # =================================================

            try:

                semantic_result = (
                    semantic_validate_user_story(

                        business_requirement,

                        approved_epic,

                        story,

                        validator_retries
                    )
                )


            except Exception as error:

                print(
                    "\n⚠️ SEMANTIC VALIDATION "
                    "COULD NOT COMPLETE"
                )


                print(
                    "Error:",
                    error
                )


                semantic_validation_errors.append(
                    str(error)
                )


                # IMPORTANT:
                #
                # Do NOT add this to rejected_feedback.
                #
                # The User Story was not proven invalid.
                # The validator itself failed.
                #
                continue


            print(
                "SEMANTIC VALIDATION:"
            )


            print(
                semantic_result
            )


            # =================================================
            # APPROVAL
            # =================================================

            if semantic_result == "PASS":


                approved_stories.append(
                    {
                        "title":
                            story.title,

                        "story":
                            story.story
                    }
                )


                print(
                    "✅ USER STORY APPROVED"
                )


            else:


                print(
                    "❌ USER STORY REJECTED"
                )


                rejected_feedback.append(
                    semantic_result
                )


        # ====================================================
        # APPROVED STORIES FOUND
        # ====================================================

        if approved_stories:


            final_stories = []


            # ------------------------------------------------
            # Assign IDs ONLY after validation
            # ------------------------------------------------

            for index, story in enumerate(
                approved_stories,
                start=1
            ):


                final_stories.append(
                    {
                        "id":
                            f"US-{index:03d}",

                        "title":
                            story["title"],

                        "story":
                            story["story"],

                        "parent_epic_id":
                            epic_id,

                        "source_requirement_id":
                            business_requirement_id
                    }
                )


            # ------------------------------------------------
            # Print approved stories
            # ------------------------------------------------

            print(
                "\n========================================"
            )


            print(
                "APPROVED USER STORIES"
            )


            print(
                "========================================"
            )


            for story in final_stories:

                print(
                    f'{story["id"]}: '
                    f'{story["title"]}'
                )

                print(
                    f'Story: '
                    f'{story["story"]}'
                )

                print(
                    f'Parent Epic: '
                    f'{story["parent_epic_id"]}'
                )

                print(
                    f'Source Requirement: '
                    f'{story["source_requirement_id"]}'
                )


            # ------------------------------------------------
            # ALWAYS RETURN LIST
            # ------------------------------------------------

            return final_stories


        # ====================================================
        # NO STORIES APPROVED
        # ====================================================

        # ----------------------------------------------------
        # If semantic validation itself failed, don't claim
        # that the User Stories were semantically rejected.
        # ----------------------------------------------------

        if semantic_validation_errors:

            print(
                "\n⚠️ Semantic validation did not "
                "complete successfully."
            )

            print(
                "The generated User Stories were "
                "NOT automatically marked invalid."
            )


        # ====================================================
        # PREPARE REGENERATION FEEDBACK
        # ====================================================

        if rejected_feedback:

            # Limit feedback size so it does not grow
            # excessively for large requirements.

            feedback = "\n".join(
                rejected_feedback[:10]
            )


        else:

            feedback = (
                "No User Stories passed validation. "
                "Generate corrected User Stories strictly "
                "grounded in the Original Business Requirement."
            )


        # ====================================================
        # REGENERATION
        # ====================================================

        if attempt < max_attempts:

            print(
                "\n🔄 Regeneration required."
            )

            print(
                f"Next attempt: "
                f"{attempt + 1}/{max_attempts}"
            )

        else:

            print(
                "\n⛔ Maximum User Story attempts reached."
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    print(
        "\n❌ USER STORY GENERATION FAILED"
    )


    print(
        f"Maximum attempts reached: "
        f"{max_attempts}"
    )


    # --------------------------------------------------------
    # More useful diagnostic
    # --------------------------------------------------------

    if semantic_validation_errors:

        print(
            "\n⚠️ IMPORTANT:"
        )

        print(
            "The semantic validator failed during "
            "validation."
        )

        print(
            "This does NOT necessarily mean the "
            "User Story was invalid."
        )


    if generation_errors:

        print(
            "\n⚠️ Generation errors encountered:"
        )

        for error in generation_errors[-3:]:

            print(
                "-",
                error
            )


    # IMPORTANT:
    # Always return an empty LIST, never None.

    return []