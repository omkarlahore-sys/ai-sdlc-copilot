from pydantic import BaseModel, Field


class AcceptanceCriteria(BaseModel):
    given: str = Field(
        description="The initial condition before the action"
    )

    when: str = Field(
        description="The user action or event"
    )

    then: str = Field(
        description="The expected business outcome"
    )