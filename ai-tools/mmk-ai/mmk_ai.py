

import os
import sys
import subprocess

BASE = os.path.expanduser("~/MMK/ai-tools")


def run_flux():
    flux_file = os.path.join(BASE, "flux", "flux.py")

    if not os.path.isfile(flux_file):
        print("\nERROR: FLUX module not found.")
        print(flux_file)
        input("\nPress Enter to continue...")
        return

    print("\n======================================")
    print("          MMK FLUX GENERATOR")
    print("======================================")
    print()
    print("Enter your image prompt.")
    print("Type 'back' to return to the main menu.")
    print()

    prompt = input("FLUX PROMPT > ").strip()

    if not prompt:
        print("\nNo prompt entered.")
        input("Press Enter to continue...")
        return

    if prompt.lower() == "back":
        return

    print("\nStarting MMK FLUX...")
    print("Note: FLUX API generation may require paid credits.\n")

    try:
        subprocess.run(
            [sys.executable, flux_file, prompt],
            check=False
        )
    except Exception as e:
        print("\nFLUX error:")
        print(e)

    input("\nPress Enter to continue...")


def system_check():
    print("\nMMK AI system location:")
    print(BASE)
    print("\nChecking folders...")

    folders = [
        "flux",
        "images",
        "output",
        "prompts",
        "scripts",
        "config",
    ]

    for folder in folders:
        path = os.path.join(BASE, folder)
        status = "OK" if os.path.isdir(path) else "MISSING"
        print(f"[{status}] {folder}")

    print("\nChecking important files...")

    files = [
        "flux/flux.py",
        "flux/.env",
        "flux/.gitignore",
    ]

    for file in files:
        path = os.path.join(BASE, file)
        status = "OK" if os.path.isfile(path) else "MISSING"
        print(f"[{status}] {file}")

    input("\nPress Enter to continue...")


def show_menu():
    while True:
        print()
        print("=" * 38)
        print("       MMK AI COMMAND CENTER")
        print("=" * 38)
        print()
        print("1. FLUX Image Generator")
        print("2. Image Optimizer")
        print("3. Prompt Library")
        print("4. Product Generator")
        print("5. Website Assets")
        print("6. Video Tools")
        print("7. MMK Catalogue")
        print("8. System Check")
        print("9. Exit")
        print()

        choice = input("MMK > ").strip()

        if choice == "1":
            run_flux()

        elif choice == "2":
            print("\nImage Optimizer: coming next.")
            input("Press Enter to continue...")

        elif choice == "3":
            print("\nPrompt Library: coming next.")
            input("Press Enter to continue...")

        elif choice == "4":
            print("\nProduct Generator: coming next.")
            input("Press Enter to continue...")

        elif choice == "5":
            print("\nWebsite Assets: coming next.")
            input("Press Enter to continue...")

        elif choice == "6":
            print("\nVideo Tools: coming next.")
            input("Press Enter to continue...")

        elif choice == "7":
            print("\nMMK Catalogue: coming next.")
            input("Press Enter to continue...")

        elif choice == "8":
            system_check()

        elif choice == "9":
            print("\nMMK AI Command Center closed.")
            break

        else:
            print("\nInvalid option. Choose 1-9.")


if __name__ == "__main__":
    show_menu()

        
