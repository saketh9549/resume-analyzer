from openai import OpenAI

import os



from dotenv import load_dotenv

import os

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

# -----------------------------------
# OPENAI CLIENT
# -----------------------------------

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# -----------------------------------
# AI FEEDBACK FUNCTION
# -----------------------------------


def get_resume_feedback(resume_text):

    prompt = f"""
    Analyze this resume and provide:

    1. Strengths
    2. Weaknesses
    3. Improvements
    4. ATS Optimization Tips

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
