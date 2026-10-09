import os
from pathlib import Path
from typing import Dict, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

BACKEND_PROMPTS_DIR = os.path.join(BACKEND_DIR, 'prompts')
PROMPTS_DIR = os.path.join(ROOT_DIR, 'prompts')


def load_prompt(filename: str) -> str:
    """
    Safely load a prompt template from disk using absolute anchoring.
    Checks backend/prompts first, then falls back to root prompts.
    """
    path = os.path.join(BACKEND_PROMPTS_DIR, filename)
    if not os.path.exists(path):
        alt_path = os.path.join(PROMPTS_DIR, filename)
        if os.path.exists(alt_path):
            path = alt_path
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


class PromptLoader:
    """
    Loads, caches, and formats LLM prompt templates using absolute path anchoring.

    Prompt files are stored externally from the Python source code so that
    prompts can be independently versioned, tested, and improved.
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        if prompts_dir:
            self.prompts_dir = Path(prompts_dir)
        else:
            if os.path.exists(BACKEND_PROMPTS_DIR):
                self.prompts_dir = Path(BACKEND_PROMPTS_DIR)
            elif os.path.exists(PROMPTS_DIR):
                self.prompts_dir = Path(PROMPTS_DIR)
            else:
                raise FileNotFoundError(
                    "Could not locate the prompts directory. "
                    f"Checked '{BACKEND_PROMPTS_DIR}' and '{PROMPTS_DIR}'."
                )

        self._cache: Dict[str, str] = {}

    def get_template(self, prompt_name: str) -> str:
        """
        Load a prompt template and cache it in memory.

        Caching prevents repeated filesystem reads for every LLM request.
        """
        if prompt_name in self._cache:
            return self._cache[prompt_name]

        filename = (
            prompt_name
            if prompt_name.endswith(".txt")
            else f"{prompt_name}.txt"
        )

        file_path = self.prompts_dir / filename

        if not file_path.is_file():
            # Fallback check in alternate prompts directory
            alt_path = Path(BACKEND_PROMPTS_DIR) / filename
            if alt_path.is_file():
                file_path = alt_path
            else:
                raise FileNotFoundError(
                    f"Prompt template not found: {file_path}"
                )

        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(
                f"Unable to read prompt template '{file_path}': {exc}"
            ) from exc

        if not content.strip():
            raise ValueError(
                f"Prompt template '{file_path}' is empty."
            )

        self._cache[prompt_name] = content
        return content

    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format a prompt template.

        Raises an explicit error when required template variables are missing
        instead of silently returning an incorrectly formatted prompt.
        """
        template = self.get_template(prompt_name)

        try:
            formatted = template.format(**kwargs)
        except KeyError as exc:
            missing_key = exc.args[0]
            raise ValueError(
                f"Missing required variable '{missing_key}' "
                f"for prompt '{prompt_name}'."
            ) from exc
        except ValueError as exc:
            raise ValueError(
                f"Invalid formatting syntax in prompt '{prompt_name}': {exc}"
            ) from exc

        if not formatted.strip():
            raise ValueError(
                f"Formatted prompt '{prompt_name}' is empty."
            )

        return formatted

    def clear_cache(self) -> None:
        """Clear cached prompt templates."""
        self._cache.clear()

    def reload_prompt(self, prompt_name: str) -> str:
        """
        Force-reload a prompt from disk.
        """
        self._cache.pop(prompt_name, None)
        return self.get_template(prompt_name)