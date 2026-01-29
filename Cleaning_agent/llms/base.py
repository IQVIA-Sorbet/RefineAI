import json

class LLMClient:
    def __init__(self, call_fn):
        """
        call_fn: function(prompt: str) -> str
        Example: gemini_call or openai_call
        """
        self.call_fn = call_fn

    def call(self, prompt: str) -> str:
        """
        Raw text call. Used for code generation.
        """
        response = self.call_fn(prompt)

        if not isinstance(response, str):
            raise ValueError("LLM response is not a string")

        return response.strip()

    def ask_json(self, prompt: str) -> dict:
        """
        Call LLM and strictly parse JSON.
        Used for interpreter / verifier / auditor.
        """
        raw = self.call(prompt)

        # Gemini sometimes wraps JSON in ``` or text
        cleaned = self._extract_json(raw)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM did not return valid JSON.\n"
                f"Raw response:\n{raw}"
            ) from e

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON object from Gemini responses that may contain
        markdown or extra text.
        """
        text = text.strip()

        # Case 1: Markdown fenced JSON
        if text.startswith("```"):
            lines = text.splitlines()
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines).strip()

        # Case 2: Text before/after JSON
        first = text.find("{")
        last = text.rfind("}")

        if first != -1 and last != -1 and last > first:
            return text[first:last + 1]

        return text
