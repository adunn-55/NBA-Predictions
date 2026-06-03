import os
import datetime
import pandas as pd
import pickle
from pipeline.data_fetcher import fetch_season_games
from pipeline.feature_engineering import generate_rolling_features, build_matchup_matrix, train_and_save_model
from nba_api.stats.endpoints import scoreboardv2

def get_todays_schedule():
    """Fetches games scheduled for today from the NBA API."""
    today_str = datetime.datetime.today().strftime('%Y-%m-%d')
    print(f"📅 Fetching scheduled games for: {today_str}")
    
    try:
        sb = scoreboardv2.ScoreboardV2(game_date=today_str, league_id='00', day_offset='0')
        games_today = sb.game_header.get_data_frame()
        return games_today
    except Exception as e:
        print(f"⚠️ Could not fetch schedule (likely off-season or API downtime): {e}")
        return pd.DataFrame()

def main():
    # 1. Pipeline Run: Fetch and Train
    # We use a recent past season (e.g., 2023-24) to ensure data is populated for training
    raw_data = fetch_season_games('2023-24')
    processed_data = generate_rolling_features(raw_data)
    matchup_data = build_matchup_matrix(processed_data)
    train_and_save_model(matchup_data)
    
    # 2. Daily Prediction Phase
    games_today = get_todays_schedule()
    
    output_lines = [
        f"# 🏀 Daily NBA Predictions - {datetime.datetime.today().strftime('%B %d, %Y')}\n",
        "This file is automatically updated daily via GitHub Actions automated pipeline.\n",
        "| Home Team | Away Team | Predicted Winner | Home Win Probability |\n",
        "| :--- | :--- | :--- | :--- |\n"
    ]
    
    if games_today.empty:
        output_lines.append("| N/A | N/A | No games scheduled for today | N/A |\n")
    else:
        # Load the saved model assets
        with open('pipeline/nba_model.pkl', 'rb') as f:
            model, feature_cols = pickle.load(f)
            
        # For simplicity in this initial blueprint, we map out a mock loop parsing the daily schedule dataframe
        # In a full run, you match today's TEAM_IDs with their final rolling row from `processed_data`
        output_lines.append("| Sample Team A | Sample Team B | Home Team | 64.5% |\n")

    # 3. Write predictions to a file for GitHub to display
    with open("predictions_today.md", "w") as f:
        f.writelines(output_lines)
    print("📝 Daily predictions generated and saved to predictions_today.md")

if __name__ == "__main__":
    main()
