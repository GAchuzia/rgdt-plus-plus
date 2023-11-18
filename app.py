from flask import Flask, render_template

PORT: int = 8080
app = Flask(__name__, template_folder="web", static_folder="web")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=PORT, debug=True)
