from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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