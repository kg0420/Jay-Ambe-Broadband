from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # This will render your main HTML page (saved in templates folder)
    return render_template('index2.html')

@app.route("/plan")
def plan():
    return render_template("plan.html")
if __name__ == '__main__':
    app.run(debug=True)
