import pandas as pd
import time
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.library.http import NBAHTTP

def fetch_season_games(season_year: str) -> pd.DataFrame:
    """
    Fetches regular-season game logs with custom headers and retries
    to bypass strict cloud server rate limits.
    """
    print(f"📡 Querying NBA API for the {season_year} regular season...")
    
    # Standard browser headers to disguise the GitHub Action runner
    custom_headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',
        'Connection': 'keep-alive'
    }
    
    # Inject headers directly into the NBA API package session configuration
    NBAHTTP.headers = custom_headers
    
    # Try connecting with a loop to gracefully handle temporary timeouts
    for attempt in range(3):
        try:
            game_finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season_year,
                league_id_nullable='00',  
                season_type_nullable='Regular Season'
            )
            games_df = game_finder.get_data_frames()[0]
            
            games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
            games_df = games_df.sort_values(by='GAME_DATE').reset_index(drop=True)
            
            print(f"✅ Retrieved {len(games_df)} historical team-game rows.")
            return games_df
            
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} timed out or failed. Retrying in 5 seconds... Error: {e}")
            time.sleep(5)
            
    raise ConnectionError("❌ Failed to pull data from NBA API after multiple secure attempts due to server throttling.")
