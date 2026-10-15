
from PIL import Image, ImageDraw, ImageFont
import os
import re


def save_image(image,name="img",direc="images"):
    """Save the PIL image in the given directory and at the bottom of the image is the prompt saved in name"""
    os.makedirs(direc, exist_ok=True)

    font = ImageFont.load_default(size=18)
    padding = 10
    draw = ImageDraw.Draw(image)

    # wrap the caption so each line fits the image width
    lines, line = [], ""
    for word in name.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= image.width - 2 * padding:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)

    # new canvas: original image on top, white strip with the caption below
    line_height = font.size + 4
    strip_height = len(lines) * line_height + 2 * padding
    captioned = Image.new("RGB", (image.width, image.height + strip_height), "white")
    captioned.paste(image, (0, 0))
    draw = ImageDraw.Draw(captioned)
    for i, text in enumerate(lines):
        draw.text((padding, image.height + padding + i * line_height), text, fill="black", font=font)

    # file name from the prompt, without overwriting earlier images
    stem = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")[:50] or "img"
    path = os.path.join(direc, f"{stem}.png")
    counter = 1
    while os.path.exists(path):
        path = os.path.join(direc, f"{stem}_{counter}.png")
        counter += 1

    captioned.save(path)
    print(f"Image Saved: {path}")
