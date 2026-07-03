import random
import requests


def generate_faces(count: int, gender: str = "random"):
    images = []

    print(f"🔄 Запрашиваю {count} лиц (gender={gender})")

    for i in range(count):
        if gender == "male":
            url = f"https://randomuser.me/api/portraits/men/{random.randint(1, 99)}.jpg"
        elif gender == "female":
            url = f"https://randomuser.me/api/portraits/women/{random.randint(1, 99)}.jpg"
        else:
            g = random.choice(["men", "women"])
            url = f"https://randomuser.me/api/portraits/{g}/{random.randint(1, 99)}.jpg"

        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200 and len(r.content) > 500:
                images.append(r.content)
                print(f"✅ Лицо {i + 1} загружено")
            else:
                print(f"⚠️ Лицо {i + 1} — плохой ответ")
        except Exception as e:
            print(f"❌ Ошибка {i + 1}: {e}")

    print(f"Итого загружено: {len(images)}/{count}")
    return images