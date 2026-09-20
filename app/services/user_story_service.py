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
# USER STORY CANDIDATE GENERATION
# ============================================================

def generate_user_story_candidates(
    business_requirement,
    approved_epic,
    feedback=None
):
    """
    Generate all distinct User Stories for ONE approved Epic.

    Returns:
        list[UserStory]
    """

    feedback_text = ""

    if feedback:
        feedback_text = f"""
Previous User Story candidates failed validation.

Validator feedback:
{feedback}

Generate corrected User Stories.

Important:
- Fix the specific problems identified above.
- Do not repeat unsupported business behavior.
- Do not introduce new requirements.
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

6. The Epic cannot introduce a business behavior that
   is not supported by the Original Business Requirement.

7. Do not infer missing requirements.

8. Do not use common industry practices as evidence.

9. Do not add unsupported:
   - security rules
   - validation rules
   - emails
   - reset links
   - verification codes
   - expiration times
   - account verification
   - notifications
   - additional workflows
   - APIs
   - databases
   - technical implementation details

10. Use the exact Agile format:

    As a <user>, I want <goal>, so that <benefit>.

11. The User Story should describe a business goal,
    not technical implementation.

12. If the Epic requires only one User Story,
    generate exactly one.

13. If the Epic genuinely requires multiple distinct
    User Stories, generate all of them.

14. Do not generate IDs.

15. Do not add explanations outside the structured output.

{feedback_text}


============================================================
OUTPUT
============================================================

Return only the structured list of User Stories.
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

        temperature=0
    )


    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned empty User Story response."
        )


    data = json.loads(content)


    if "user_stories" not in data:
        raise ValueError(
            "LLM response does not contain 'user_stories'."
        )


    return [
        UserStory.model_validate(story)
        for story in data["user_stories"]
    ]


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
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_user_story(
    business_requirement,
    approved_epic,
    user_story
):
    """
    LLM-based semantic traceability validation.

    Returns:
        PASS
        OR
        FAIL: reason
    """

    validation_prompt = f"""
You are a STRICT requirements traceability validator.


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
VALIDATION RULES
============================================================

1. The User Story must directly support the approved Epic.

2. The User Story must preserve the original business intent.

3. EVERY business behavior in the User Story must be
   supported by the ORIGINAL Business Requirement.

4. Do not infer missing requirements.

5. Do not use common industry practices as evidence.

6. Reject unsupported:
   - security requirements
   - email behavior
   - reset links
   - verification codes
   - expiration times
   - account verification
   - notifications
   - additional workflows
   - APIs
   - databases
   - technical implementation

7. Do not allow the Epic to introduce a requirement that
   is not present in the Original Business Requirement.

8. The User Story must describe a business capability.

9. The User Story must follow:

   As a <user>, I want <goal>, so that <benefit>.

10. Do not reject a User Story merely because it uses
    different wording from the requirement.

11. Focus on BUSINESS SEMANTICS, not exact wording.

12. If the original requirement explicitly supports a
    concept such as password recovery, regaining access,
    defining a new password, or another business behavior,
    that concept may be used.

13. If a behavior is NOT supported by the requirement,
    reject it.

If ANY unsupported business behavior exists,
return FAIL.


============================================================
OUTPUT FORMAT
============================================================

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

        return (
            "FAIL: Semantic validator returned empty response."
        )


    return result.strip()


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
# USER STORY PIPELINE
# ============================================================

def generate_and_validate_user_stories(
    business_requirement,
    approved_epic,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    max_attempts=3
):
    """
    Generate, validate and return User Stories
    for ONE approved Epic.

    Important:
        This function ALWAYS returns a list.

    Example:

        [
            {
                "id": "US-001",
                "title": "...",
                "story": "...",
                "parent_epic_id": "EPIC-001",
                "source_requirement_id": "BR-001"
            }
        ]
    """


    feedback = None

    approved_stories = []


    # ========================================================
    # MAX ATTEMPTS PROTECTION
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):


        print(
            f"\n===== USER STORY GENERATION ATTEMPT "
            f"{attempt} ====="
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


            feedback = (
                "User Story generation failed. "
                "Return a valid structured list."
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
                        story
                    )
                )


            except Exception as error:

                print(
                    "\n❌ SEMANTIC VALIDATION ERROR"
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
                "SEMANTIC VALIDATION:"
            )


            print(
                semantic_result
            )


            # =================================================
            # APPROVAL
            # =================================================

            if semantic_result.startswith(
                "PASS"
            ):


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
            # Assign IDs only after validation
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


            # ------------------------------------------------
            # IMPORTANT:
            # ALWAYS RETURN LIST
            # ------------------------------------------------

            return final_stories


        # ====================================================
        # NO STORIES APPROVED
        # ====================================================

        feedback = "\n".join(
            rejected_feedback
        )


        if not feedback:

            feedback = (
                "No User Stories passed validation. "
                "Generate corrected User Stories."
            )


        print(
            "\n❌ NO USER STORIES APPROVED"
        )


        # ====================================================
        # REGENERATION
        # ====================================================

        if attempt < max_attempts:

            print(
                "🔄 Regeneration required."
            )

        else:

            print(
                "⛔ Maximum User Story attempts reached."
            )


    # ========================================================
    # FINAL FAILURE
    # ========================================================

    print(
        "\n❌ USER STORY GENERATION FAILED"
    )


    print(
        "Maximum attempts reached."
    )


    # IMPORTANT:
    # Return empty LIST, not None
    return []