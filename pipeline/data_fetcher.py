import pandas as pd
import numpy as np
import datetime
import re

def fetch_season_games(season_year: str) -> pd.DataFrame:
    """
    Advanced algorithmic sports data engine. Simulates an NBA conference schedule
    by decoupling team characteristics into Offense, Defense, and Pace parameters,
    while dynamically shifting team strengths each season using a random-walk seed.
    """
    # 1. Parse Season Year
    match = re.search(r"\d{4}", str(season_year))
    start_year = int(match.group()) if match else 2026
    
    print(f"📦 Running Decoupled Efficiency & Pace Simulation for the {start_year} Season...")
    
    # 2. Base Team Definitions & API Mapping
    TEAM_IDS = {
        "Boston Celtics": 1610612738,
        "Miami Heat": 1610612748,
        "Milwaukee Bucks": 1610612749,
        "New York Knicks": 1610612752,
        "Dallas Mavericks": 1610612742,
        "LA Lakers": 1610612747,
        "Golden State Warriors": 1610612744,
        "Denver Nuggets": 1610612743,
    }
    east_teams = ["Boston Celtics", "Miami Heat", "Milwaukee Bucks", "New York Knicks"]
    west_teams = ["Dallas Mavericks", "LA Lakers", "Golden State Warriors", "Denver Nuggets"]
    all_teams = list(TEAM_IDS.keys())
    
    # 3. Establish Baseline Parameter Ratings (Centered around 0 as league average)
    BASE_OFFENSE = {"Boston Celtics": 4.5, "Denver Nuggets": 3.5, "New York Knicks": 2.0, "Dallas Mavericks": 2.5, "Milwaukee Bucks": 1.0, "Golden State Warriors": 0.5, "LA Lakers": -1.5, "Miami Heat": -2.5}
    BASE_DEFENSE = {"Boston Celtics": 3.0, "Denver Nuggets": 1.0, "New York Knicks": 2.5, "Dallas Mavericks": -1.0, "Milwaukee Bucks": 0.5, "Golden State Warriors": -1.5, "LA Lakers": -0.5, "Miami Heat": 2.0}
    BASE_PACE = {"Boston Celtics": 98.0, "Denver Nuggets": 96.5, "New York Knicks": 95.0, "Dallas Mavericks": 100.5, "Milwaukee Bucks": 101.0, "Golden State Warriors": 102.0, "LA Lakers": 101.5, "Miami Heat": 94.5}
    
    # 4. Dynamic Season Variance (The Roster Shift Factor)
    np.random.seed(start_year)
    
    off_shocks = np.random.normal(0, 1.5, len(all_teams))
    def_shocks = np.random.normal(0, 1.5, len(all_teams))
    pace_shocks = np.random.normal(0, 1.0, len(all_teams))
    
    team_offense = {team: BASE_OFFENSE[team] + off_shocks[i] for i, team in enumerate(all_teams)}
    team_defense = {team: BASE_DEFENSE[team] + def_shocks[i] for i, team in enumerate(all_teams)}
    team_pace = {team: BASE_PACE[team] + pace_shocks[i] for i, team in enumerate(all_teams)}
    
    # 5. Generate Conference-Symmetric Matchups (80 games total)
    matchups = []
    # Intra-Conference (4x: 2 H, 2 A)
    for conf in [east_teams, west_teams]:
        for i in range(len(conf)):
            for j in range(len(conf)):
                if i != j:
                    matchups.extend([(conf[i], conf[j]), (conf[i], conf[j])])
    # Inter-Conference (2x: 1 H, 1 A)
    for east in east_teams:
        for west in west_teams:
            matchups.extend([(east, west), (west, east)])
            
    # Randomized schedule timeline allocation
    np.random.shuffle(matchups)
    
    # 6. Execute Simulation Loop
    base_date = pd.to_datetime(f"{start_year}-10-24")
    records = []
    
    for game_idx, (t_home, t_away) in enumerate(matchups):
        # Matchup Pace interaction: Average of both teams + game-to-game noise
        game_pace = (team_pace[t_home] + team_pace[t_away]) / 2 + np.random.normal(0, 2)
        
        # Scoring logic using structural pace baseline and offensive/defensive interactions
        pts_home_expected = (game_pace * 1.1) + 1.25 + team_offense[t_home] - team_defense[t_away]
        pts_away_expected = (game_pace * 1.1) - 1.25 + team_offense[t_away] - team_defense[t_home]
        
        pts_home = max(80, round(pts_home_expected + np.random.normal(0, 5)))
        pts_away = max(80, round(pts_away_expected + np.random.normal(0, 5)))
        
        # Fixed Overtime Resolution: Ensures scores only increase when resolving a tie
        if pts_home == pts_away:
            if np.random.rand() > 0.5:
                pts_home += 2
            else:
                pts_away += 2
            
        game_date = base_date + datetime.timedelta(days=game_idx // 2)
        game_id = f"002{str(start_year)[2:]}{game_idx:05d}"
        
        # Standardized rounded turnover calculation
        tov_home = max(5, round(game_pace * 0.13 + np.random.normal(0, 1.5)))
        tov_away = max(5, round(game_pace * 0.13 + np.random.normal(0, 1.5)))
        
        # Home Row Vector (Exposing Latent Ground-Truth Ratings for Model Validation)
        records.append({
            'GAME_ID': game_id, 'GAME_DATE': game_date, 'MATCHUP': f"{t_away} @ {t_home}",
            'TEAM_ID': TEAM_IDS[t_home], 'TEAM_NAME': t_home, 'PTS': pts_home,
            'PLUS_MINUS': pts_home - pts_away, 'WL': 'W' if pts_home > pts_away else 'L',
            'TOV': tov_home,
            'TRUE_LATENT_OFF': team_offense[t_home], 'TRUE_LATENT_DEF': team_defense[t_home], 'TRUE_LATENT_PACE': team_pace[t_home]
        })
        # Away Row Vector
        records.append({
            'GAME_ID': game_id, 'GAME_DATE': game_date, 'MATCHUP': f"{t_home} vs. {t_away}",
            'TEAM_ID': TEAM_IDS[t_away], 'TEAM_NAME': t_away, 'PTS': pts_away,
            'PLUS_MINUS': pts_away - pts_home, 'WL': 'W' if pts_away > pts_home else 'L',
            'TOV': tov_away,
            'TRUE_LATENT_OFF': team_offense[t_away], 'TRUE_LATENT_DEF': team_defense[t_away], 'TRUE_LATENT_PACE': team_pace[t_away]
        })
        
    df = pd.DataFrame(records)
    print(f"✅ Simulation Complete. Constructed {len(df)} structurally authentic, auditable game vectors.")
    return df
