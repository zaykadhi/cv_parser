from flask import Flask, render_template, request , jsonify
from markupsafe import escape
from flask import url_for
import os 
from werkzeug.utils import secure_filename

from resume_parser import ResumeParser, MongoDBLoader

app = Flask(__name__) 

uploaded_files_path ="uploaded_cv" 



@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST": 
        status = save_file (request)

    return render_template('index.html')

def save_file (request, file_path=uploaded_files_path):
    file = request.files['file']
    if file.filename == '':
        return {'status': 'No file selected'}

    filename = secure_filename(file.filename)
    input_path = os.path.join(file_path, filename)
    file.save(input_path)
    data = main_process (input_path)

    return jsonify({'data': data})

def main_process (input_path):
    resume_parser = ResumeParser(input_path)
    final_file_path = resume_parser.parse_resume()

    if final_file_path:
        print("Final output file:", final_file_path)

        # Initialize MongoDBLoader with your preferred database, collection names, and MongoDB Atlas URI

        database_name = "resume_data"
        collection_name = "resume_collection"
        uri = "mongodb+srv://kadhizayneb:QUj5PXn19KUjoU91@resume-parser-cluster.8alehr1.mongodb.net/?retryWrites=true&w=majority"
        loader = MongoDBLoader(database_name, collection_name, uri)

        # Load the final output JSON file into MongoDB
        loader.load_json_to_mongodb(final_file_path) 
        return  resume_parser.data_output(final_file_path)
