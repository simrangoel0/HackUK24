from flask import Flask, jsonify, request
from fact_checker import fact_check_fn, fact_check_fn_img, fact_check_fn_video
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def fact_check():
    data = request.get_json()
    print(data)
    
    if "file" in data:
        file = data["file"]
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)
        print(f"File saved to {file_path}")

        if file.mimetype.startswith('image/'):
            print("The file is an image.")
            check = fact_check_fn_img(file_path, data["num_articles"])
        elif file.mimetype.startswith('video/'):
            print("The file is a video.")
            check = fact_check_fn_video(file_path, data["num_articles"])
        else:
            print("The file is neither an image nor a video.")
            check = fact_check_fn(data["claim"], data["num_articles"])
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temporary file {file_path} has been deleted.")
    else:
        print("No file given.")
        check = fact_check_fn(data["claim"], data["num_articles"])

    check_json = jsonify(check)
    print(check_json)
    return check_json, 200

if __name__ == '__main__':
    app.run(debug=True)