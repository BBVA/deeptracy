from flask import Blueprint, request, Response, json

from deeptracy.dal.project_manager import get_project_list
from deeptracy.dal.project_manager import add_project
from deeptracy.dal.database import db

project = Blueprint("project", __name__)


@project.route("/", methods=["GET"])
def get_project():
    with db.session_scope() as session:
        project_list = get_project_list(session)
        return Response(json.dumps(project_list), mimetype='application/json')


@project.route("/add", methods=["POST"])
def add_project():
    with db.session_scope() as session:
        data = request.get_json()
        project = add_project(data, session)
        return project
