import subprocess

def git(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except Exception:
        return "Unavailable"

print("MMK GIT STATUS")
print("Branch:", git("git branch --show-current"))
print("Latest commit:", git("git log -1 --oneline"))
print("Changes:")
print(git("git status --short") or "Clean working tree.")
