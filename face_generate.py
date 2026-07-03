import requests
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
import random


def _get_face(i, gender, folder):
    if gender == "male":
        url = f"https://randomuser.me/api/portraits/men/{random.randint(1, 99)}.jpg"
    elif gender == "female":
        url = f"https://randomuser.me/api/portraits/women/{random.randint(1, 99)}.jpg"
    else:
        g = random.choice(["men", "women"])
        url = f"https://randomuser.me/api/portraits/{g}/{random.randint(1, 99)}.jpg"

    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        return None

    filename = os.path.join(folder, f"{uuid.uuid4().hex}.jpg")

    with open(filename, "wb") as f:
        f.write(r.content)

    return filename


def generate_fake_face(count=5, gender="random", folder="fake_faces"):
    os.makedirs(folder, exist_ok=True)

    files = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(
            lambda i: _get_face(i, gender, folder),
            range(count)
        ))

    for r in results:
        if r:
            files.append(r)

    return files