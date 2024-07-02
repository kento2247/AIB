import base64
from io import BytesIO

import requests
from PIL import Image


def get_gemini_response(base64_image):
    url = "http://127.0.0.1:5000/gemini_response"
    response = requests.post(url, json={"image": base64_image})
    print(response.json())


def demo():
    img_path = "images/komei01.jpg"
    # 画像をbase64エンコード
    with open(img_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    get_gemini_response(base64_image)

    # url = "http://127.0.0.1:5000/"
    # payload = {"image": base64_image, "text_prompt": "face"}
    # headers = {"Content-Type": "application/json"}

    # response = requests.post(url, json=payload, headers=headers)
    # print(response.json())

    # # exit()
    # data = response.json()
    # mask_base64 = data["mask"]
    # labels = data["labels"]

    # mask_data = base64.b64decode(mask_base64)
    # mask_image = Image.open(BytesIO(mask_data))
    # # mask_image.show()  # またはmask_image.save('output_mask.jpg')で保存
    # # save mask image
    # mask_image.save("output_mask.jpg")

    # print(labels)


demo()
