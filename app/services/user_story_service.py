import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.user_story import UserStory

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_user_story_candidates(
    business_requirement,
    approved_epic,
    feedback=None
):

    feedback_text = ""

    if feedback:
        feedback_text = f"""
Previous User Story candidates failed validation.

Validator feedback:
{feedback}

Generate corrected User Stories.
Do not repeat the identified problems.
"""

    prompt = f"""
You are an experienced Agile Business Analyst.

Original Business Requirement:

{business_requirement}

Approved Epic:

Title: {approved_epic["title"]}
Description: {approved_epic["description"]}

Generate all DISTINCT User Stories required for this
approved Epic.

Rules:

1. Generate only genuinely distinct User Stories.

2. Do not create duplicate or artificially split stories.

3. Every Story must directly support the approved Epic.

4. Every Story must be supported by the original
   Business Requirement.

5. Do not introduce unsupported business behavior.

6. Do not assume common industry behavior.

7. Do not add:
   - security rules
   - validation rules
   - emails
   - reset links
   - verification codes
   - expiration times
   - APIs
   - databases
   - technical implementation details

8. Use:

   As a <user>, I want <goal>, so that <benefit>.

9. If one User Story is sufficient, return exactly one.

10. Do not generate IDs.

{feedback_text}

Return only the structured list.
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
        "required": ["user_stories"],
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

    data = json.loads(
        response.choices[0].message.content
    )

    return [
        UserStory.model_validate(story)
        for story in data["user_stories"]
    ]


def python_validate_user_story(user_story):

    errors = []

    if not user_story.title.strip():
        errors.append("User Story title is empty.")

    if not user_story.story.strip():
        errors.append("User Story is empty.")

    story_lower = user_story.story.lower()

    if "as a" not in story_lower:
        errors.append("Missing 'As a'.")

    if "i want" not in story_lower:
        errors.append("Missing 'I want'.")

    if "so that" not in story_lower:
        errors.append("Missing 'so that'.")

    if errors:
        return False, errors

    return True, []


def semantic_validate_user_story(
    business_requirement,
    approved_epic,
    user_story
):

    validation_prompt = f"""
You are a STRICT requirements traceability validator.

Original Business Requirement:

{business_requirement}

Approved Epic:

Title: {approved_epic["title"]}
Description: {approved_epic["description"]}

Candidate User Story:

Title:
{user_story.title}

Story:
{user_story.story}

Validate the User Story.

Rules:

1. The Story must directly support the approved Epic.

2. The Story must preserve the original business intent.

3. EVERY business behavior, condition, user goal,
   and business assumption in the Story must be
   supported by the Original Business Requirement.

4. Do not infer additional requirements.

5. Do not use common industry practices as evidence.

6. Reject unsupported:
   - forgotten-password scenarios
   - compromised-password scenarios
   - email sending
   - reset links
   - verification codes
   - security requirements
   - expiration times
   - account verification
   - additional workflows
   - APIs
   - databases
   - technical implementation

7. The Epic provides context but cannot add new
   business requirements that were not supported
   by the Original Business Requirement.

8. The Story must follow:

   As a <user>, I want <goal>, so that <benefit>.

If ANY unsupported business behavior exists,
return FAIL.

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


def is_duplicate_user_story(
    user_story,
    approved_stories
):

    new_title = user_story.title.strip().lower()
    new_story = user_story.story.strip().lower()

    for approved in approved_stories:

        if new_title == approved["title"].strip().lower():
            return True

        if new_story == approved["story"].strip().lower():
            return True

    return False


def generate_and_validate_user_stories(
    business_requirement,
    approved_epic,
    business_requirement_id="BR-001",
    epic_id="EPIC-001",
    max_attempts=3
):

    feedback = None
    approved_stories = []

    for attempt in range(1, max_attempts + 1):

        print(
            f"\n===== USER STORY GENERATION ATTEMPT "
            f"{attempt} ====="
        )

        try:

            candidates = generate_user_story_candidates(
                business_requirement,
                approved_epic,
                feedback
            )

        except Exception as error:

            print("\n❌ USER STORY GENERATION ERROR")
            print("Error:", error)

            feedback = (
                "User Story generation failed. "
                "Generate a valid structured list."
            )

            continue

        if not candidates:

            feedback = (
                "No User Stories were generated. "
                "At least one valid User Story is required."
            )

            print("\n❌ NO USER STORY CANDIDATES")

            continue

        print(
            f"\nGenerated {len(candidates)} "
            f"User Story candidate(s)"
        )

        rejected_feedback = []

        for index, story in enumerate(
            candidates,
            start=1
        ):

            print(
                f"\n--- CANDIDATE USER STORY {index} ---"
            )

            print("Title:", story.title)
            print("Story:", story.story)

            valid, errors = python_validate_user_story(
                story
            )

            if not valid:

                reason = "; ".join(errors)

                print(
                    "PYTHON VALIDATION: FAIL"
                )
                print("Reason:", reason)

                rejected_feedback.append(reason)

                continue

            print(
                "PYTHON VALIDATION: PASS"
            )

            if is_duplicate_user_story(
                story,
                approved_stories
            ):

                print(
                    "DUPLICATE CHECK: FAIL"
                )

                rejected_feedback.append(
                    f"Duplicate User Story: {story.title}"
                )

                continue

            print(
                "DUPLICATE CHECK: PASS"
            )

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
                    "❌ SEMANTIC VALIDATION ERROR"
                )
                print("Error:", error)

                rejected_feedback.append(
                    "Semantic validation failed."
                )

                continue

            print(
                "SEMANTIC VALIDATION:"
            )
            print(semantic_result)

            if semantic_result.startswith("PASS"):

                approved_stories.append(
                    {
                        "title": story.title,
                        "story": story.story
                    }
                )

                print("✅ USER STORY APPROVED")

            else:

                print("❌ USER STORY REJECTED")

                rejected_feedback.append(
                    semantic_result
                )

        if approved_stories:

            final_stories = []

            for index, story in enumerate(
                approved_stories,
                start=1
            ):

                final_stories.append(
                    {
                        "id": f"US-{index:03d}",
                        "title": story["title"],
                        "story": story["story"],
                        "parent_epic_id": epic_id,
                        "source_requirement_id":
                            business_requirement_id
                    }
                )

            print(
                "\n========================================"
            )
            print("APPROVED USER STORIES")
            print(
                "========================================"
            )

            for story in final_stories:

                print(
                    f'{story["id"]}: '
                    f'{story["title"]}'
                )

            return final_stories

        feedback = "\n".join(
            rejected_feedback
        )

        print(
            "\n❌ NO USER STORIES APPROVED"
        )

        print(
            "🔄 Regeneration required."
        )

    print(
        "\n❌ USER STORY GENERATION FAILED"
    )

    print(
        "Maximum attempts reached."
    )

    return []