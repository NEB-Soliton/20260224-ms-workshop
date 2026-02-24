"""
Views for serving HTML pages
"""
from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    """Pomodoro timer main page"""
    return render_template('index.html')
