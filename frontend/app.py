from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
# import openai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
Bootstrap(app)

# OpenAI APIキーを設定
# openai.api_key = 'your_openai_api_key'

class PromptForm(FlaskForm):
    prompt = TextAreaField('Prompt', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PromptForm()
    image_url = None
    blur_targets = []
    user_response = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                file_path = os.path.join('static', 'uploads', file.filename)
                file.save(file_path)
                image_url = file_path

                # OpenAI APIに接続してblur対象を取得
                # response = openai.Completion.create(
                #     engine="text-davinci-003",
                #     prompt="describe in one brief sentence the areas of the image that need to be kept private for segmentation",
                #     max_tokens=100
                # )
                # blur_targets = response['choices'][0]['text'].strip().split('\n')
                blur_targets = ['face', 'license plate', 'address']

        # elif form.validate_on_submit():
        #     user_prompt = form.prompt.data
        #     response = openai.Completion.create(
        #         engine="text-davinci-003",
        #         prompt=user_prompt,
        #         max_tokens=100
        #     )
        #     user_response = response['choices'][0]['text'].strip()

    return render_template('index.html', form=form, image_url=image_url, blur_targets=blur_targets, user_response=user_response)

@app.route('/remove_target', methods=['POST'])
def remove_target():
    target_index = int(request.form['index'])
    blur_targets = request.form.getlist('blur_targets')
    if 0 <= target_index < len(blur_targets):
        del blur_targets[target_index]
    return jsonify(blur_targets)

if __name__ == '__main__':
    app.run(debug=True)
