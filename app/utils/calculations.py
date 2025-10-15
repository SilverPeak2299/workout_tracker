"""Utility module for workout calculations (volume, 1RM estimates, etc.)."""
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.models import WorkoutLog, SetLog


class WorkoutCalculator:
    """Perform calculations on workout data."""
    
    @staticmethod
    def estimate_1rm(weight, reps, rpe=None):
        """
        Estimate 1RM using Epley formula with optional RPE adjustment.
        
        Args:
            weight: Weight lifted
            reps: Number of reps performed
            rpe: Rate of Perceived Exertion (1-10)
        
        Returns:
            float: Estimated 1RM
        """
        if reps == 1:
            return weight
        
        # Epley formula: 1RM = weight * (1 + reps/30)
        estimated_1rm = weight * (1 + reps / 30.0)
        
        # Adjust based on RPE if provided
        if rpe is not None:
            # RPE 10 = maximal effort, RPE 7 = 3 reps in reserve
            # Adjust the estimate based on perceived difficulty
            rpe_adjustment = 1.0 + (10 - rpe) * 0.025
            estimated_1rm *= rpe_adjustment
        
        return round(estimated_1rm, 2)
    
    @staticmethod
    def calculate_volume(sets_query):
        """
        Calculate total volume (sets × reps × weight) from a query of sets.
        
        Args:
            sets_query: SQLAlchemy query result of SetLog objects
        
        Returns:
            float: Total volume
        """
        total_volume = 0
        for set_log in sets_query:
            total_volume += set_log.reps * set_log.weight
        return round(total_volume, 2)
    
    @staticmethod
    def get_weekly_volume(user_id, weeks_back=1):
        """
        Get weekly volume statistics for a user.
        
        Args:
            user_id: User ID
            weeks_back: Number of weeks to look back
        
        Returns:
            dict: Weekly volume by exercise
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        # Query sets for the date range
        sets = SetLog.query.join(WorkoutLog).filter(
            WorkoutLog.user_id == user_id,
            WorkoutLog.date >= start_date,
            WorkoutLog.date <= end_date
        ).all()
        
        # Group by exercise and calculate volume
        exercise_volumes = {}
        for set_log in sets:
            exercise = set_log.exercise_name
            volume = set_log.reps * set_log.weight
            
            if exercise not in exercise_volumes:
                exercise_volumes[exercise] = {
                    'total_volume': 0,
                    'total_sets': 0,
                    'total_reps': 0
                }
            
            exercise_volumes[exercise]['total_volume'] += volume
            exercise_volumes[exercise]['total_sets'] += 1
            exercise_volumes[exercise]['total_reps'] += set_log.reps
        
        # Round volumes
        for exercise in exercise_volumes:
            exercise_volumes[exercise]['total_volume'] = round(
                exercise_volumes[exercise]['total_volume'], 2
            )
        
        return exercise_volumes
    
    @staticmethod
    def get_best_estimated_1rm(user_id, exercise_name=None, weeks_back=4):
        """
        Get the best estimated 1RM for exercises.
        
        Args:
            user_id: User ID
            exercise_name: Specific exercise name (optional)
            weeks_back: Number of weeks to look back
        
        Returns:
            dict: Best estimated 1RM by exercise
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        # Query sets for the date range
        query = SetLog.query.join(WorkoutLog).filter(
            WorkoutLog.user_id == user_id,
            WorkoutLog.date >= start_date,
            WorkoutLog.date <= end_date
        )
        
        if exercise_name:
            query = query.filter(SetLog.exercise_name == exercise_name)
        
        sets = query.all()
        
        # Calculate 1RM for each set and keep the best per exercise
        exercise_1rms = {}
        for set_log in sets:
            exercise = set_log.exercise_name
            estimated_1rm = WorkoutCalculator.estimate_1rm(
                set_log.weight, 
                set_log.reps, 
                set_log.rpe
            )
            
            if exercise not in exercise_1rms or estimated_1rm > exercise_1rms[exercise]:
                exercise_1rms[exercise] = estimated_1rm
        
        return exercise_1rms
    
    @staticmethod
    def get_workout_summary(workout_log_id):
        """
        Get a summary of a specific workout.
        
        Args:
            workout_log_id: WorkoutLog ID
        
        Returns:
            dict: Workout summary with volume and best sets
        """
        workout = WorkoutLog.query.get(workout_log_id)
        if not workout:
            return None
        
        sets = SetLog.query.filter_by(workout_log_id=workout_log_id).all()
        
        total_volume = WorkoutCalculator.calculate_volume(sets)
        
        # Group by exercise
        exercise_data = {}
        for set_log in sets:
            exercise = set_log.exercise_name
            if exercise not in exercise_data:
                exercise_data[exercise] = {
                    'sets': [],
                    'total_volume': 0,
                    'best_estimated_1rm': 0
                }
            
            exercise_data[exercise]['sets'].append({
                'set_number': set_log.set_number,
                'reps': set_log.reps,
                'weight': set_log.weight,
                'rpe': set_log.rpe
            })
            
            volume = set_log.reps * set_log.weight
            exercise_data[exercise]['total_volume'] += volume
            
            estimated_1rm = WorkoutCalculator.estimate_1rm(
                set_log.weight, set_log.reps, set_log.rpe
            )
            if estimated_1rm > exercise_data[exercise]['best_estimated_1rm']:
                exercise_data[exercise]['best_estimated_1rm'] = estimated_1rm
        
        return {
            'workout': workout,
            'total_volume': total_volume,
            'exercises': exercise_data
        }
