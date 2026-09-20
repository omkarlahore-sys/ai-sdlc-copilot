import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.models.epic import Epic


# ============================================================
# ENVIRONMENT / CLIENT
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# EPIC GENERATION
# ============================================================

def generate_epic_candidates(
    business_requirement,
    feedback=None
):
    """
    Generate one or more Epic candidates from a Business
    Requirement.

    Returns:
        list[Epic]
    """

    feedback_text = ""

    if feedback:
        feedback_text = f"""
Previous Epic candidates failed validation.

Validator feedback:
{feedback}

Generate corrected Epic candidates.

Do not repeat the unsupported behavior identified
in the validator feedback.
"""

    prompt = f"""
You are an experienced Business Analyst.

Analyze the following Business Requirement:

{business_requirement}

Generate all DISTINCT business Epics required
to represent the requirement.

Rules:

1. Generate only genuinely distinct business capabilities.

2. Do not split one simple capability into artificial
   or duplicate Epics.

3. Every Epic must be directly supported by the
   original Business Requirement.

4. Do not introduce unsupported business rules.

5. Do not add technical implementation details.

6. Do not assume common industry behavior.

7. If the requirement represents only one business
   capability, return exactly ONE Epic.

8. If the requirement contains multiple genuinely
   distinct business capabilities, generate one Epic
   for each capability.

9. Each Epic must represent a meaningful business
   capability.

10. Do not generate IDs.

11. Do not generate User Stories.

12. Do not generate Acceptance Criteria.

13. Do not generate Test Cases.

{feedback_text}

Return only the structured list of Epics.
"""

    schema = {
        "type": "object",
        "properties": {
            "epics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "title",
                        "description"
                    ],
                    "additionalProperties": False
                }
            }
        },
        "required": [
            "epics"
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
                "name": "multiple_epics",
                "schema": schema,
                "strict": True
            }
        },

        temperature=0
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned empty Epic response."
        )

    data = json.loads(content)

    if "epics" not in data:
        raise ValueError(
            "LLM response does not contain 'epics'."
        )

    return [
        Epic.model_validate(epic)
        for epic in data["epics"]
    ]


# ============================================================
# PYTHON VALIDATION
# ============================================================

