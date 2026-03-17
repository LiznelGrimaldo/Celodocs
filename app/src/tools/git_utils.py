import subprocess
import os
import sys


def is_git_repository():
    """Check if the current directory is a git repository."""
    return os.path.isdir(".git")


def check_remote_changes(remote="origin", branch="main"):
    if not is_git_repository():
        return "This directory is not a Git repository."

    try:
        # Get the remote commit hash
        remote_hash = (
            subprocess.check_output(
                ["git", "ls-remote", remote, branch], stderr=subprocess.STDOUT
            )
            .decode("utf-8")
            .split()[0]
        )

        # Get the local commit hash
        local_hash = (
            subprocess.check_output(
                ["git", "rev-parse", branch], stderr=subprocess.STDOUT
            )
            .decode("utf-8")
            .strip()
        )

        # Compare the hashes
        if remote_hash != local_hash:
            return "This version of the script is outdated. Please pull the latest change via this terminal command: git pull"
        else:
            return ""

    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.output.decode('utf-8').strip()}"


def perform_git_pull():
    try:
        subprocess.run(["git", "pull"], check=True)
        print("Successfully performed git pull.")
    except subprocess.CalledProcessError as e:
        print(f"Error performing git pull: {e}")


def ask_user_for_git_pull():
    run_question = True
    while run_question:
        command = input(
            "Your script is outdated. Do you want to update the script with a git pull? (Y/N/quit) "
        )
        if command.lower() == "y":
            perform_git_pull()
            run_question = False
        elif command.lower() == "n":
            run_question = False
        elif command.lower() == "quit":
            sys.exit()
        else:
            print(f"Unknown command: {command!r}")
