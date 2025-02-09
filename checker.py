import os
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import json
import instructor

load_dotenv()  # Loads your GROQ_API_KEY from .env file


client = instructor.from_groq(Groq(api_key=os.getenv("GROQ_API_KEY")), mode=instructor.Mode.JSON)


class CodeChange(BaseModel):
    path: str
    code_rewrite: str
    explanation: str

def get_all_files_recursively(root_directory):
    """
    Recursively collect all file paths under the specified directory.
    """
    all_files = []
    for root, dirs, files in os.walk(root_directory):
        for filename in files:
            # Build the full path to the file
            file_path = os.path.join(root, filename)
            all_files.append(file_path)
    return all_files

def analyze_file_with_llm(file_path):
    """
    Reads file content and queries the LLM to determine if it's out of date
    and what changes might be necessary. Returns a CodeChange object if applicable.
    """
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as f:
        file_content = f.read()
        # print(file_content)

    # Create a user prompt for the LLM
    user_prompt = (
        "Analyze the following code and determine if the syntax is out of date. "
        "If it is out of date, specify what changes need to be made in the following JSON format:\n\n"
        "{\n"
        '  "path": "relative/file/path",\n'
        '  "code_rewrite": "A rewrite of the file that is more up to date, using the native language (i.e. if the file is a Next.Js file, rewrite the Next.js file using Javascript/Typescript with the updated API changes)". The file should be a complete file, not just a partial updated code segment,\n'
        '  "explanation": "Explanation of why the change is necessary."\n'
        "}\n\n"
        f"{file_content}"
    )


    try:
        chat_completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": "You are a helpful assistant that analyzes code and returns a JSON object with the path, code change, and explanation. Your goal is to identify outdated syntax in code and suggest changes to update it to the latest syntax."}, {"role": "user", "content": user_prompt}],
            response_model=CodeChange,
        )
        # llm_response = chat_completion.choices[0].message.content
        print(chat_completion)
        
        # Convert the LLM response to a dictionary before creating the CodeChange instance
        # code_change_data = json.loads(chat_completion)
        # code_change = CodeChange(**code_change_data)  # This should work now
        return chat_completion
    except (ValidationError, json.JSONDecodeError) as parse_error:
        print(f"Error parsing LLM response for {file_path}: {parse_error}")
        return None
    except Exception as e:
        # Handle any other exceptions, e.g. network errors, model issues, etc.
        print(f"Error analyzing {file_path}: {e}")
        return None

def main():
    # Directory you want to recursively analyze
    directory_to_analyze = "example-web"

    # Store results in a list of CodeChange instances
    analysis_results = []

    all_files = get_all_files_recursively(directory_to_analyze)
    for filepath in all_files:
        # Query LLM for this file
        response = analyze_file_with_llm(filepath)
        if response is None:
            continue  # Skip if there was an error
        analysis_results.append(response)

    # Print out any files that are deemed out of date and their suggested changes
    if not analysis_results:
        print("No files were found to be out of date.")
    else:
        for result in analysis_results:
            print(f"File '{result.path}' is out of date.")
            print("Suggested Changes:\n", result.code_rewrite)
            print("Explanation:\n", result.explanation)
            print("-" * 40)

if __name__ == "__main__":
    main()
