from flask import Flask, jsonify, request
from fact_checker import fact_check_fn

app = Flask(__name__)

@app.route('/', methods=['POST'])
def fact_check():
    data = request.get_json()
    print(data)
    check = fact_check_fn(data["claim"], data["num_articles"])
    check2 = check[8:len(check)-4]
    check_json = jsonify(check2)
    print(check_json)
    return check_json, 200

if __name__ == '__main__':
    app.run(debug=True)