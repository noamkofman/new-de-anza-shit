from flask import Flask, Response
import os

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response



@app.route("/")
def root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    return Response(html, mimetype="text/html")

if __name__=="__main__":
    app.run(debug=True, port=8080)
