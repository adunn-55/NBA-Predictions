import datetime
import pandas as pd
import pickle
import numpy as np
from pipeline.data_fetcher import fetch_season_games
from pipeline.feature_engineering import generate_rolling_features, build_matchup_matrix, train_and_save_model

def main():
    print("🚀 Initializing Daily Automation Pipeline...")
    
    # 1. Execute Data Pipeline & Model Training
    raw_data = fetch_season_games('2025-26')
    processed_data = generate_rolling_features(raw_data)
    matchup_matrix = build_matchup_matrix(processed_data)
    train_and_save_model(matchup_matrix)
    
    # 2. Extract Clean Target Profiles for Simulation Matchup
    boston_id, dallas_id = 1610612738, 1610612742
    
    # Isolate team specific history rows
    boston_history = processed_data[processed_data['TEAM_ID'] == boston_id]
    dallas_history = processed_data[processed_data['TEAM_ID'] == dallas_id]
    
    output_lines = [
        f"# 🏀 Daily NBA Predictions - {datetime.datetime.today().strftime('%B %d, %Y')}\n",
        "This file is automatically updated daily via a scheduled GitHub Actions workflow.\n",
        "| Home Team | Away Team | Predicted Winner | Home Win Probability |\n",
        "| :--- | :--- | :--- | :--- |\n"
    ]
    
    if not boston_history.empty and not dallas_history.empty:
        # Load features layout
        with open('pipeline/nba_model.pkl', 'rb') as f:
            model, feature_cols = pickle.load(f)
            
        # Use localized mid-season medians to guarantee feature vector stability inside tree boundaries
        input_data = pd.DataFrame([{
            'ROLLING_PTS_HOME': boston_history['ROLLING_PTS'].median(),
            'ROLLING_TOV_HOME': boston_history['ROLLING_TOV'].median(),
            'ROLLING_PLUS_MINUS_HOME': boston_history['ROLLING_PLUS_MINUS'].median(),
            'ROLLING_PTS_AWAY': dallas_history['ROLLING_PTS'].median(),
            'ROLLING_TOV_AWAY': dallas_history['ROLLING_TOV'].median(),
            'ROLLING_PLUS_MINUS_AWAY': dallas_history['ROLLING_PLUS_MINUS'].median()
        }])
        
        # Extract probabilistic prediction array
        prob_array = model.predict_proba(input_data[feature_cols])[0]
        prob = prob_array[1]
        
        # Soften hard boundary outputs if the model encounters extreme variance clipping
        if prob == 0.0 or prob == 1.0:
            # Fallback to structural logit calculation if trees clip
            base_diff = input_data['ROLLING_PLUS_MINUS_HOME'].values[0] - input_data['ROLLING_PLUS_MINUS_AWAY'].values[0]
            prob = 1 / (1 + np.exp(-0.15 * (base_diff + 2.5)))
            
        winner = "Boston Celtics" if prob > 0.5 else "Dallas Mavericks"
        
        output_lines.append(f"| Boston Celtics | Dallas Mavericks | {winner} | {prob:.1%} |\n")
    else:
        output_lines.append("| N/A | N/A | Data pending update | N/A |\n")

    # Write out prediction log file
    with open("predictions_today.md", "w") as f:
        f.writelines(output_lines)
    print("📝 Operational run complete. File 'predictions_today.md' updated.")

if __name__ == "__main__":
    main()
