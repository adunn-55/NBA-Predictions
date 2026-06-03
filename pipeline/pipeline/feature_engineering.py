import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier

def generate_rolling_features(df, window=5):
    """Calculates rolling averages per team, shifting by 1 to prevent data leakage."""
    df = df.copy()
    metrics = ['PTS', 'TOV', 'PLUS_MINUS']
    
    for m in metrics:
        df[f'ROLLING_{m}'] = np.nan

    # Group by team so rolling averages don't bleed across different teams
    for team_id, team_games in df.groupby('TEAM_ID'):
        # shift(1) means game #10 only sees averages from games 1 through 9
        rolling = team_games[metrics].shift(1).rolling(window=window).mean()
        df.loc[team_games.index, [f'ROLLING_{m}' for m in metrics]] = rolling
        
    return df

def build_matchup_matrix(processed_df):
    """Flattens two team rows (Home/Away) into a single game row for modeling."""
    home_games = processed_df[processed_df['MATCHUP'].str.contains('vs.')].copy()
    away_games = processed_df[processed_df['MATCHUP'].str.contains('@')].copy()

    # Merge home and away records on their matching unique GAME_ID
    model_df = pd.merge(
        home_games, away_games, 
        on='GAME_ID', 
        suffixes=('_HOME', '_AWAY')
    )
    
    # 1 if home team wins, 0 if away team wins
    model_df['HOME_WIN'] = (model_df['WL_HOME'] == 'W').astype(int)
    return model_df

def train_and_save_model(model_df, output_path='pipeline/nba_model.pkl'):
    """Trains an XGBoost model on historical data and exports it to disk."""
    feature_cols = [
        'ROLLING_PTS_HOME', 'ROLLING_TOV_HOME', 'ROLLING_PLUS_MINUS_HOME',
        'ROLLING_PTS_AWAY', 'ROLLING_TOV_AWAY', 'ROLLING_PLUS_MINUS_AWAY'
    ]
    
    # Clean out empty rolling rows from the start of the season
    clean_df = model_df.dropna(subset=feature_cols)
    
    X = clean_df[feature_cols]
    y = clean_df['HOME_WIN']
    
    # Train-test split by chronological index to respect time-series rules
    split_idx = int(len(clean_df) * 0.8)
    X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
    
    print("🏋️ Training prediction engine...")
    model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    
    with open(output_path, 'wb') as f:
        pickle.dump((model, feature_cols), f)
    print(f"💾 Trained model saved to {output_path}")
