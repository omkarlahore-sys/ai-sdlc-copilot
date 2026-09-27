# ============================================================
# AI SDLC COPILOT - EPIC SERVICE
# ============================================================

from __future__ import annotations

import json
import os
import time
from typing import Any

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
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "openai/gpt-oss-120b"

# Maximum number of actual generation attempts.
MAX_GENERATION_ATTEMPTS = 5

# Temporary API retry count.
API_RETRY_ATTEMPTS = 3

# Delay between API retries.
API_RETRY_DELAY_SECONDS = 2


# ============================================================
# PROMPT SAFETY LIMITS
# ============================================================

# This is NOT a limit on the user's Business Requirement.
#
# It only prevents accidental prompt explosion when feedback
# from previous failed attempts becomes very large.

MAX_REQUIREMENT_CHARS = 20000
MAX_FEEDBACK_CHARS = 6000


# ============================================================
# TEXT HELPERS
# ============================================================

def _clean_text(
    text: Any,
    max_chars: int | None = None,
) -> str:
    """
    Safely convert text into a clean string.

    If max_chars is provided, truncate only the prompt copy.
    The original Business Requirement remains unchanged
    everywhere else in the application.
    """

    if text is None:
        return ""

    value = str(text).strip()

    if max_chars is not None:
        if len(value) > max_chars:
            value = (
                value[:max_chars]
                + "\n\n[Prompt text truncated for safety.]"
            )

    return value


def _prepare_requirement(
    business_requirement: str,
) -> str:
    """
    Prepare a Business Requirement for LLM prompts.

    There is intentionally no 400/500 character restriction.
    """

    requirement = _clean_text(
        business_requirement
    )

    if not requirement:
        raise ValueError(
            "Business Requirement cannot be empty."
        )

    return _clean_text(
        requirement,
        MAX_REQUIREMENT_CHARS,
    )


def _prepare_feedback(
    feedback: str | None,
) -> str:
    """
    Prevent validation feedback from growing indefinitely
    across regeneration attempts.
    """

    if not feedback:
        return ""

    return _clean_text(
        feedback,
        MAX_FEEDBACK_CHARS,
    )


# ============================================================
# GROQ API HELPER
# ============================================================

def _call_groq(
    messages: list[dict[str, str]],
    response_format: dict | None = None,
    temperature: float = 0,
):
    """
    Call Groq with controlled retry handling.

    Important:
        API retries are separate from generation attempts.

    A temporary 429 / timeout / connection problem should
    not immediately consume one of the five generation attempts.
    """

    last_error = None

    for retry_number in range(
        1,
        API_RETRY_ATTEMPTS + 1,
    ):

        try:

            kwargs = {
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": temperature,
            }

            if response_format is not None:
                kwargs["response_format"] = response_format

            return client.chat.completions.create(
                **kwargs
            )

        except Exception as error:

            last_error = error

            error_text = str(error).lower()

            retryable = (
                "429" in error_text
                or "rate limit" in error_text
                or "too many requests" in error_text
                or "timeout" in error_text
                or "timed out" in error_text
                or "temporarily unavailable" in error_text
                or "connection" in error_text
            )

            # ----------------------------------------------
            # Non-retryable error
            # ----------------------------------------------

            if not retryable:
                raise

            # ----------------------------------------------
            # Maximum API retry reached
            # ----------------------------------------------

            if retry_number >= API_RETRY_ATTEMPTS:

                raise RuntimeError(
                    "Groq API request failed after "
                    f"{API_RETRY_ATTEMPTS} retries: "
                    f"{error}"
                ) from error

            delay = (
                API_RETRY_DELAY_SECONDS
                * retry_number
            )

            print(
                "\n⚠️ Temporary Groq API problem."
            )

            print(
                f"API retry "
                f"{retry_number + 1}/"
                f"{API_RETRY_ATTEMPTS}"
            )

            print(
                f"Waiting {delay} seconds..."
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Groq API request failed: {last_error}"
    )


# ============================================================
# EPIC GENERATION
# ============================================================

