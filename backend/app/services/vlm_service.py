import base64
import mimetypes
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv("backend/.env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def analyze_image(image_path: str):

    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    response = client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """
Analyze this image carefully.

If it contains a chart or graph:
- identify the chart type
- identify the X and Y axes
- identify important values
- explain trends
- compare important values

If it contains a diagram:
- explain the main components
- explain the relationships between them

If it contains text:
- extract the important information

Give a clear and factual explanation.
""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        temperature=0.2,
        max_completion_tokens=1500,
    )

    return response.choices[0].message.content