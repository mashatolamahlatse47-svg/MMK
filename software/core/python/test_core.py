"""Basic MMK Core validation."""

from mmk_core.config import load_config
from mmk_core.version import get_version


config = load_config()

assert config["organization"] == "MMK"
assert config["currency"] == "ZAR"
assert get_version() == "0.1.0"

print("MMK Core test: PASS")
print("Organization:", config["organization"])
print("Currency:", config["currency"])
print("Version:", get_version())
