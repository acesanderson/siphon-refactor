from conduit.sync import Conduit, Model, Prompt, Response, Verbosity
from pathlib import Path
import base64
import re

EXTENSIONS = {".csv", ".json", ".xml", ".txt", ".md", ".yaml", ".toml", ".html"}
VERBOSITY = Verbosity.PROGRESS
MODEL = "gemini2.5"
PROMPT_STRING = """
You will generate the file data for the given file type and extension. I will use it to create example files for testing purposes.
Create an example {{extension}} file. ONLY return the file CONTENT, do NOT return any explanation or additional text.
Choose a random and somewhat obscure format, topic, to ensure variety in the generated examples.
Length should be around 200-300 words.
""".strip()


def generate_example_file(extension: str) -> None:
    """
    Generate an example file with LLM-created content for a given file extension.

    Uses the configured language model to create realistic example file content
    for the specified extension, writes it to disk, and logs the result. Designed
    for creating diverse test fixtures with minimal manual effort.
    """
    model = Model(MODEL)
    prompt = Prompt(PROMPT_STRING)
    conduit = Conduit(model=model, prompt=prompt)
    response = conduit.run(input_variables={"extension": extension}, verbose=VERBOSITY)

    assert isinstance(response, Response), "Expected response to be of type Response"
    response_string = str(response.content).strip()

    file_path = Path(f"example{extension}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response_string)

    print(f"Generated: {file_path}")


if __name__ == "__main__":
    for index, ext in enumerate(EXTENSIONS):
        print(f"\nGenerating example file {index + 1}/{len(EXTENSIONS)}: {ext}")
        generate_example_file(ext)
