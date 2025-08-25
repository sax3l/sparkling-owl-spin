from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form.get('name')
        return f"<h1>Hello, {name}!</h1>"
    return render_template_string(open('templates/form.html').read())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)