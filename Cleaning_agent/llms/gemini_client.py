import time
import random
from google import genai
from google.genai import types, errors

# IMPORTANT:
# This uses Application Default Credentials (OAuth)
# No API keys anywhere

client = genai.Client(
    vertexai=True,
    project="tedxtrial",
    location="global"  # 'global' often fails for Vertex GenAI; 'us-central1' is safer
)


# --- START OF NEW CODE ---

def gemini_call_with_retry(prompt, max_retries=7):
    """
    Wrapper for Gemini API with exponential backoff and correct error handling
    for the google-genai (v0.2+) library.
    """
    base_wait_time = 1

    for i in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(  # 'config' is the argument name in new lib
                    temperature=0
                )
            )

            # In the new library, safety blocks often return a valid response object
            # but with no text. We must check for this to avoid "NoneType" errors.
            if not response.text:
                # You can inspect response.candidates[0].finish_reason here if needed
                print(f"ERROR: Response blocked or empty. Finish Reason: {response.candidates[0].finish_reason}")
                raise ValueError("Prompt was blocked by safety settings or returned no content.")

            return response.text

        except errors.ClientError as e:
            # The new library uses ClientError for HTTP status codes (4xx)
            if e.code == 429:  # Rate Limit
                if i < max_retries - 1:
                    wait_time = base_wait_time * (2 ** i) + random.uniform(0, 1)
                    print(f"Rate limit exceeded (429). Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    continue

            # If it's a 400 (Bad Request), it's often a policy violation or invalid argument
            if e.code == 400:
                print(f"ERROR: Bad Request (Likely blocked or invalid): {e}")
                raise

            # Re-raise other ClientErrors (401, 403, 404, etc.)
            raise e

        except errors.ServerError as e:
            # 5xx Errors (Google side issues) - Safe to retry
            if i < max_retries - 1:
                wait_time = base_wait_time * (2 ** i) + random.uniform(0, 1)
                print(f"Server error ({e.code}). Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
                continue
            raise e

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

    raise Exception("LLM call failed after multiple retries.")


def gemini_call(prompt):
    return gemini_call_with_retry(prompt)