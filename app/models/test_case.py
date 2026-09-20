from pydantic import BaseModel, Field


class TestCase(BaseModel):

    title: str = Field(
        description="Short functional test case title"
    )

    precondition: str = Field(
        description="Condition required before executing the test"
    )

    steps: list[str] = Field(
        description="Ordered functional test steps"
    )

    expected_result: str = Field(
        description="Expected business outcome"
    )