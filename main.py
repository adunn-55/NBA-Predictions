import datetime
import pandas as pd
import pickle
from pipeline.data_fetcher import fetch_season_games
from pipeline.feature_engineering import generate_rolling_features, build_matchup_matrix, train_and_save_model

def main():
    print("🚀 Initializing Daily Automation Pipeline...")
    
    # 1. Pipeline execution: Fetch data, clean features, train model
    raw_data = fetch_season_games('2025-26')
    processed_data = generate_rolling_features(raw_data)
    matchup_matrix = build_matchup_matrix(processed_data)
    train_and_save_model(matchup_matrix)
    
    # 2. Extract final statistical momentum profiles for simulation
    # Grab the most recent available feature row for every team
    latest_team_stats = processed_data.sort_values('GAME_DATE').groupby('TEAM_ID').last().reset_index()
    
    # 3. Simulate a sample upcoming matchup dashboard 
    # (Since it's June/the off-season, we generate a representative marquee matchup)
    boston_id, dallas_id = 1610612738, 1610612742  # Standard NBA API Team IDs
    
    home_profile = latest_team_stats[latest_team_stats['TEAM_ID'] == boston_id]
    away_profile = latest_team_stats[latest_team_stats['TEAM_ID'] == dallas_id]
    
    output_lines = [
        f"# 🏀 Daily NBA Predictions - {datetime.datetime.today().strftime('%B %d, %Y')}\n",
        "This file is automatically updated daily via a scheduled GitHub Actions workflow.\n",
        "| Home Team | Away Team | Predicted Winner | Home Win Probability |\n",
        "| :--- | :--- | :--- | :--- |\n"
    ]
    
    if not home_profile.empty and not away_profile.empty:
        # Load features layout
        with open('pipeline/nba_model.pkl', 'rb') as f:
            model, feature_cols = pickle.load(f)
            
        # Reconstruct structural feature input vector
        input_data = pd.DataFrame([{
            'ROLLING_PTS_HOME': home_profile['ROLLING_PTS'].values[0],
            'ROLLING_TOV_HOME': home_profile['ROLLING_TOV'].values[0],
            'ROLLING_PLUS_MINUS_HOME': home_profile['ROLLING_PLUS_MINUS'].values[0],
            'ROLLING_PTS_AWAY': away_profile['ROLLING_PTS'].values[0],
            'ROLLING_TOV_AWAY': away_profile['ROLLING_TOV'].values[0],
            'ROLLING_PLUS_MINUS_AWAY': away_profile['ROLLING_PLUS_MINUS'].values[0]
        }])
        
        prob = model.predict_proba(input_data[feature_cols])[0][1]
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
