from flask import Flask, request, render_template, Response
from flask_cors import CORS, cross_origin
  
app = Flask(__name__,template_folder="templates") 


# Webpage route
@app.route("/", methods=["GET"])
def index():
    """The homepage of the website where HTML will be served."""
    return render_template("index.html")


# API Routes
@app.route("/upload", methods=["POST"])
@cross_origin()
def upload():
    """API route for uploading JSON and XML file"""

    file = request.files.get("file")
    if file is None:
        return Response(status=400)  # Bad request (no file given)
    
    
    

    

