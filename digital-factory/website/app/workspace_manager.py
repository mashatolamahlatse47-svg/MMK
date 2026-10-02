from pathlib import Path
import shutil


FACTORY_ROOT = Path(__file__).resolve().parents[2]
PROJECTS_ROOT = FACTORY_ROOT / "projects"
TEMPLATE_ROOT = PROJECTS_ROOT / "_TEMPLATE"


def create_project_workspace(project_id):
    project_root = PROJECTS_ROOT / project_id

    if project_root.exists():
        raise FileExistsError(
            f"Project workspace already exists: {project_id}"
        )

    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(
            "Project workspace template does not exist."
        )

    shutil.copytree(TEMPLATE_ROOT, project_root)

    return project_root


if __name__ == "__main__":
    print("[MMK WORKSPACE MANAGER READY]")
    print(f"Projects: {PROJECTS_ROOT}")
    print(f"Template: {TEMPLATE_ROOT}")
