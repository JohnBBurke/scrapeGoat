import os
import time
from flask import Flask, Response
import requests
app = Flask(__name__)
@app.route('/')
def generate_large_csv():
    def generate():
        r = requests.get('http://httpbin.org/stream/20', stream=True)
        for row in r.iter_lines():
            yield ','.join(row) + '\n'
    return Response(generate(), mimetype='text/csv')


if __name__ == "__main__":
    app.run()