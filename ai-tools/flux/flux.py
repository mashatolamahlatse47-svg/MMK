import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BFL_API_KEY")

if not API_KEY:
    print("ERROR: BFL_API_KEY is not set.")
    print("Add your FLUX API key to ai-tools/flux/.env")
    sys.exit(1)

prompt = " ".join(sys.argv[1:]).strip()

if not prompt:
    print("Usage:")
    print('python flux.py "your image prompt here"')
    sys.exit(1)

url = "https://api.bfl.ai/v1/flux-2-pro"

headers = {
    "accept": "application/json",
    "x-key": API_KEY,
    "Content-Type": "application/json",
}

payload = {
    "prompt": prompt,
    "width": 1024,
    "height": 1024,
}

print("MMK FLUX: submitting image request...")

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=60,
)

response.raise_for_status()
data = response.json()

polling_url = data.get("polling_url")

if not polling_url:
    print("ERROR: No polling URL returned.")
    print(data)
    sys.exit(1)

print("MMK FLUX: request accepted.")
print("MMK FLUX: waiting for image...")

while True:
    result = requests.get(
        polling_url,
        headers={"x-key": API_KEY},
        timeout=60,
    )

    result.raise_for_status()
    status_data = result.json()

    status = status_data.get("status")

    if status == "Ready":
        image_url = status_data["result"]["sample"]
        break

    if status in ("Error", "Failed"):
        print("FLUX generation failed:")
        print(status_data)
        sys.exit(1)

    print(f"Status: {status}")
    time.sleep(2)

print("MMK FLUX: downloading image...")

image = requests.get(image_url, timeout=120)
image.raise_for_status()

os.makedirs("../output", exist_ok=True)

filename = "../output/mmk_flux_" + time.strftime("%Y%m%d_%H%M%S") + ".jpg"

with open(filename, "wb") as f:
    f.write(image.content)

print()
print("SUCCESS!")
print(f"Image saved to: {filename}")
