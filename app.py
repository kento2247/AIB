import os

import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from PIL import Image
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
Bootstrap(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class PromptForm(FlaskForm):
    prompt = TextAreaField("Prompt", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():
    form = PromptForm()
    image_url = None
    blur_targets = []
    user_response = None

    # if request.method == "POST":
    #     if "file" in request.files:
    #         file = request.files["file"]
    #         if file:
    # file_path = os.path.join("static", "uploads", file.filename)
    # file.save(file_path)
    # image_url = file_path
    # response = model.generate_content(
    #     [
    #         "describe in one brief sentence the areas of the image that need to be kept private for segmentation",
    #         img,
    #     ]
    # )
    # blur_targets = response.split(", ")
    # print(blur_targets)

    # elif form.validate_on_submit():
    #     user_prompt = form.prompt.data
    #     response = openai.Completion.create(
    #         engine="text-davinci-003",
    #         prompt=user_prompt,
    #         max_tokens=100
    #     )
    #     user_response = response['choices'][0]['text'].strip()

    return render_template(
        "index.html",
        form=form,
        image_url=image_url,
        blur_targets=blur_targets,
        user_response=user_response,
    )


@app.route("/gemini_response", methods=["POST"])
def gemini_response():
    img = request.form["image"]
    response = model.generate_content(
        [
            "List the areas of the image that need to be kept private for segmentation. Just respond with area names, e.g., \"'face', 'license plate'\".",
            img,
        ]
    )
    return response


@app.route("/remove_target", methods=["POST"])
def remove_target():
    target_index = int(request.form["index"])
    blur_targets = request.form.getlist("blur_targets")
    if 0 <= target_index < len(blur_targets):
        del blur_targets[target_index]
    return jsonify(blur_targets)


@app.route("/demo", methods=["GET", "POST"])
def demo():
    if request.method == "POST":
        if "image" not in request.files:
            return jsonify({"error": "No file part"}), 400

        img_file = request.files["image"]
        if img_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # 画像ファイルをPIL Image形式に変換
        img = Image.open(img_file)

        # 必要に応じて一時ファイルに保存する場合
        file_path = os.path.join(UPLOAD_FOLDER, img_file.filename)
        img.save(file_path)

        # モデルに渡すために必要な処理をここで行う
        # ここではimgをそのまま使っていることを想定
        response = model.generate_content(
            [
                "List the areas of the image that need to be kept private for segmentation. Just respond with area names, e.g., \"'face', 'license plate'\".",
                img,  # PIL Imageオブジェクトを渡す
            ]
        )
        print(response.text)
        return jsonify({"response": response.text}), 200
    elif request.method == "GET":
        return render_template("demo.html")


if __name__ == "__main__":
    app.run(debug=True)
