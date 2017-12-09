import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def index():
    if request.args:
        d = {i: request.args[i] for i in request.args}
        with open('answers.json', 'r', encoding='utf-8') as f:
            answers = json.load(f)
        answers.append(d)
        with open('answers.json', 'w', encoding='utf-8') as f:
            json.dump(answers, f, ensure_ascii=False, indent=4)
        return redirect('/thanks')

    return render_template('home.html')


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/json')
def results():
    with open('answers.json', 'r', encoding='utf-8') as f:
        results = f.read()
    return results


@app.route('/search')
def search():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
