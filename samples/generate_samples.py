"""
Generate sample images + questions for cv-20 Multimodal Image QA.
Run: pip install Pillow && python generate_samples.py
Output: 5 images + questions.txt with suggested questions per image.
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(__file__)


def make_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def save(img, name):
    img.save(os.path.join(OUT, name))
    print(f"  created: {name}")


def kitchen():
    img = Image.new("RGB", (500, 400), (240, 230, 220))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 320, 500, 400], fill=(160, 140, 110))
    d.rectangle([0, 260, 500, 325], fill=(200, 180, 150))
    # red apple on counter
    d.ellipse([200, 220, 260, 270], fill=(220, 50, 50))
    d.rectangle([227, 210, 233, 225], fill=(60, 140, 40))
    # blue mug
    d.rectangle([310, 225, 360, 270], fill=(60, 100, 200))
    d.arc([350, 235, 375, 260], start=270, end=90, fill=(60, 100, 200), width=5)
    # yellow banana
    d.arc([100, 230, 190, 270], start=200, end=340, fill=(220, 200, 50), width=12)
    d.text((10, 370), "Kitchen scene", fill=(80, 80, 80))
    return img


def park():
    img = Image.new("RGB", (500, 400), (135, 200, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 280, 500, 400], fill=(80, 160, 60))
    # red bench
    d.rectangle([180, 260, 320, 275], fill=(180, 60, 40))
    d.rectangle([185, 275, 200, 300], fill=(140, 40, 20))
    d.rectangle([305, 275, 320, 300], fill=(140, 40, 20))
    # green tree
    d.rectangle([380, 200, 395, 285], fill=(100, 70, 40))
    d.ellipse([340, 140, 435, 215], fill=(40, 140, 40))
    # yellow sun
    d.ellipse([40, 30, 100, 90], fill=(255, 220, 50))
    # white cloud
    d.ellipse([200, 40, 300, 90], fill=(255, 255, 255))
    d.ellipse([220, 25, 280, 70], fill=(255, 255, 255))
    d.text((10, 370), "Park scene", fill=(40, 80, 40))
    return img


def living_room():
    img = Image.new("RGB", (500, 400), (230, 220, 210))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 330, 500, 400], fill=(160, 140, 110))
    # blue sofa
    d.rectangle([40, 230, 300, 340], fill=(60, 100, 180))
    d.rectangle([40, 205, 300, 240], fill=(80, 120, 200))
    # black tv
    d.rectangle([340, 80, 490, 220], fill=(20, 20, 20))
    d.rectangle([350, 90, 480, 210], fill=(30, 60, 100))
    # orange cat on sofa
    d.ellipse([160, 195, 220, 240], fill=(220, 130, 50))
    d.ellipse([175, 180, 205, 210], fill=(220, 130, 50))
    d.text((10, 370), "Living room", fill=(80, 80, 80))
    return img


def street():
    img = Image.new("RGB", (600, 400), (135, 180, 220))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 280, 600, 400], fill=(80, 80, 80))
    for x in range(0, 600, 80):
        d.rectangle([x, 330, x + 50, 345], fill=(255, 255, 255))
    # red car
    d.rectangle([60, 295, 220, 345], fill=(200, 50, 50))
    d.polygon([(90, 295), (110, 255), (190, 255), (210, 295)], fill=(200, 50, 50))
    for wx in [90, 190]:
        d.ellipse([wx - 20, 335, wx + 20, 370], fill=(30, 30, 30))
    # stop sign
    d.polygon([(480, 180), (500, 160), (520, 160), (540, 180), (540, 200),
               (520, 220), (500, 220), (480, 200)], fill=(200, 40, 40))
    d.text((10, 370), "Street scene", fill=(240, 240, 240))
    return img


def farm():
    img = Image.new("RGB", (500, 400), (135, 200, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 280, 500, 400], fill=(100, 160, 60))
    # red barn
    d.rectangle([60, 160, 220, 290], fill=(180, 50, 40))
    d.polygon([(40, 160), (140, 80), (240, 160)], fill=(140, 30, 20))
    d.rectangle([120, 220, 160, 290], fill=(100, 70, 40))
    # white cow
    d.ellipse([280, 220, 400, 290], fill=(240, 240, 240))
    d.ellipse([380, 200, 420, 240], fill=(240, 240, 240))
    d.line([295, 290, 295, 320], fill=(200, 200, 200), width=4)
    d.line([330, 290, 330, 320], fill=(200, 200, 200), width=4)
    d.line([360, 290, 360, 320], fill=(200, 200, 200), width=4)
    d.line([390, 290, 390, 320], fill=(200, 200, 200), width=4)
    d.text((10, 370), "Farm scene", fill=(40, 80, 40))
    return img


QUESTIONS = {
    "sample_kitchen.jpg": [
        "What fruit is on the counter?",
        "What color is the mug?",
        "How many items are on the counter?",
        "Is there a banana in the image?",
    ],
    "sample_park.jpg": [
        "What color is the bench?",
        "Is there a tree in the image?",
        "What is the weather like?",
        "What color is the sun?",
    ],
    "sample_living_room.jpg": [
        "What color is the sofa?",
        "Is there a cat in the image?",
        "What is on the wall?",
        "What color is the TV screen?",
    ],
    "sample_street.jpg": [
        "What color is the car?",
        "Is there a traffic sign?",
        "What is the road surface made of?",
        "How many cars are visible?",
    ],
    "sample_farm.jpg": [
        "What animal is in the image?",
        "What color is the barn?",
        "Is there a cow?",
        "What color is the grass?",
    ],
}

if __name__ == "__main__":
    print("Generating cv-20 samples...")
    save(kitchen(), "sample_kitchen.jpg")
    save(park(), "sample_park.jpg")
    save(living_room(), "sample_living_room.jpg")
    save(street(), "sample_street.jpg")
    save(farm(), "sample_farm.jpg")

    # Write questions file
    qpath = os.path.join(OUT, "questions.txt")
    with open(qpath, "w") as f:
        for img_name, questions in QUESTIONS.items():
            f.write(f"\n=== {img_name} ===\n")
            for q in questions:
                f.write(f"  - {q}\n")
    print(f"  created: questions.txt")
    print("Done — 5 images + questions.txt in samples/")
