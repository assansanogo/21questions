# python_code/app.py
from flask import Flask
app = Flask(__name__)

# route principale
@app.route('/')
def hello_world():
    return('Hey, we have Flask in a Docker container!')

# execute the app si le contexte est main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)