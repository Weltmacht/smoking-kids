import requests
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SOURCE_IMAGES_PREFIX="https://img.izismile.com/img/img2/20090821/smoking_kids"
IZISMILE_SOURCE_RANGE=50


def build_izi_image_list() -> list:
    collatedlist = []

    for i in range(0, IZISMILE_SOURCE_RANGE):
        # Ignore #19, kid is too inappropriate
        if verify_image_exists(SOURCE_IMAGES_PREFIX+f"_{str(i).zfill(2)}.jpg") and i != 19:
            collatedlist.insert(1, SOURCE_IMAGES_PREFIX+f"_{str(i).zfill(2)}.jpg")
    return collatedlist

def verify_image_exists(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)
        # logging.info(f"IMAGE Found: {url}")
        return response.status_code == 200
    except requests.RequestException:
        return False

def inspirational_quote() -> tuple[str, str]:
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
        else:
            raise Exception
    except Exception:
        logging.error(f"No quote found!")
    return data[0]["q"], data[0]["a"]

def main():
    webhook_urls = get_env_data_as_dict('.env').get("WEBHOOK_URL").split(',')
    izi_image_list = build_izi_image_list()
    random_image_url = random.randint(0, len(izi_image_list)-1)
    image = izi_image_list[random_image_url]
    quote, author = inspirational_quote()
    logging.info(f"{image, quote, author}")

    payload = {
        "content": f"{quote} — {author}",
        "embeds": [
            {
                "image": {"url": image}
            }
        ]
    }

    for webhook_url in webhook_urls:
        requests.post(webhook_url, json=payload)

### Helper Funcs
def get_env_data_as_dict(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            return dict(tuple(line.replace('\n', '').strip().split('=')) for line
                in f.readlines() if not line.startswith('#') if not line == '\n')
    except: 
        logging.error("You need to include the .env file")

if __name__ == "__main__":
    main()
