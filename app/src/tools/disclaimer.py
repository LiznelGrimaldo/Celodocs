import os
from rich import print
from rich.prompt import Prompt


def display_disclaimer():
    disclaimer = """
    This script corresponds to a “Celonis Non-Release Tool” as stated in the 
    [Celonis Non-Release Tools - Terms of Use (April 2022)](/disclaimer.md).
    By clicking the “I accept” button or otherwise affirmatively respond as part of 
    the access process to the Tools, you (both as an individual and as an authorized 
    representative on behalf of the legal entity you are employed by)
    agree that you have read these Terms and agree to be legally bound by them.
    """
    print(disclaimer)
    response = input("Do you accept the terms? (yes/no): ").strip().lower()
    return response == "yes"


def check_disclaimer_accepted():
    accepted_file = "disclaimer_accepted.txt"

    # Check if the disclaimer has been accepted previously
    if os.path.exists(accepted_file):
        print("Disclaimer has already been accepted.")
        return True
    else:
        # Display disclaimer and ask for acceptance
        if display_disclaimer():
            with open(accepted_file, "w") as f:
                f.write("accepted")
            print("Thank you for accepting the terms.")
            return True
        else:
            print("You need to accept the terms to proceed.")
            return False


def main_script():
    # Your main script logic goes here
    print("Running main script...")


if __name__ == "__main__":
    if check_disclaimer_accepted():
        main_script()
    else:
        print("Exiting the script.")
