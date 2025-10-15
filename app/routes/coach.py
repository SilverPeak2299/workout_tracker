"""Coach view routes for read-only access via shareable links."""
from flask import Blueprint, render_template, abort
from app.models import User, WorkoutLog
from app.utils.calculations import WorkoutCalculator

bp = Blueprint('coach', __name__, url_prefix='/coach')


@bp.route('/view/<token>')
def view(token):
    """Read-only coach view accessible via shareable token."""
    # Find user by share token
    user = User.query.filter_by(share_token=token).first()
    
    if not user:
        abort(404)
    
    # Get weekly statistics
    weekly_volume = WorkoutCalculator.get_weekly_volume(user.id, weeks_back=1)
    best_1rms = WorkoutCalculator.get_best_estimated_1rm(user.id, weeks_back=4)
    
    # Get recent workouts
    recent_workouts = WorkoutLog.query.filter_by(user_id=user.id).order_by(
        WorkoutLog.date.desc()
    ).limit(10).all()
    
    return render_template(
        'coach/view.html',
        user=user,
        weekly_volume=weekly_volume,
        best_1rms=best_1rms,
        recent_workouts=recent_workouts
    )


@bp.route('/workout/<token>/<int:workout_id>')
def view_workout(token, workout_id):
    """View details of a specific workout in coach view."""
    # Find user by share token
    user = User.query.filter_by(share_token=token).first()
    
    if not user:
        abort(404)
    
    # Get workout (must belong to this user)
    workout = WorkoutLog.query.filter_by(id=workout_id, user_id=user.id).first_or_404()
    summary = WorkoutCalculator.get_workout_summary(workout_id)
    
    return render_template('coach/workout.html', summary=summary, token=token)
