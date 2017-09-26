from flask import Blueprint, request, Response, json

from deeptracy.dal.project import get_project_list, add_project
from deeptracy.dal.database import db

project = Blueprint("project", __name__)


@project.route("/", methods=["GET"])
def get_project():
    with db.session_scope() as session:
        project_list = get_project_list(session)
        return json.dumps([item.to_dict() for item in project_list])


@project.route("/add", methods=["POST"])
def add_project():
    with db.session_scope() as session:
        data = request.get_json()
        project = add_project(data, session)
        return project
