from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# IMPORT ALL MODELS
from .user import User
from .team import Team
from .team_member import TeamMember
from .tournament import Tournament
from .round import Round
from .submission import Submission
from .evaluation import Evaluation
from .leaderboard import Leaderboard