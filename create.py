# write-html.py
from flask import Flask, render_template, jsonify, render_template_string

app = Flask(__name__)



message = """<html>
<head></head>
<body><p>Hello World!</p></body>
</html>"""

@app.route('/')
def home():
    return render_template_string(message)


if __name__ == '__main__':
    app.run(host="localhost", port=80)
