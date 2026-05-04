from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = '12345'
API_URL = 'http://127.0.0.1:5000/users'

@app.route('/')
def index():
    try:
        api_response = requests.get(API_URL)
        if api_response.status_code == 200:
            responses = api_response.json()
            return render_template('index.html', users=responses)
        else:
            flash(f'API error with code: {api_response.status_code}')
    except Exception as e:
        flash(f'Loi ket noi API: {str(e)}')
        return render_template('index.html', users=[])

if __name__ == '__main__':
    app.run(port=5001, debug=True)