def generate_epic_candidates(
    business_requirement: str,
    feedback: str | None = None,
) -> list[Epic]:
    """
    Generate one or more Epic candidates.

    The Business Requirement can be long.
    There is no 400/500 character restriction.
    """

    requirement = _prepare_requirement(
        business_requirement
    )

    feedback_text = ""

    if feedback:

        safe_feedback = _prepare_feedback(
            feedback
        )

        feedback_text = f"""

Previous validation feedback:

{safe_feedback}

Use this feedback only to correct the previous
Epic generation.

Do not introduce new business requirements.
"""

    prompt = f"""
You are an experienced Business Analyst.

Analyze the following Business Requirement.

BUSINESS REQUIREMENT:
{requirement}

Generate all DISTINCT business Epics required
to represent this requirement.

IMPORTANT:

The Business Requirement may be long and may contain
multiple sentences, business rules, actors,
processes, and capabilities.

Read the complete requirement before generating
the Epics.

Rules:

1. Generate only genuinely distinct business
   capabilities.

2. Do not create artificial Epics simply because
   the requirement contains many sentences.

3. Do not merge genuinely distinct business
   capabilities unnecessarily.

4. Every Epic must be directly supported by the
   Business Requirement.

5. Do not invent requirements.

6. Do not assume common industry behavior.

7. Do not add technical implementation details.

8. Do not add APIs, databases, frameworks,
   programming languages, cloud services,
   authentication mechanisms, or infrastructure
   unless explicitly required as a business capability.

9. If the requirement represents one capability,
   return exactly one Epic.

10. If the requirement contains multiple genuinely
    distinct business capabilities, return one Epic
    for each capability.

11. Each Epic must remain at business-capability level.

12. Do not generate IDs.

13. Do not generate User Stories.

14. Do not generate Acceptance Criteria.

15. Do not generate Test Cases.

{feedback_text}

Return only the structured Epic list.
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
                        "description",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": [
            "epics",
        ],
        "additionalProperties": False,
    }

    response = _call_groq(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "multiple_epics",
                "schema": schema,
                "strict": True,
            },
        },
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "LLM returned an empty Epic response."
        )

    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            "LLM returned invalid JSON for Epics."
        ) from error

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

def python_validate_epic(
    epic: Epic,
):
    """
    Deterministic validation.

    No LLM call is required.
    """

    errors = []

    title = (
        epic.title.strip()
        if epic.title
        else ""
    )

    description = (
        epic.description.strip()
        if epic.description
        else ""
    )

    if not title:

        errors.append(
            "Epic title is empty."
        )

    if not description:

        errors.append(
            "Epic description is empty."
        )

    if len(title) > 200:

        errors.append(
            "Epic title is too long."
        )

    if len(description) > 1500:

        errors.append(
            "Epic description is too long."
        )

    if errors:

        return False, errors

    return True, []


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def is_duplicate_epic(
    epic: Epic,
    existing_epics: list[dict],
) -> bool:
    """
    Deterministic duplicate detection.

    Checks:
        - exact title
        - exact description
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

    for existing in existing_epics:

        existing_title = (
            existing["title"]
            .strip()
            .lower()
        )

        existing_description = (
            existing["description"]
            .strip()
            .lower()
        )

        if new_title == existing_title:

            return True

        if new_description == existing_description:

            return True

    return False


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def semantic_validate_epics(
    business_requirement: str,
    epics: list[Epic],
) -> list[dict]:
    """
    Validate all Epics in ONE LLM call.

    This is much more efficient than making one
    semantic-validation API call per Epic.
    """

    requirement = _prepare_requirement(
        business_requirement
    )

    epic_text_parts = []

    for index, epic in enumerate(
        epics,
        start=1,
    ):

        epic_text_parts.append(
            f"""
EPIC {index}

Title:
{epic.title}

Description:
{epic.description}
"""
        )

    epic_text = "\n".join(
        epic_text_parts
    )

    prompt = f"""
You are a strict requirements traceability
validator.

Read the COMPLETE Business Requirement.

BUSINESS REQUIREMENT:
{requirement}

CANDIDATE EPICS:
{epic_text}

Validate every candidate Epic.

Rules:

1. The Epic must represent a genuine business
   capability contained in the requirement.

2. The Epic must not introduce unsupported
   business behavior.

3. Do not infer missing requirements.

4. Do not use common industry practices as evidence.

5. Reject unsupported:
   - security requirements
   - validation rules
   - email behavior
   - reset links
   - verification codes
   - time limits
   - APIs
   - databases
   - technical implementation

6. Reject unnecessary expansion.

7. Keep the Epic at business-capability level.

8. Do not introduce unsupported actors.

9. Do not introduce unsupported conditions.

10. Do not introduce unsupported notifications.

11. Identify duplicate or overlapping Epics.

12. If an Epic is clearly supported by the requirement,
    mark it PASS.

13. Only mark FAIL when there is a concrete
    unsupported behavior or traceability problem.

Return one validation result for every Epic.
"""

    schema = {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "epic_index": {
                            "type": "integer"
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "PASS",
                                "FAIL",
                            ],
                        },
                        "reason": {
                            "type": "string"
                        },
                    },
                    "required": [
                        "epic_index",
                        "status",
                        "reason",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": [
            "results",
        ],
        "additionalProperties": False,
    }

    response = _call_groq(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "epic_validation",
                "schema": schema,
                "strict": True,
            },
        },
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:

        raise ValueError(
            "LLM returned an empty semantic validation response."
        )

    try:

        data = json.loads(content)

    except json.JSONDecodeError as error:

        raise ValueError(
            "Invalid JSON returned by semantic validator."
        ) from error

    results = data.get(
        "results",
        []
    )

    if not results:

        raise ValueError(
            "Semantic validator returned no results."
        )

    return results


