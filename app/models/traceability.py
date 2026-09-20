from pydantic import BaseModel


# ============================================================
# TRACEABILITY RECORD
# ============================================================

class TraceabilityRecord(BaseModel):

    business_requirement_id: str

    epic_id: str

    user_story_id: str

    acceptance_criteria_id: str

    test_case_id: str


# ============================================================
# TRACEABILITY REPORT
# ============================================================

class TraceabilityReport(BaseModel):

    records: list[TraceabilityRecord]