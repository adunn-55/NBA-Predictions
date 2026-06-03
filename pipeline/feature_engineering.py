import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier

def generate_rolling_features(df, window=5):
    """Calculates rolling averages for each team, shifting by 1 game to prevent leakage."""
    df = df.copy()
    core_metrics = ['PTS', 'TOV', 'PLUS_MINUS']
    
    for metric in core_metrics:
        df[f'ROLLING_{metric}'] = np.nan

    for team_id, team_games in df.groupby('TEAM_ID'):
        # shift(1) ensures tonight's row only knows about past games
        rolling = team_games[core_metrics].shift(1).rolling(window=window).mean()
        df.loc[team_games.index, [f'ROLLING_{m}' for m in core_metrics]] = rolling
        
    return df

def build_matchup_matrix(processed_df):
    """Pivots the team-centric rows into a single row per game (Home vs Away)."""
    # Isolate home rows (vs.) and away rows (@)
    home_games = processed_df[processed_df['MATCHUP'].str.contains('vs.')].copy()
    away_games = processed_df[processed_df['MATCHUP'].str.contains('@')].copy()

    # Match them on the unique GAME_ID
    model_df = pd.merge(
        home_games, 
        away_games, 
        on='GAME_ID', 
        suffixes=('_HOME', '_AWAY')
    )
    
    model_df['HOME_WIN'] = (model_df['WL_HOME'] == 'W').astype(int)
    return model_df

def train_and_save_model(model_df, output_path='pipeline/nba_model.pkl'):
    """Trains the XGBoost model and serializes it to disk."""
    feature_cols = [
        'ROLLING_PTS_HOME', 'ROLLING_TOV_HOME', 'ROLLING_PLUS_MINUS_HOME',
        'ROLLING_PTS_AWAY', 'ROLLING_TOV_AWAY', 'ROLLING_PLUS_MINUS_AWAY'
    ]
    
    # Drop any rows that didn't have enough history to calculate rolling stats
    clean_df = model_df.dropna(subset=feature_cols)
    
    X = clean_df[feature_cols]
    y = clean_df['HOME_WIN']
    
    # Simple chronological split (80% train, 20% validation)
    split_idx = int(len(clean_df) * 0.8)
    X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
    
    print("🏋️ Training the prediction model...")
    model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model and the features list
    with open(output_path, 'wb') as f:
        pickle.dump((model, feature_cols), f)
    print(f"💾 Model saved successfully to {output_path}")
