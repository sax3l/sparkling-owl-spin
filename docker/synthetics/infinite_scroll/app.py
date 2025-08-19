from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(open('static/index.html').read())

@app.route('/data')
def data():
    page = int(request.args.get('page', 1))
    items = [f"Item {(page - 1) * 10 + i}" for i in range(1, 11)]
    return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)