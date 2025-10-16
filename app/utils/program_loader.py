"""Utility module for loading and processing workout programs from JSON."""
import json
from datetime import datetime


def _value_for_week(values, week_in_cycle):
    """Helper to safely pick a value for a given week in the cycle."""
    if not isinstance(values, (list, tuple)) or not values:
        return values

    index = max(min(week_in_cycle - 1, len(values) - 1), 0)
    return values[index]


class ProgramLoader:
    """Load and manage workout programs from JSON files."""
    
    def __init__(self, json_path):
        """Initialize the program loader with a JSON file path."""
        self.json_path = json_path
        self.program = self._load_program()
        self.uses_session_structure = 'sessions' in self.program and 'weeks' in self.program
    
    def _load_program(self):
        """Load the program from JSON file."""
        try:
            with open(self.json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return a default program structure if file doesn't exist
            return self._get_default_program()
    
    def _get_default_program(self):
        """Return a default program structure."""
        return {
            "name": "Default 3+1 Program",
            "description": "Alternating A/B weeks with progressive load and deload.",
            "cycle_weeks": 4,
            "weeks": {
                "A": {
                    "Monday": "strength_day",
                    "Thursday": "upper_pull",
                    "Saturday": "conditioning"
                },
                "B": {
                    "Monday": "strength_day",
                    "Thursday": "upper_push",
                    "Saturday": "conditioning"
                }
            },
            "sessions": {
                "strength_day": {
                    "name": "Lower Body Strength",
                    "description": "Main lower body strength session.",
                    "exercises": [
                        {"name": "Back Squat", "sets": [4, 4, 4, 3], "reps": [6, 5, 4, 6]},
                        {"name": "Romanian Deadlift", "sets": [3, 3, 3, 2], "reps": [8, 8, 6, 8]},
                        {"name": "Split Squat", "sets": [3, 3, 3, 2], "reps": [10, 10, 8, 10]}
                    ]
                },
                "upper_pull": {
                    "name": "Upper Pull Focus",
                    "description": "Back and posterior chain accessories.",
                    "exercises": [
                        {"name": "Pull Ups", "sets": [3, 3, 3, 2], "reps": [8, 8, 6, 8]},
                        {"name": "Barbell Row", "sets": [3, 3, 3, 2], "reps": [10, 8, 8, 10]},
                        {"name": "Face Pull", "sets": [3, 3, 3, 2], "reps": [15, 15, 12, 15]}
                    ]
                },
                "upper_push": {
                    "name": "Upper Push Focus",
                    "description": "Horizontal and vertical pressing.",
                    "exercises": [
                        {"name": "Bench Press", "sets": [4, 4, 4, 3], "reps": [8, 6, 5, 8]},
                        {"name": "Overhead Press", "sets": [3, 3, 3, 2], "reps": [10, 8, 6, 10]},
                        {"name": "Dip", "sets": [3, 3, 3, 2], "reps": [12, 10, 8, 12]}
                    ]
                },
                "conditioning": {
                    "name": "Conditioning & Core",
                    "description": "Light conditioning with core work.",
                    "exercises": [
                        {"name": "Bike Sprint", "sets": [6, 6, 6, 4], "reps": [20, 20, 20, 15]},
                        {"name": "Plank", "sets": [3, 3, 3, 3], "reps": [45, 45, 45, 30]},
                        {"name": "Side Plank", "sets": [2, 2, 2, 2], "reps": [30, 30, 30, 20]}
                    ]
                }
            }
        }
    
    def get_program_info(self):
        """Get basic program information."""
        return {
            'name': self.program.get('name', 'Unknown Program'),
            'description': self.program.get('description', ''),
            'cycle_weeks': self.program.get('cycle_weeks', 4)
        }
    
    def get_split_names(self):
        """Get the names of available splits."""
        if self.uses_session_structure:
            weeks = self.program.get('weeks', {})
            return {key: f'Week {key}' for key in weeks.keys()}

        splits = self.program.get('splits', {})
        return {key: split.get('name', f'Split {key}') for key, split in splits.items()}

    def _calculate_cycle_metrics(self, user_start_date):
        """Calculate shared metrics for determining the current program week."""
        if user_start_date is None:
            user_start_date = datetime.utcnow().date()

        today = datetime.utcnow().date()
        days_elapsed = max((today - user_start_date).days, 0)
        weeks_elapsed = days_elapsed // 7

        cycle_weeks = self.program.get('cycle_weeks', 4) or 4
        week_in_cycle = (weeks_elapsed % cycle_weeks) + 1

        return today, weeks_elapsed, week_in_cycle, cycle_weeks

    def _resolve_week_type(self, weeks_elapsed, preferred_split=None):
        """Resolve whether the current schedule follows the A or B template."""
        if preferred_split and preferred_split in self.program.get('weeks', {}):
            return preferred_split

        return 'A' if weeks_elapsed % 2 == 0 else 'B'

    def _build_session_plan(self, session_data, week_in_cycle):
        """Convert a session definition into a concrete workout plan for a specific week."""
        if not session_data:
            return []

        exercises = []
        for exercise in session_data.get('exercises', []):
            exercises.append({
                'name': exercise.get('name', 'Exercise'),
                'sets': _value_for_week(exercise.get('sets', []), week_in_cycle),
                'reps': _value_for_week(exercise.get('reps', []), week_in_cycle),
                'notes': exercise.get('notes', '')
            })

        return exercises
    
    def get_today_workout(self, user_start_date=None, preferred_split=None):
        """
        Determine today's workout based on A/B weekly alternation and 3+1 periodization.
        
        Args:
            user_start_date: Date when user started the program (defaults to today)
            preferred_split: Force a specific split ('A' or 'B'), otherwise alternates by week
        
        Returns:
            dict: Workout plan for today including week number and exercises
        """
        today, weeks_elapsed, week_in_cycle, cycle_weeks = self._calculate_cycle_metrics(user_start_date)

        if self.uses_session_structure:
            week_type = self._resolve_week_type(weeks_elapsed, preferred_split)
            day_name = today.strftime('%A')
            weeks_config = self.program.get('weeks', {})
            session_key = weeks_config.get(week_type, {}).get(day_name)
            session_data = self.program.get('sessions', {}).get(session_key, {}) if session_key else None

            workout_plan = self._build_session_plan(session_data, week_in_cycle)

            session_name = session_data.get('name') if session_data else 'Rest Day'
            session_description = session_data.get('description', '') if session_data else ''

            return {
                'split': week_type,
                'week_type': week_type,
                'split_name': session_name,
                'session_name': session_name,
                'session_key': session_key,
                'session_description': session_description,
                'day_name': day_name,
                'week_in_cycle': week_in_cycle,
                'is_deload': week_in_cycle == cycle_weeks,
                'is_rest_day': session_key is None,
                'cycle_weeks': cycle_weeks,
                'exercises': workout_plan
            }

        # Legacy split-based programs
        if preferred_split:
            split = preferred_split
        else:
            split = 'A' if weeks_elapsed % 2 == 0 else 'B'

        splits = self.program.get('splits', {})
        if split not in splits:
            split = list(splits.keys())[0] if splits else 'A'

        workout_data = splits.get(split, {})
        exercises = workout_data.get('exercises', [])

        workout_plan = []
        for exercise in exercises:
            workout_plan.append({
                'name': exercise.get('name', 'Exercise'),
                'sets': _value_for_week(exercise.get('sets', [3, 3, 3, 2]), week_in_cycle),
                'reps': _value_for_week(exercise.get('reps', [8, 8, 8, 8]), week_in_cycle),
                'notes': exercise.get('notes', '')
            })

        return {
            'split': split,
            'week_type': split,
            'split_name': workout_data.get('name', f'Split {split}'),
            'session_name': workout_data.get('name', f'Split {split}'),
            'session_description': workout_data.get('description', ''),
            'session_key': split,
            'day_name': None,
            'week_in_cycle': week_in_cycle,
            'is_deload': week_in_cycle == cycle_weeks,
            'is_rest_day': False,
            'cycle_weeks': cycle_weeks,
            'exercises': workout_plan
        }

    def get_split_workout(self, split, week_in_cycle=1, day_name=None):
        """Get workout plan for a specific split/week combination."""
        if self.uses_session_structure:
            return self.get_session_workout(split, day_name=day_name, week_in_cycle=week_in_cycle)

        splits = self.program.get('splits', {})
        if split not in splits:
            return None

        workout_data = splits.get(split, {})
        exercises = workout_data.get('exercises', [])

        workout_plan = []
        for exercise in exercises:
            workout_plan.append({
                'name': exercise.get('name', 'Exercise'),
                'sets': _value_for_week(exercise.get('sets', [3, 3, 3, 2]), week_in_cycle),
                'reps': _value_for_week(exercise.get('reps', [8, 8, 8, 8]), week_in_cycle),
                'notes': exercise.get('notes', '')
            })

        return {
            'split': split,
            'split_name': workout_data.get('name', f'Split {split}'),
            'week_in_cycle': week_in_cycle,
            'is_rest_day': False,
            'exercises': workout_plan
        }

    def get_session_workout(self, week_type, day_name=None, week_in_cycle=1):
        """Get the structured session for a given week template and day."""
        if not self.uses_session_structure:
            return self.get_split_workout(week_type, week_in_cycle)

        weeks_config = self.program.get('weeks', {})
        sessions = self.program.get('sessions', {})
        schedule = weeks_config.get(week_type, {})

        if day_name is None:
            days = []
            for day_label, session_key in schedule.items():
                session_data = sessions.get(session_key, {})
                days.append({
                    'day_name': day_label,
                    'session_key': session_key,
                    'session_name': session_data.get('name', session_key),
                    'session_description': session_data.get('description', ''),
                    'exercises': self._build_session_plan(session_data, week_in_cycle),
                    'is_rest_day': session_key is None
                })

            return {
                'week_type': week_type,
                'week_in_cycle': week_in_cycle,
                'cycle_weeks': self.program.get('cycle_weeks', 4),
                'days': days
            }

        session_key = schedule.get(day_name)
        session_data = sessions.get(session_key, {}) if session_key else None

        return {
            'week_type': week_type,
            'day_name': day_name,
            'session_key': session_key,
            'session_name': session_data.get('name', 'Rest Day') if session_data else 'Rest Day',
            'session_description': session_data.get('description', '') if session_data else '',
            'week_in_cycle': week_in_cycle,
            'is_rest_day': session_key is None,
            'cycle_weeks': self.program.get('cycle_weeks', 4),
            'exercises': self._build_session_plan(session_data, week_in_cycle)
        }
