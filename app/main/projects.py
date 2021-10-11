# -*- coding: UTF-8 -*-

from flask import render_template
from app.main import bp

@bp.route('/projects/projects')
def get_projects():
    return render_template('projects/projects.html')

@bp.route('/projects/project')
def get_project():
    return render_template('projects/project.html')

@bp.route('/projects/add_project')
def add_project():
    return render_template('projects/add_project.html')

@bp.route('/projects/edit_project')
def edit_project_n():
    return render_template('projects/edit_project.html')