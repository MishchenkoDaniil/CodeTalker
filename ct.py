import requests
import subprocess
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_current_branch():
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    return result.stdout.strip()

def get_git_diff():
    subprocess.run(["git", "add", "."], check=True)
    result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True)
    return result.stdout

def generate_commit_message(diff_output):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "prompt": f"Write a commit message based on these code changes:\n\n{diff_output}",
        "max_tokens": 60
    }
    # Замените 'davinci-codex' на актуальное название модели, например 'text-davinci-003'
    response = requests.post("https://api.openai.com/v1/engines/gpt-3.5-turbo/completions", headers=headers, json=data)
    return response.json().get("choices", [{}])[0].get("text", "").strip()

def git_commit_push():
    try:
        diff_output = get_git_diff()
        print("Git diff output:", diff_output)  # Отладочная печать

        commit_message = generate_commit_message(diff_output)
        print("Generated commit message:", commit_message)  # Отладочная печать

        if not commit_message:
            commit_message = "Minor changes"

        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        current_branch = get_current_branch()
        subprocess.run(["git", "push", "origin", current_branch], check=True)

        print(f"Changes successfully committed and pushed to {current_branch}.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

git_commit_push()