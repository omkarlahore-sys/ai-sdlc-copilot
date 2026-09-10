import os
import json

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


business_requirement = """
Customers should be able to reset their password
using their registered email address.
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
    "required": ["epics"],
    "additionalProperties": False
}


prompt = f"""
You are an experienced Business Analyst.

Analyze the following Business Requirement:

{business_requirement}

Generate all distinct business Epics required to
represent this requirement.

Rules:

1. Generate only Epics that are genuinely required
   by the requirement.

2. Do not split one simple capability into unnecessary
   artificial Epics.

3. Do not introduce unsupported business behavior.

4. Do not add technical implementation details.

5. If one Epic is sufficient, return exactly one Epic.

6. Do not generate IDs.

Return only the structured response.
"""


try:

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

    data = json.loads(
        response.choices[0].message.content
    )

    print("===== GENERATED EPICS =====")

    for index, epic in enumerate(
        data["epics"],
        start=1
    ):

        print(f"\nEPIC {index}")
        print("Title:", epic["title"])
        print("Description:", epic["description"])

except Exception as error:

    print("\n❌ MULTIPLE EPIC GENERATION FAILED")
    print("Error:", error)