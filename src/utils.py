import base64
import os
import uuid
from io import BytesIO
from types import SimpleNamespace

import cv2
import google.generativeai as genai
import requests
import yaml
from dotenv import load_dotenv
from PIL import Image


class aib:
    def __init__(self, session_id=None):
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = str(uuid.uuid4())
        load_dotenv()
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.config = self.get_config("config.yaml")
        self.init_prompt = self.config.init_prompt
        self.upload_path = os.path.join(self.config.upload_folder, self.session_id)
        self.mask_path = os.path.join(self.config.mask_folder, self.session_id)
        self.output_path = os.path.join(self.config.output_folder, self.session_id)
        self.upload_path += ".jpg"
        self.mask_path += ".jpg"
        self.output_path += ".jpg"

    def get_config(self, file_path):
        # return SimpleNamespace object from yaml file
        with open(file_path) as file:
            data = yaml.safe_load(file)

        def dict_to_namespace(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    d[key] = dict_to_namespace(value)
                return SimpleNamespace(**d)
            return d

        return dict_to_namespace(data)

    def mosaic_image(
        self, image_path, mask_path, scale=0.04, save_path="images/mosaic_image.jpg"
    ):
        """
        画像にモザイク処理を適用する
        :param image_path: 入力画像のパス
        :param mask_path: マスク画像のパス
        :param scale: 縮小・拡大のスケール（0.1は10%に縮小し、その後10倍に拡大）
        :param save_path: 結果画像の保存パス
        """
        # 画像とマスクの読み込み
        image = cv2.imread(image_path)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

        # 画像またはマスクの読み込みに失敗した場合の処理
        if image is None:
            raise FileNotFoundError(f"Error: Could not read image file '{image_path}'")
        if mask is None:
            raise FileNotFoundError(f"Error: Could not read mask file '{mask_path}'")

        # 画像のサイズを取得
        h, w = image.shape[:2]

        # マスクされた領域を抽出
        masked_image = cv2.bitwise_and(image, image, mask=mask)

        small_image = cv2.resize(
            masked_image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_LINEAR,
        )
        # 縮小した画像を再拡大してモザイク効果を適用
        mosaic_image = cv2.resize(small_image, (w, h), interpolation=cv2.INTER_NEAREST)

        # モザイク領域をマスクとして作成
        mosaic_mask = cv2.inRange(mosaic_image, 0, 255)

        # 元の画像からモザイクを適用する部分を取り除く
        clear_image_part = cv2.bitwise_and(image, image, mask=mosaic_mask)
        # # モザイク領域と元の画像の統合
        result = cv2.add(clear_image_part, mosaic_image)

        cv2.imwrite(save_path, result)
        return

    def blur_image(
        self,
        image_path,
        mask_path,
        blur_radius=30,
        save_path="images/blurred_image.jpg",
    ):
        image = cv2.imread(image_path)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        _, binary_mask = cv2.threshold(
            mask, 127, 255, cv2.THRESH_BINARY
        )  # マスクを2値化する
        blurred_image = cv2.GaussianBlur(
            image, (23, 23), blur_radius
        )  # ぼかし処理を適用
        blurred_area = cv2.bitwise_and(
            blurred_image, blurred_image, mask=binary_mask
        )  # ぼかし領域をマスクで選択
        inverse_mask = cv2.bitwise_not(binary_mask)  # マスクの反転を作成
        original_area = cv2.bitwise_and(
            image, image, mask=inverse_mask
        )  # 元の画像のマスク外領域を選択
        final_image = cv2.add(blurred_area, original_area)  # ぼかし領域と元の領域を合成
        cv2.imwrite(save_path, final_image)  # ぼかした画像を保存する場合

    def gsam_api(self, image_path, text_prompt, save_path="images/mask.jpg"):
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
            self.config.gsam_api_url,
            json={"image": base64_image, "text_prompt": text_prompt},
        )
        # return jsonify({"mask": mask_base64, "labels": pred_phrases})
        mask_base64 = response.json()["mask"]
        mask = Image.open(BytesIO(base64.b64decode(mask_base64)))
        labels = response.json()["labels"]

        # Save the mask image
        mask.save(save_path)
        return labels

    def gemini_api(self, image_path, prompt):
        img = Image.open(image_path)
        result = self.model.generate_content([prompt, img])

        # return result.text

        result_list = eval(result.text)
        # tuple型だったら，"this photo shows ... and ..."の形にする
        if type(result_list) == tuple:
            # 重複があれば削除
            result_list = list(set(result_list))
            result_str = ""
            length = len(result_list)
            for i, r in enumerate(result_list):
                result_str += r
                if i != length - 1:
                    result_str += " and "
            print(result_str)

        else:
            result_str = result.text

        return result_str

    def all(self, img_file):
        img = Image.open(img_file)
        img.save(self.upload_path)
        assistant = self.gemini_api(
            self.upload_path,
            self.init_prompt,
        )
        self.mask_labels = self.gsam_api(
            self.upload_path,
            assistant,
            self.mask_path,
        )
        # self.mosaic_image(self.upload_path, self.mask_path, save_path=self.output_path)
        self.blur_image(self.upload_path, self.mask_path, save_path=self.output_path)
        return self.session_id, self.output_path, self.mask_labels

    def fix(self, prompt, mask_labels: list[list[str]]):
        new_labels = self.gsam_api(self.output_path, prompt, self.mask_path)
        self.mask_labels = mask_labels + new_labels
        # self.mosaic_image(self.output_path, self.mask_path, save_path=self.output_path)
        self.blur_image(self.output_path, self.mask_path, save_path=self.output_path)
        return self.session_id, self.output_path, self.mask_labels

    def __del__(self):
        # imageを削除
        try:
            os.remove(self.mask_path)
            os.remove(self.upload_path)  # fixの場合不要
            # os.remove(self.output_path)
        except:
            pass
        return
