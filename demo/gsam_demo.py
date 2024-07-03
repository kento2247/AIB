import base64
import os
from io import BytesIO
from types import SimpleNamespace

import cv2
import requests
from PIL import Image

config = SimpleNamespace()
config.gsam_api_url = "http://172.18.102.33:5000/segment"


def gsam_demo(image_path, text_prompt):
    """
    image_path: Path to the image file
    text_prompt: Text prompt for the model
    """
    image = cv2.imread(image_path)
    # Ensure the image was correctly loaded
    if image is None:
        raise FileNotFoundError(f"Error: Could not read image file '{image_path}'")
    # Encode image to base64
    _, buffer = cv2.imencode(".jpg", image)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    response = requests.post(
        config.gsam_api_url, json={"image": base64_image, "text_prompt": text_prompt}
    )
    # return jsonify({"mask": mask_base64, "labels": pred_phrases})
    mask_base64 = response.json()["mask"]
    mask = Image.open(BytesIO(base64.b64decode(mask_base64)))
    labels = response.json()["labels"]

    # Save the mask image
    mask.save("output_mask.jpg")
    print(labels)


gsam_demo("images/komei01.jpg", "face")
