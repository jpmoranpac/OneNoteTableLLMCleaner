from openai import OpenAI

# Initialize client (Groq uses OpenAI-compatible API)
def create_openai_client(key_path: str = "api_key.txt") -> OpenAI:
    """
    Reads API key from file and returns an OpenAI client.

    File should contain ONLY the API key (no quotes, no extra text).
    """
    with open(key_path, "r", encoding="utf-8") as f:
        api_key = f.read().strip()

    if not api_key:
        raise ValueError("API key file is empty")

    return OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

client = create_openai_client()

SYSTEM_PROMPT = """You are editing rough conference notes.

Rules:
- Correct spelling, grammar, and punctuation
- Do NOT change meaning
- Do NOT summarise or expand
- Preserve structure where possible
"""
import time
import re
from openai import RateLimitError

def with_backoff(func, *args, max_retries=5, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)

        except RateLimitError as e:
            msg = str(e)

            # Try to extract "try again in Xs"
            match = re.search(r"try again in ([0-9.]+)s", msg)

            if match:
                wait_time = float(match.group(1))
            else:
                # fallback exponential backoff
                wait_time = 2 ** attempt

            print(f"Rate limited. Waiting {wait_time:.2f}s...")
            time.sleep(wait_time)

    raise RuntimeError("Max retries exceeded")

def proofread_text(text):
#     response = with_backoff(
#     client.chat.completions.create,
#     model="llama-3.1-8b-instant",
#     messages=[{"role": "user", "content": text}]
# )

    response = with_backoff(client.chat.completions.create,
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    sample_text = """
    today we discused pacemaker implantaion and its complication.
    the patient was very unstable but respond well after procedure.
    doctor said it was succesfull overall
    """

    corrected = proofread_text(sample_text)

    print("=== Original ===")
    print(sample_text)
    print("\n=== Corrected ===")
    print(corrected)
