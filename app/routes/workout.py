"""Workout tracking routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from datetime import datetime
from app import db
from app.models import User, WorkoutLog, SetLog
from app.routes.main import login_required
from app.utils.program_loader import ProgramLoader
from app.utils.calculations import WorkoutCalculator

bp = Blueprint('workout', __name__, url_prefix='/workout')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Display user's workout dashboard."""
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Load program
    program_path = current_app.config['PROGRAM_JSON_PATH']
    program_loader = ProgramLoader(program_path)
    
    # Get today's workout plan
    today_workout = program_loader.get_today_workout()
    
    # Get weekly statistics
    weekly_volume = WorkoutCalculator.get_weekly_volume(user_id, weeks_back=1)
    best_1rms = WorkoutCalculator.get_best_estimated_1rm(user_id, weeks_back=4)
    
    # Get recent workouts
    recent_workouts = WorkoutLog.query.filter_by(user_id=user_id).order_by(
        WorkoutLog.date.desc()
    ).limit(5).all()
    
    # Generate share link for coach view
    share_url = url_for('coach.view', token=user.share_token, _external=True)
    
    return render_template(
        'workout/dashboard.html',
        user=user,
        today_workout=today_workout,
        weekly_volume=weekly_volume,
        best_1rms=best_1rms,
        recent_workouts=recent_workouts,
        share_url=share_url
    )


@bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_workout():
    """Log a new workout."""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Get form data
        workout_name = request.form.get('workout_name')
        week_number = int(request.form.get('week_number', 1))
        split = request.form.get('split', 'A')
        notes = request.form.get('notes', '')
        date_str = request.form.get('date')
        
        # Parse date
        if date_str:
            workout_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            workout_date = datetime.utcnow().date()
        
        # Create workout log
        workout_log = WorkoutLog(
            user_id=user_id,
            date=workout_date,
            workout_name=workout_name,
            week_number=week_number,
            split=split,
            notes=notes
        )
        db.session.add(workout_log)
        db.session.flush()  # Get the ID
        
        # Parse and add sets
        set_count = 0
        for key in request.form:
            if key.startswith('exercise_'):
                parts = key.split('_')
                if len(parts) >= 3:
                    exercise_idx = parts[1]
                    field = parts[2]
                    
                    if field == 'name':
                        exercise_name = request.form.get(key)
                        
                        # Get all sets for this exercise
                        set_idx = 0
                        while True:
                            reps_key = f'exercise_{exercise_idx}_set_{set_idx}_reps'
                            weight_key = f'exercise_{exercise_idx}_set_{set_idx}_weight'
                            rpe_key = f'exercise_{exercise_idx}_set_{set_idx}_rpe'
                            
                            if reps_key not in request.form:
                                break
                            
                            reps = request.form.get(reps_key)
                            weight = request.form.get(weight_key)
                            rpe = request.form.get(rpe_key)
                            
                            if reps and weight:
                                set_log = SetLog(
                                    workout_log_id=workout_log.id,
                                    exercise_name=exercise_name,
                                    set_number=set_idx + 1,
                                    reps=int(reps),
                                    weight=float(weight),
                                    rpe=float(rpe) if rpe else None
                                )
                                db.session.add(set_log)
                                set_count += 1
                            
                            set_idx += 1
        
        db.session.commit()
        
        flash(f'Workout logged successfully! ({set_count} sets recorded)', 'success')
        return redirect(url_for('workout.dashboard'))
    
    # GET request - show form
    program_path = current_app.config['PROGRAM_JSON_PATH']
    program_loader = ProgramLoader(program_path)
    today_workout = program_loader.get_today_workout()
    today_date = datetime.utcnow().date().isoformat()
    
    return render_template('workout/log.html', today_workout=today_workout, today_date=today_date)


@bp.route('/history')
@login_required
def history():
    """View workout history."""
    user_id = session.get('user_id')
    
    # Get all workouts for user
    workouts = WorkoutLog.query.filter_by(user_id=user_id).order_by(
        WorkoutLog.date.desc()
    ).all()
    
    return render_template('workout/history.html', workouts=workouts)


@bp.route('/workout/<int:workout_id>')
@login_required
def view_workout(workout_id):
    """View details of a specific workout."""
    user_id = session.get('user_id')
    
    workout = WorkoutLog.query.filter_by(id=workout_id, user_id=user_id).first_or_404()
    summary = WorkoutCalculator.get_workout_summary(workout_id)
    
    return render_template('workout/view.html', summary=summary)


@bp.route('/api/program')
@login_required
def api_program():
    """API endpoint to get program information."""
    program_path = current_app.config['PROGRAM_JSON_PATH']
    program_loader = ProgramLoader(program_path)
    
    split = request.args.get('split', 'A')
    week = int(request.args.get('week', 1))
    day = request.args.get('day')

    workout = program_loader.get_split_workout(split, week, day_name=day)
    return jsonify(workout or {})
