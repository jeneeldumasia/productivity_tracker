import os
import uuid
import pandas as pd

# --- Configuration & Data Paths ---
DATA_DIR = 'tracker_data'
CONFIG_FILE = os.path.join(DATA_DIR, 'config.csv')
ACTIVITIES_FILE = os.path.join(DATA_DIR, 'activities.csv')
USER_ID_FILE = os.path.join(DATA_DIR, 'user_id.txt')

def ensure_data_dir_and_files():
    """Ensures that the data directory and necessary files exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Ensure Activities file has a tags column ---
    if not os.path.exists(ACTIVITIES_FILE):
        # Create a new file with the tags column
        pd.DataFrame(columns=['app_name', 'start_time', 'end_time', 'duration_seconds', 'tags']).to_csv(ACTIVITIES_FILE, index=False)
    else:
        # If the file exists, check if it has the tags column and add it if not
        df = pd.read_csv(ACTIVITIES_FILE)
        if 'tags' not in df.columns:
            df['tags'] = '' # Add an empty tags column
            df.to_csv(ACTIVITIES_FILE, index=False)

    if not os.path.exists(USER_ID_FILE):
        with open(USER_ID_FILE, 'w') as f:
            f.write(str(uuid.uuid4()))
    if not os.path.exists(CONFIG_FILE):
        pd.DataFrame({
            'key': ['check_interval_seconds', 'productivity_apps', 'is_dark_mode', 'idle_threshold_minutes'],
            'value': [3, 'VS Code,Google Chrome,PyCharm', 'False', 5]
        }).to_csv(CONFIG_FILE, index=False)

def load_config():
    """Loads configuration from the CSV file."""
    try:
        df = pd.read_csv(CONFIG_FILE).set_index('key')['value']
        return {
            "check_interval_seconds": int(df.get('check_interval_seconds', 3)),
            "productivity_apps": [app.strip() for app in df.get('productivity_apps', "").split(',')],
            "is_dark_mode": df.get('is_dark_mode', 'False').lower() == 'true',
            "idle_threshold_minutes": int(df.get('idle_threshold_minutes', 5))
        }
    except (FileNotFoundError, KeyError):
        return {
            "check_interval_seconds": 3,
            "productivity_apps": ["VS Code", "Google Chrome"],
            "is_dark_mode": False,
            "idle_threshold_minutes": 5
        }

def save_config(config):
    """Saves the configuration dictionary to the CSV file."""
    config_to_save = {
        'check_interval_seconds': config['check_interval_seconds'],
        'productivity_apps': ",".join(config['productivity_apps']),
        'is_dark_mode': str(config['is_dark_mode']),
        'idle_threshold_minutes': config['idle_threshold_minutes']
    }
    pd.DataFrame(config_to_save.items(), columns=['key', 'value']).to_csv(CONFIG_FILE, index=False)

def load_activities():
    """Loads activity data from the CSV file."""
    try:
        df = pd.read_csv(ACTIVITIES_FILE)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration_seconds'] = pd.to_numeric(df['duration_seconds'])
        # Ensure the tags column is treated as a string, filling empty values
        if 'tags' not in df.columns:
            df['tags'] = ''
        df['tags'] = df['tags'].fillna('').astype(str)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['app_name', 'start_time', 'end_time', 'duration_seconds', 'tags'])

def append_activity(activity_data):
    """Appends a new activity record to the CSV file."""
    # Ensure the new activity has a 'tags' key
    if 'tags' not in activity_data:
        activity_data['tags'] = ''
        
    df = load_activities()
    new_df = pd.DataFrame([activity_data])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(ACTIVITIES_FILE, index=False)

def update_activity_tags(start_time, new_tags):
    """Finds an activity by its start time and updates its tags."""
    df = load_activities()
    # Find the row that matches the start time (this should be unique)
    # Using a tolerance for timestamp matching
    start_time_dt = pd.to_datetime(start_time)
    mask = (df['start_time'] >= start_time_dt - pd.Timedelta(seconds=1)) & \
           (df['start_time'] <= start_time_dt + pd.Timedelta(seconds=1))

    if mask.any():
        df.loc[mask, 'tags'] = new_tags
        df.to_csv(ACTIVITIES_FILE, index=False)
        return True
    return False