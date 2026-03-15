from flask import Blueprint, render_template

tournaments_bp = Blueprint("tournaments", __name__)


@tournaments_bp.route("/tournaments")
def tournaments():
    """
    Simple view that renders the tournaments page.
    For now data is static in the template; later it can be replaced with DB data.
    """
    return render_template("tournaments.html")
