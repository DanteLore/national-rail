from flask import Flask

# http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello world of trains!"


if __name__ == '__main__':
    app.run(debug=True)
