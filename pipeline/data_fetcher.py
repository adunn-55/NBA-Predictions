import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder

def fetch_season_games(season_year: str) -> pd.DataFrame:
    """Fetches regular-season game logs for a specific year from the NBA API."""
    print(f"📡 Querying NBA API for the {season_year} regular season...")
    
    game_finder = leaguegamefinder.LeagueGameFinder(
        season_nullable=season_year,
        league_id_nullable='00',  # '00' limits queries strictly to the NBA
        season_type_nullable='Regular Season'
    )
    
    games_df = game_finder.get_data_frames()[0]
    
    # Clean dates and ensure correct chronological order
    games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
    games_df = games_df.sort_values(by='GAME_DATE').reset_index(drop=True)
    
    print(f"✅ Retrieved {len(games_df)} historical team-game rows.")
    return games_df