def python_validate_epic(epic):
    """
    Basic deterministic validation.
    """

    errors = []

    if not epic.title or not epic.title.strip():
        errors.append(
            "Epic title is empty."
        )

    if not epic.description or not epic.description.strip():
        errors.append(
            "Epic description is empty."
        )

    if errors:
        return False, errors

    return True, []


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_epic(
    business_requirement,
    epic
):
    """
    Validate whether the Epic is completely supported
    by the original Business Requirement.
    """

    prompt = f"""
You are a STRICT requirements traceability validator.

Original Business Requirement:

{business_requirement}

Candidate Epic:

Title:
{epic.title}

Description:
{epic.description}

Determine whether this Epic is fully supported
by the Original Business Requirement.

STRICT RULES:

1. The Epic must represent a genuine business capability
   present in the requirement.

2. Every business behavior introduced by the Epic must
   be supported by the requirement.

3. Do not infer missing requirements.

4. Do not use common industry practices as evidence.

5. Reject unsupported:
   - security rules
   - workflows
   - validation rules
   - emails
   - reset links
   - verification codes
   - time limits
   - APIs
   - databases
   - technical implementation

6. Reject unnecessary expansion of the requirement.

7. The Epic must remain at business-capability level.

8. Do not convert assumptions into requirements.

9. Do not introduce new actors, conditions,
   notifications, or system behavior unless
   explicitly supported by the requirement.

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
                "content": prompt
            }
        ],

        temperature=0
    )

    result = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    return result


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def is_duplicate_epic(
    epic,
    approved_epics
):
    """
    Check whether an Epic is already approved.

    Duplicate detection is deterministic.
    """

    new_title = (
        epic.title
        .strip()
        .lower()
    )

    new_description = (
        epic.description
        .strip()
        .lower()
    )

    for approved in approved_epics:

        existing_title = (
            approved["title"]
            .strip()
            .lower()
        )

        existing_description = (
            approved["description"]
            .strip()
            .lower()
        )

        # Exact title match
        if new_title == existing_title:
            return True

        # Exact description match
        if new_description == existing_description:
            return True

    return False


# ============================================================
# MULTIPLE EPIC PIPELINE
# ============================================================

def generate_and_validate_epics(
    business_requirement,
    business_requirement_id="BR-001",
    max_attempts=3
):
    """
    Generate, validate and approve multiple Epics.

    Returns:

        [
            {
                "id": "EPIC-001",
                "title": "...",
                "description": "...",
                "source_requirement_id": "BR-001"
            },
            ...
        ]

    Returns an empty list if no Epic is approved
    after max_attempts.
    """

    feedback = None

    # Stores only approved Epic information.
    approved_epics = []

    for attempt in range(
        1,
        max_attempts + 1
    ):

        print(
            f"\n===== EPIC GENERATION ATTEMPT "
            f"{attempt} ====="
        )

        # ====================================================
        # GENERATE CANDIDATES
        # ====================================================

        try:

            candidates = generate_epic_candidates(
                business_requirement,
                feedback
            )

        except Exception as error:

            print(
                "\n❌ EPIC GENERATION ERROR"
            )

            print(
                "Error:",
                error
            )

            feedback = (
                "Epic generation failed. "
                "Generate a valid structured list "
                "containing at least one Epic."
            )

            continue


        # ====================================================
        # EMPTY RESULT
        # ====================================================

        if not candidates:

            print(
                "\n❌ NO EPIC CANDIDATES GENERATED"
            )

            feedback = (
                "No Epic was generated. "
                "Generate at least one valid Epic "
                "directly supported by the requirement."
            )

            continue


        print(
            f"\nGenerated {len(candidates)} "
            f"Epic candidate(s)"
        )


        # ====================================================
        # VALIDATE EACH CANDIDATE
        # ====================================================

        rejected_feedback = []

        for index, epic in enumerate(
            candidates,
            start=1
        ):

            print(
                f"\n--- CANDIDATE EPIC {index} ---"
            )

            print(
                "Title:",
                epic.title
            )

            print(
                "Description:",
                epic.description
            )


            # ------------------------------------------------
            # PYTHON VALIDATION
            # ------------------------------------------------

            valid, errors = (
                python_validate_epic(epic)
            )

            if not valid:

                reason = "; ".join(errors)

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


            # ------------------------------------------------
            # DUPLICATE VALIDATION
            # ------------------------------------------------

            if is_duplicate_epic(
                epic,
                approved_epics
            ):

                print(
                    "DUPLICATE CHECK: FAIL"
                )

                reason = (
                    f"Duplicate Epic detected: "
                    f"{epic.title}"
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


            # ------------------------------------------------
            # SEMANTIC VALIDATION
            # ------------------------------------------------

            try:

                semantic_result = (
                    semantic_validate_epic(
                        business_requirement,
                        epic
                    )
                )

            except Exception as error:

                print(
                    "❌ SEMANTIC VALIDATION ERROR"
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


            # ------------------------------------------------
            # APPROVAL
            # ------------------------------------------------

            if semantic_result.startswith(
                "PASS"
            ):

                approved_epics.append(
                    {
                        "title":
                            epic.title.strip(),

                        "description":
                            epic.description.strip(),

                        "source_requirement_id":
                            business_requirement_id
                    }
                )

                print(
                    "✅ EPIC APPROVED"
                )

            else:

                print(
                    "❌ EPIC REJECTED"
                )

                rejected_feedback.append(
                    semantic_result
                )


        # ====================================================
        # RESULT AFTER THIS ATTEMPT
        # ====================================================

        if approved_epics:

            final_epics = []

            for index, epic in enumerate(
                approved_epics,
                start=1
            ):

                final_epics.append(
                    {
                        "id":
                            f"EPIC-{index:03d}",

                        "title":
                            epic["title"],

                        "description":
                            epic["description"],

                        "source_requirement_id":
                            epic[
                                "source_requirement_id"
                            ]
                    }
                )


            # ------------------------------------------------
            # DISPLAY APPROVED EPICS
            # ------------------------------------------------

            print(
                "\n========================================"
            )

            print(
                "APPROVED EPICS"
            )

            print(
                "========================================"
            )


            for epic in final_epics:

                print(
                    f'{epic["id"]}: '
                    f'{epic["title"]}'
                )

                print(
                    "Description:",
                    epic["description"]
                )

                print(
                    "Source Requirement:",
                    epic[
                        "source_requirement_id"
                    ]
                )


            return final_epics


        # ====================================================
        # REGENERATION FEEDBACK
        # ====================================================

        if rejected_feedback:

            feedback = "\n".join(
                rejected_feedback
            )

        else:

            feedback = (
                "No valid Epic was approved. "
                "Generate corrected Epic candidates."
            )


        print(
            "\n❌ NO EPICS APPROVED"
        )

        print(
            "🔄 Regeneration required."
        )


    # ========================================================
    # MAXIMUM ATTEMPTS REACHED
    # ========================================================

    print(
        "\n❌ EPIC GENERATION FAILED"
    )

    print(
        "Maximum attempts reached."
    )

    return []


# ============================================================
# BACKWARD-COMPATIBILITY WRAPPER
# ============================================================

def generate_and_validate_epic(
    business_requirement,
    business_requirement_id="BR-001",
    max_attempts=3
):
    """
    Compatibility wrapper for older pipeline code.

    If the old pipeline expects ONE Epic, this function
    returns the first approved Epic.

    New pipeline code should use:

        generate_and_validate_epics()

    because the project supports multiple Epics.
    """

    epics = generate_and_validate_epics(
        business_requirement,
        business_requirement_id=
            business_requirement_id,
        max_attempts=max_attempts
    )

    if not epics:
        return None

    return epics[0]