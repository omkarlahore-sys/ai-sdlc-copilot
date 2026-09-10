from pydantic import BaseModel, Field


class Epic(BaseModel):
    title: str = Field(description="Epic title")
    description: str = Field(description="Short Epic description")