# ============================================================
# BUILD APPROVED EPICS
# ============================================================

def _build_final_epics(
    approved_epics: list[dict],
):
    """
    Assign stable Epic IDs after validation.
    """

    final_epics = []

    for index, epic in enumerate(
        approved_epics,
        start=1,
    ):

        final_epics.append(
            {
                "id":
                    f"EPIC-{index:03d}",

                "title":
                    epic["title"].strip(),

                "description":
                    epic["description"].strip(),

                "source_requirement_id":
                    epic[
                        "source_requirement_id"
                    ],
            }
        )

    return final_epics


# ============================================================
# MAIN EPIC PIPELINE
# ============================================================

def generate_and_validate_epics(
    business_requirement: str,
    business_requirement_id: str = "BR-001",
    max_attempts: int = MAX_GENERATION_ATTEMPTS,
):
    """
    Generate and validate multiple Epics.

    Important:

    max_attempts = 5

    This controls generation attempts.

    API retry handling is separate.

    Long Business Requirements are supported.
    """

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    requirement = _prepare_requirement(
        business_requirement
    )

    if max_attempts < 1:

        max_attempts = 1

    # Prevent accidental extreme values.

    max_attempts = min(
        max_attempts,
        5,
    )

    feedback = None

    # ========================================================
    # GENERATION LOOP
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        print("\n")
        print("=" * 80)
        print(
            f"EPIC GENERATION ATTEMPT "
            f"{attempt}/{max_attempts}"
        )
        print("=" * 80)

        # ====================================================
        # STEP 1 - GENERATE
        # ====================================================

        try:

            candidates = generate_epic_candidates(
                requirement,
                feedback,
            )

        except Exception as error:

            print(
                "\n❌ EPIC GENERATION ERROR"
            )

            print(
                "Error:",
                error,
            )

            # This is feedback for the next attempt,
            # but temporary API retries have already been
            # handled inside _call_groq().

            feedback = (
                "The previous Epic generation failed. "
                "Generate a valid structured Epic response "
                "directly supported by the Business Requirement."
            )

            continue

        # ====================================================
        # STEP 2 - EMPTY RESULT
        # ====================================================

        if not candidates:

            print(
                "\n❌ NO EPIC CANDIDATES GENERATED"
            )

            feedback = (
                "No Epic was generated. "
                "Generate at least one meaningful "
                "business capability."
            )

            continue

        print(
            f"\nGenerated "
            f"{len(candidates)} Epic candidate(s)."
        )

        # ====================================================
        # STEP 3 - PYTHON VALIDATION
        # ====================================================

        valid_candidates = []

        rejected_feedback = []

        for index, epic in enumerate(
            candidates,
            start=1,
        ):

            print(
                f"\n--- CANDIDATE EPIC {index} ---"
            )

            print(
                "Title:",
                epic.title,
            )

            print(
                "Description:",
                epic.description,
            )

            valid, errors = (
                python_validate_epic(
                    epic
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
                    reason,
                )

                rejected_feedback.append(
                    reason
                )

                continue

            print(
                "PYTHON VALIDATION: PASS"
            )

            # ------------------------------------------------
            # Duplicate validation
            # ------------------------------------------------

            if is_duplicate_epic(
                epic,
                [
                    {
                        "title":
                            item.title,

                        "description":
                            item.description,
                    }
                    for item in valid_candidates
                ],
            ):

                reason = (
                    f"Duplicate Epic detected: "
                    f"{epic.title}"
                )

                print(
                    "DUPLICATE CHECK: FAIL"
                )

                print(
                    "Reason:",
                    reason,
                )

                rejected_feedback.append(
                    reason
                )

                continue

            print(
                "DUPLICATE CHECK: PASS"
            )

            valid_candidates.append(
                epic
            )

        # ====================================================
        # NO VALID CANDIDATES
        # ====================================================

        if not valid_candidates:

            print(
                "\n❌ NO VALID EPIC CANDIDATES"
            )

            feedback = "\n".join(
                rejected_feedback
            )

            feedback = _prepare_feedback(
                feedback
            )

            continue

        # ====================================================
        # STEP 4 - SEMANTIC VALIDATION
        # ====================================================

        try:

            validation_results = (
                semantic_validate_epics(
                    requirement,
                    valid_candidates,
                )
            )

        except Exception as error:

            print(
                "\n❌ SEMANTIC VALIDATION ERROR"
            )

            print(
                "Error:",
                error,
            )

            feedback = (
                "Semantic validation could not be completed. "
                "Generate Epics directly supported by the "
                "Business Requirement."
            )

            continue

        # ====================================================
        # STEP 5 - PROCESS RESULTS
        # ====================================================

        approved_epics = []

        returned_indexes = set()

        for result in validation_results:

            epic_index = result.get(
                "epic_index"
            )

            status = str(
                result.get(
                    "status",
                    "",
                )
            ).strip().upper()

            reason = str(
                result.get(
                    "reason",
                    "",
                )
            ).strip()

            # ----------------------------------------------
            # Validate index
            # ----------------------------------------------

            if not isinstance(
                epic_index,
                int,
            ):

                continue

            if (
                epic_index < 1
                or epic_index > len(
                    valid_candidates
                )
            ):

                continue

            returned_indexes.add(
                epic_index
            )

            epic = valid_candidates[
                epic_index - 1
            ]

            print(
                f"\nSEMANTIC VALIDATION "
                f"FOR EPIC {epic_index}"
            )

            print(
                "Status:",
                status,
            )

            print(
                "Reason:",
                reason,
            )

            if status == "PASS":

                approved_epics.append(
                    {
                        "title":
                            epic.title.strip(),

                        "description":
                            epic.description.strip(),

                        "source_requirement_id":
                            business_requirement_id,
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
                    f"{epic.title}: {reason}"
                )

        # ====================================================
        # STEP 6 - CHECK MISSING VALIDATION RESULTS
        # ====================================================

        if len(returned_indexes) != len(
            valid_candidates
        ):

            print(
                "\n⚠️ Validator did not return "
                "a result for every candidate."
            )

            rejected_feedback.append(
                "Semantic validator must return "
                "a result for every Epic."
            )

        # ====================================================
        # STEP 7 - APPROVED EPICS
        # ====================================================

        if approved_epics:

            final_epics = _build_final_epics(
                approved_epics
            )

            print("\n")
            print("=" * 80)
            print("APPROVED EPICS")
            print("=" * 80)

            for epic in final_epics:

                print(
                    f'\n{epic["id"]}: '
                    f'{epic["title"]}'
                )

                print(
                    "Description:",
                    epic["description"],
                )

                print(
                    "Source Requirement:",
                    epic[
                        "source_requirement_id"
                    ],
                )

            return final_epics

        # ====================================================
        # STEP 8 - PREPARE REGENERATION FEEDBACK
        # ====================================================

        if rejected_feedback:

            feedback = "\n".join(
                rejected_feedback
            )

        else:

            feedback = (
                "No Epic was approved. "
                "Generate corrected Epics that are "
                "directly supported by the requirement."
            )

        feedback = _prepare_feedback(
            feedback
        )

        print(
            "\n❌ NO EPICS APPROVED"
        )

        if attempt < max_attempts:

            print(
                "🔄 Regeneration required."
            )

    # ========================================================
    # FINAL FAILURE
    # ========================================================

    print("\n")
    print("=" * 80)
    print("❌ EPIC GENERATION FAILED")
    print("=" * 80)

    print(
        f"Maximum generation attempts "
        f"({max_attempts}) reached."
    )

    print(
        "\nPossible reasons:"
    )

    print(
        "1. Semantic validator rejected the generated Epics."
    )

    print(
        "2. The model generated unsupported business behavior."
    )

    print(
        "3. The requirement is ambiguous."
    )

    print(
        "4. The API returned invalid structured output."
    )

    print(
        "5. The validator could not validate all candidates."
    )

    return []


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def generate_and_validate_epic(
    business_requirement: str,
    business_requirement_id: str = "BR-001",
    max_attempts: int = MAX_GENERATION_ATTEMPTS,
):
    """
    Compatibility wrapper for code that expects
    a single Epic.
    """

    epics = generate_and_validate_epics(
        business_requirement,
        business_requirement_id=(
            business_requirement_id
        ),
        max_attempts=max_attempts,
    )

    if not epics:
        return None

    return epics[0]