import sys
from pathlib import Path

ENGINE_PATH = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from sites import create_site, get_site, list_sites, deactivate_site


def test_site_management():
    site_id = create_site(
        "MMK Development Test Site",
        "Test Address"
    )

    site = get_site(site_id)

    assert site is not None
    assert site["name"] == "MMK Development Test Site"
    assert site["status"] == "active"

    sites = list_sites()

    assert any(item["id"] == site_id for item in sites)

    deactivate_site(site_id)

    site = get_site(site_id)

    assert site["status"] == "inactive"


if __name__ == "__main__":
    test_site_management()
    print("MMK Security Site Test: PASS")
    print("Create site: PASS")
    print("Retrieve site: PASS")
    print("List sites: PASS")
    print("Deactivate site: PASS")
