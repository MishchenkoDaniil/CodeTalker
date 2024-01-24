#!/usr/bin/env python3
import argparse
import configparser
import gettext
import locale
import os
import subprocess
import sys
import requests

def set_localization():
    """ Set up localization based on the selected language """
    locale.setlocale(locale.LC_ALL, '')
    current_locale = locale.getlocale()[0]
    locale_dir = os.path.join('src', 'locales')
    language = current_locale.split('_')[0] if current_locale else 'en'
    lang = gettext.translation('codetalker', localedir=locale_dir, languages=[language], fallback=True)
    lang.install()

def run_command(command):
    """ Execute a system command and return its output """
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def get_git_diff():
    """ Retrieve the output of git diff for staged changes """
    return run_command("git diff --cached")

def generate_commit_message(diff):
    """ Generate a commit message based on git diff """
    api_key = os.getenv('CHATGPT_TOKEN')

    if not api_key:
        print("Error: ChatGPT API token not found in environment variables.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "text-davinci-003",
        "prompt": f"Explain these code changes:\n{diff}",
        "temperature": 0.5,
        "max_tokens": 100
    }
    response = requests.post("https://api.openai.com/v1/engines/text-davinci-003/completions", headers=headers, json=data)
    response_json = response.json()
    choices = response_json.get("choices")
    
    if choices and len(choices) > 0:
        return choices[0].get("text")
    else:
        print("Error: Invalid response from the API.")
        sys.exit(1)

def get_diff_between_branches(branch_a, branch_b):
    """ Retrieves git diff between two branches """
    return run_command(f"git diff {branch_a} {branch_b}")

def parse_arguments():
    """ Parses command line arguments """
    parser = argparse.ArgumentParser(description="CodeTalker - Git commit report generator")
    parser.add_argument('-a', '--branch-a', help="First branch for comparison", required=False)
    parser.add_argument('-b', '--branch-b', help="Second branch for comparison", required=False)
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    set_localization()
    
    if args.branch_a and args.branch_b:
        diff = get_diff_between_branches(args.branch_a, args.branch_b)
        print(diff)  # Or create a report using the diff
        return

    diff = get_git_diff()
    if not diff:
        print(_("No changes to commit."))
        sys.exit(0)

    commit_message = generate_commit_message(diff)
    if not commit_message:
        print(_("Error generating commit message."))
        sys.exit(1)

    run_command("git add .")
    run_command(f"git commit -m \"{commit_message}\"")
    config = configparser.ConfigParser()
    config.read('src/config.ini')
    auto_push = config['DEFAULT'].getboolean('AutoPush', True)

    if auto_push:
        current_branch = run_command("git rev-parse --abbrev-ref HEAD")
        run_command(f"git push origin {current_branch}")
        print(_(f"Changes successfully committed and pushed to branch {current_branch}."))
    else:
        print(_("Changes successfully committed. Auto-push is disabled."))

if __name__ == "__main__":
    main()