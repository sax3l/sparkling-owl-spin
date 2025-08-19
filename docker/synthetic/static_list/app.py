from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    items = [f"Item {i}" for i in range(1, 21)]
    html = "<h1>Static List</h1><ul>"
    for item in items:
        html += f"<li>{item}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)