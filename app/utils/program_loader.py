"""Utility module for loading and processing workout programs from JSON."""
import json
from datetime import datetime, timedelta


class ProgramLoader:
    """Load and manage workout programs from JSON files."""
    
    def __init__(self, json_path):
        """Initialize the program loader with a JSON file path."""
        self.json_path = json_path
        self.program = self._load_program()
    
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
            "description": "3 weeks progressive overload + 1 deload week",
            "cycle_weeks": 4,
            "splits": {
                "A": {
                    "name": "Upper Body Push",
                    "exercises": [
                        {"name": "Bench Press", "sets": [3, 3, 3, 2], "reps": [8, 6, 4, 8]},
                        {"name": "Overhead Press", "sets": [3, 3, 3, 2], "reps": [10, 8, 6, 10]},
                        {"name": "Dips", "sets": [3, 3, 3, 2], "reps": [12, 10, 8, 12]}
                    ]
                },
                "B": {
                    "name": "Lower Body & Pull",
                    "exercises": [
                        {"name": "Squat", "sets": [3, 3, 3, 2], "reps": [8, 6, 4, 8]},
                        {"name": "Deadlift", "sets": [3, 3, 3, 2], "reps": [6, 4, 2, 6]},
                        {"name": "Pull-ups", "sets": [3, 3, 3, 2], "reps": [10, 8, 6, 10]}
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
        splits = self.program.get('splits', {})
        return {key: split.get('name', f'Split {key}') for key, split in splits.items()}
    
    def get_today_workout(self, user_start_date=None, preferred_split=None):
        """
        Determine today's workout based on A/B weekly alternation and 3+1 periodization.
        
        Args:
            user_start_date: Date when user started the program (defaults to today)
            preferred_split: Force a specific split ('A' or 'B'), otherwise alternates by week
        
        Returns:
            dict: Workout plan for today including week number and exercises
        """
        if user_start_date is None:
            user_start_date = datetime.utcnow().date()
        
        today = datetime.utcnow().date()
        days_elapsed = (today - user_start_date).days
        weeks_elapsed = days_elapsed // 7
        
        # Determine which week in the cycle (1-4 for 3+1 periodization)
        cycle_weeks = self.program.get('cycle_weeks', 4)
        week_in_cycle = (weeks_elapsed % cycle_weeks) + 1
        
        # Determine split (A or B) - alternates weekly
        if preferred_split:
            split = preferred_split
        else:
            split = 'A' if weeks_elapsed % 2 == 0 else 'B'
        
        # Get the workout for this split
        splits = self.program.get('splits', {})
        if split not in splits:
            split = list(splits.keys())[0] if splits else 'A'
        
        workout_data = splits.get(split, {})
        exercises = workout_data.get('exercises', [])
        
        # Build workout plan with week-specific sets/reps
        workout_plan = []
        for exercise in exercises:
            sets_list = exercise.get('sets', [3, 3, 3, 2])
            reps_list = exercise.get('reps', [8, 8, 8, 8])
            
            # Get sets/reps for current week (week_in_cycle is 1-indexed)
            sets = sets_list[week_in_cycle - 1] if week_in_cycle <= len(sets_list) else sets_list[0]
            reps = reps_list[week_in_cycle - 1] if week_in_cycle <= len(reps_list) else reps_list[0]
            
            workout_plan.append({
                'name': exercise.get('name', 'Exercise'),
                'sets': sets,
                'reps': reps
            })
        
        return {
            'split': split,
            'split_name': workout_data.get('name', f'Split {split}'),
            'week_in_cycle': week_in_cycle,
            'is_deload': week_in_cycle == cycle_weeks,
            'exercises': workout_plan
        }
    
    def get_split_workout(self, split, week_in_cycle=1):
        """Get workout plan for a specific split and week."""
        splits = self.program.get('splits', {})
        if split not in splits:
            return None
        
        workout_data = splits.get(split, {})
        exercises = workout_data.get('exercises', [])
        
        workout_plan = []
        for exercise in exercises:
            sets_list = exercise.get('sets', [3, 3, 3, 2])
            reps_list = exercise.get('reps', [8, 8, 8, 8])
            
            sets = sets_list[week_in_cycle - 1] if week_in_cycle <= len(sets_list) else sets_list[0]
            reps = reps_list[week_in_cycle - 1] if week_in_cycle <= len(reps_list) else reps_list[0]
            
            workout_plan.append({
                'name': exercise.get('name', 'Exercise'),
                'sets': sets,
                'reps': reps
            })
        
        return {
            'split': split,
            'split_name': workout_data.get('name', f'Split {split}'),
            'week_in_cycle': week_in_cycle,
            'exercises': workout_plan
        }
