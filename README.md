# Workout Tracker 💪

A hyper-modular Flask application for tracking gym workouts with JSON-driven programming, passwordless authentication, and a read-only coach view.

## Features

- **JSON-Driven Programs**: Define A/B weekly splits and 3+1 periodization cycles in a simple JSON format
- **Passwordless Authentication**: Magic link login via email - no passwords to remember!
- **Multi-User Support**: Each user has isolated data in SQLite
- **Workout Logging**: Track sets, reps, weight, and RPE (Rate of Perceived Exertion)
- **Dashboard Analytics**: 
  - View today's workout plan
  - Weekly volume calculations
  - Estimated 1RM (one-rep max) tracking
- **Coach View**: Shareable read-only URL for coaches to monitor progress
- **Modular Architecture**: Clean separation of concerns with organized file structure

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/SilverPeak2299/workout_tracker.git
cd workout_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration (optional for basic usage)
```

4. Run the application:
```bash
python run.py
```

5. Open your browser to `http://localhost:5000`

## Project Structure

```
workout_tracker/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/
│   │   └── __init__.py          # Database models (User, WorkoutLog, SetLog)
│   ├── routes/
│   │   ├── auth.py              # Authentication routes (magic links)
│   │   ├── main.py              # Main/index routes
│   │   ├── workout.py           # Workout tracking routes
│   │   └── coach.py             # Coach view routes
│   ├── utils/
│   │   ├── program_loader.py   # JSON program loader
│   │   ├── calculations.py     # Volume and 1RM calculations
│   │   └── auth.py              # Auth helper functions
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── workout/
│   │   └── coach/
│   └── static/                  # CSS and JS files
│       ├── css/
│       └── js/
├── config.py                    # Configuration
├── program.json                 # Workout program definition
├── run.py                       # Application entry point
└── requirements.txt             # Python dependencies
```

## Usage

### 1. Login

- Navigate to the login page
- Enter your email address
- Check your inbox for a magic link (in development mode, the link is shown on screen)
- Click the link to log in

### 2. View Today's Workout

The dashboard shows:
- Today's recommended workout based on your program
- Current week in the cycle (1-4)
- Exercises with prescribed sets and reps

### 3. Log a Workout

- Click "Log Workout" from the dashboard
- Fill in the workout details:
  - Date
  - Week number and split
  - For each exercise: sets, reps, weight, and optional RPE
- Submit to save

### 4. View Analytics

The dashboard displays:
- **Weekly Volume**: Total weight × reps for each exercise this week
- **Estimated 1RM**: Best estimated one-rep max over the last 4 weeks
- **Recent Workouts**: Quick access to your workout history

### 5. Share with Your Coach

- Find the shareable link on your dashboard
- Send it to your coach for read-only access to your data
- No login required for coaches!

## Customizing Your Program

Edit `program.json` to customize your workout program:

```json
{
  "name": "Your Program Name",
  "description": "Program description",
  "cycle_weeks": 4,
  "splits": {
    "A": {
      "name": "Upper Body",
      "exercises": [
        {
          "name": "Bench Press",
          "sets": [4, 4, 4, 3],
          "reps": [8, 6, 4, 8]
        }
      ]
    },
    "B": {
      "name": "Lower Body",
      "exercises": [...]
    }
  }
}
```

- `cycle_weeks`: Number of weeks in your periodization cycle
- `sets`: Array of sets per week (length should match cycle_weeks)
- `reps`: Array of target reps per week
- The program automatically alternates between A and B splits weekly

## Configuration

Edit `.env` to configure:

- `SECRET_KEY`: Flask secret key (required for production)
- `MAIL_SERVER`, `MAIL_PORT`, etc.: Email server for magic links
- `DATABASE_URL`: SQLite database path (default: `sqlite:///workout_tracker.db`)
- `PROGRAM_JSON_PATH`: Path to your program JSON file

## Development

The application uses:
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Mail**: Email sending for magic links
- **SQLite**: Default database (easy to change to PostgreSQL/MySQL)

## Security Notes

- Magic links expire after 1 hour
- Each user's data is isolated via user_id
- Coach view tokens are unique per user and can be regenerated
- No passwords stored - more secure than traditional auth!

## License

MIT License - feel free to use and modify!

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.
