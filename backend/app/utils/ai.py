import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"


def ask_groq(system_prompt: str, user_prompt: str, max_tokens: int = 300) -> str:
    """
    Send a prompt to Groq and return the response text.
    Returns a fallback string if the API call fails.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq Error] {e}")
        return "I'm having trouble connecting right now. Keep going — you're doing great!"