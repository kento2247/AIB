import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

import src.utils as utils

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
Bootstrap(app)


class PromptForm(FlaskForm):
    prompt = TextAreaField("Prompt", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/demo", methods=["GET", "POST"])
def demo():
    if request.method == "POST":
        if "image" not in request.files:
            prompt = request.form["prompt"]
            session_id = request.form["session_id"]
            label_list = request.form["label_list"]
            label_list = eval(label_list)
            aib = utils.aib(session_id)
            session_id, output_path, label_list = aib.fix(prompt, label_list)
            return render_template(
                "demo_result.html",
                image=output_path,
                session_id=session_id,
                label_list=label_list,
            )
        else:
            img_file = request.files["image"]
            if img_file.filename == "":
                return jsonify({"error": "No selected file"}), 400
            aib = utils.aib()
            session_id, output_path, label_list = aib.all(img_file)
            return render_template(
                "demo_result.html",
                image=output_path,
                session_id=session_id,
                label_list=label_list,
            )
    elif request.method == "GET":
        output_path = "static/outputs/sample.jpg"
        session_id = "sample"
        label_list = [["face", "0.4"], ["face", "0.2"]]
        return render_template(
            "demo_result.html",
            image=output_path,
            session_id=session_id,
            label_list=label_list,
        )


if __name__ == "__main__":
    app.run(port=3000)
