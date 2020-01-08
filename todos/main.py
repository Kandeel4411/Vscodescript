import json
import os
import sys
import pathlib as pl

from bs4 import BeautifulSoup
from flask import Flask, render_template, abort, Response
import mistune

app = Flask(__name__)

CONFIG_PATH, PROJECT_NAME = sys.argv[1:]


@app.route("/")
def todos():
    todos = get_todos(project=PROJECT_NAME)
    return render_template("todo.html", todos=todos)


def get_todos(project):
    try:
        with open(CONFIG_PATH) as c:
            config = json.load(c)
            project_dir = pl.Path(config["PROJECT_DIR"])

            if project == "all":
                return [
                    (p, project_todos(project_dir=project_dir / p))
                    for p in os.listdir(project_dir)
                ]
            else:
                return [project, project_todos(project_dir=project_dir / project)]
    except FileNotFoundError:
        abort(Response("Config file was not found. Consider using 'vs init' first."))
    except Exception as e:
        print(e)
        abort(Response(f"An unexpected error occurred."))


def project_todos(project_dir):
    try:
        with pl.Path.open(project_dir / ".todo") as todos:
            html_list = mistune.markdown(todos.read())
            todo_html = BeautifulSoup(html_list, "html.parser")
            return [item.get_text() for item in todo_html.find_all("li")]
    except FileNotFoundError:
        return ["Project doesn't contain .todos file."]
    except Exception as e:
        print(e)
        abort(Response(f"An unexpected error occurred."))


@app.route("/call/<project>")
def call_back(project):
    try:
        os.system(f"vs.py project {project}")
    except Exception as e:
        print(e)
        abort(Response(f"An unexpected error occurred."))
    else:
        return "Success"


if __name__ == "__main__":
    app.run(debug=True)
