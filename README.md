# AIB

AIB: Automated Images Blurring

## usage

1. make .env file
   owing environment variables

```sh
touch .env
echo "GEMINI_API_KEY=your gemini api key" >> .env
```

2. make python virtual environment

```sh
pyenv virtualenv 3.10.0 aib
pyenv local aib
```

3. install dependencies

```sh
pip install -r requirements.txt
```

4. run

```sh
python main.py
```
