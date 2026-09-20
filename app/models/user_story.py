from pydantic import BaseModel, Field


class UserStory(BaseModel):

    title: str = Field(
        description="Short user story title"
    )

    story: str = Field(
        description=(
            "User story following "
            "As a... I want... so that..."
        )
    )