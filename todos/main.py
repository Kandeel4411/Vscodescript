import sys

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def todos():
    project = sys.argv[1]
    if project == "all":
        todos = get_todos()
    else:
        todos = get_todos(project=project)

    return render_template("todo.html", todos=todos)


def get_todos(project="all"):
    # TODO
    return []


if __name__ == "__main__":
    app.run(debug=True)
