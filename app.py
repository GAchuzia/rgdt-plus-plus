from flask import Flask, render_template
from flask_cors import CORS

PORT: int = 8080
UPLOAD_FOLDER: str = "./tests"
ALLOWED_EXTENSIONS: list[str] = ["xml", "json"]
app = Flask(__name__, template_folder="web", static_folder="web")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allow cross-origin resource sharing for simplicity
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/output")
def output():
    return render_template("output.html")


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
