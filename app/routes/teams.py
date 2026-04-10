from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tournament, Team, TeamMember
from app.decorators import roles_required

teams_bp=Blueprint("teams", __name__)

@teams_bp.route("/tournaments/<int:tournament_id>/register", methods=["GET", "POST"])
@login_required
@roles_required("team")
def register_team(tournament_id):
