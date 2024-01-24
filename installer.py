import os
import shutil
import configparser
import sys

def copy_localization_files(language):
    """ Copies localization files for the selected language """
    src_dir = os.path.join("locales", language, "LC_MESSAGES")
    dest_dir = os.path.join("src", "locales", language, "LC_MESSAGES")
    
    if not os.path.exists(src_dir):
        print(f"Localization files for '{language}' not found.")
        return False

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for file_name in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file_name)
        dest_file = os.path.join(dest_dir, file_name)
        shutil.copy2(src_file, dest_file)

    print(f"Localization files for '{language}' have been installed.")
    return True

def save_api_token(config):
    """ Saves the ChatGPT API token to the configuration """
    token = input("Please enter your ChatGPT API token: ").strip()
    config['DEFAULT']['ChatGPTToken'] = token
    print("API token saved.")

def save_auto_push_setting(config):
    """ Asks the user whether to enable auto-push and saves the setting """
    auto_push = input("Do you want to enable automatic commit push? (yes/no): ").strip().lower()
    config['DEFAULT']['AutoPush'] = 'true' if auto_push == 'yes' else 'false'
    print("Auto-push setting saved.")

def copy_config_file(config):
    """ Copies the config.ini file to the src directory """
    config_dir = 'src'
    config_path = os.path.join(config_dir, 'config.ini')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    with open(config_path, 'w') as configfile:
        config.write(configfile)

    print("Config file saved at:", config_path)

def create_symlink(script_path, symlink_path):
    """ Creates a symbolic link to the script """
    try:
        if os.path.lexists(symlink_path):
            os.remove(symlink_path)
        os.symlink(script_path, symlink_path)
        print(f"Created symlink: {symlink_path}")
    except OSError as e:
        print(f"Error creating symlink: {e}")
        sys.exit(1)

def main():
    print("Welcome to the CodeTalker installer.")
    language = input("Choose your language (en/uk): ").strip().lower()
    if language not in ["en", "uk"]:
        print("Invalid language selection. Falling back to English.")
        language = "en"

    config = configparser.ConfigParser()
    if copy_localization_files(language):
        save_api_token(config)
        save_auto_push_setting(config)
        copy_config_file(config)

    # Specify the full path to your script
    script_path = os.path.abspath("src/codetalker.py")
    if not os.path.exists(script_path):
        print(f"Error: 'codetalker.py' not found at {script_path}.")
        sys.exit(1)

    # Making the script executable
    os.chmod(script_path, 0o755)

    # Creating symbolic links
    create_symlink(script_path, "/usr/local/bin/codetalker")
    create_symlink(script_path, "/usr/local/bin/ct")

if __name__ == "__main__":
    main()