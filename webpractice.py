from flask import Flask, render_template, jsonify, render_template_string
from change_json import add_t_json, chn_param_json, del_cmd
app = Flask(__name__)


def log_page_css():
    css = """
    .button{
  background-color: #008CBA;
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
};
    #tableDiv {
    background-color: white;
    width: 50%;
    }
    """
    return css


def log_page(page_name: str, logs: list):
    td = ""
    for log in logs:
        td = td + f'<tr><td>{log}</td></tr>'
    table = f'<table id="tableId">\n{td}\n<table>'

    page = f"""
    <html>
    <head>
    <style>
    {log_page_css()}
    </style>
    </head>
    <body>
    <h1>{page_name}</h1>
    <div id="tableDiv" class="wrapper">
    {table}
    </div>
    <br>
    <br>
    <div id="box" class="box">
        <button id="button" class="button" onclick="location.href='http://192.168.1.188:80/';"> return to main page </button>
    </div>
    </body>
    </html>
    """
    return page


def read_file(log_type: str):
    """
    read the log file and save the last 10 logs by there type
    :return: only the type requested (WARNING, ERrOR, INFO)
    """
    logs = []
    last = 10
    with open('wl_log.log', 'r') as f:
        lines = f.read().split('\n')
    last_lines = lines[-last:-1]
    for line in last_lines:
        if log_type in line:
            logs.append(line)
    if not logs:
        logs.append(f'no logs to show from last {last} logs')
    return logs


@app.route('/change')
def change():
    return render_template("change_json_page.html")


@app.route('/error')
def error():
    errors = read_file('ERROR')
    return render_template_string(log_page('Error logs', errors))


@app.route('/warning')
def warning():
    warnings = read_file('WARNING')
    return render_template_string(log_page('Warning logs', warnings))


@app.route('/info')
def info():
    infos = read_file('INFO')
    return render_template_string(log_page('Info logs', infos))


@app.route('/')
def home():
    return render_template("cubes_page.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
