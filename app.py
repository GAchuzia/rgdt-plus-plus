from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os

PORT: int = 8080
UPLOAD_FOLDER: str = "./tests"
ALLOWED_EXTENSIONS: list[str] = ["xml", "json"]
app = Flask(__name__, template_folder="web", static_folder="web")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allow cross-origin resource sharing for simplicity
CORS(app)


def allowed_file(filename: str):
    """Checks if file is of an allowed type."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/output")
def output():
    return render_template("output.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    # check if the post request has the file part
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["file"]
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return redirect(url_for("download_file", name=filename))


if __name__ == "__main__":
    app.run(port=PORT, host="0.0.0.0")
