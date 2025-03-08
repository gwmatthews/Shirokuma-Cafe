# Setup

`pip -r requirements.txt`

(I recommend using a `venv`)

also, put an OpenAI API key into `.env` file, like in the template

# Scripts

Examples:
`python translate.py Shirokuma-Cafe-01.html en`

Uses ChatGPT to translate japanese lines of dialogue and generate a JSON file

`python apply-translation.py Shirokuma-Cafe-01.html en`

Uses the JSON and generates a new html file with the translations
