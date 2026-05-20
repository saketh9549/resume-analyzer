from openai import OpenAI

import os


from dotenv import load_dotenv

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def rewrite_resume(resume_text):

    prompt = f"""
    Rewrite this resume professionally.

    Improve:
    - Grammar
    - ATS optimization
    - Professional tone
    - Professional wording
    - Bullet points
    - Impact statements

    Resume:
    {resume_text}
    """


    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content
    response = client.responses.create(

        model="gpt-5.4-mini",

        input=prompt
    )

    return response.output_text

