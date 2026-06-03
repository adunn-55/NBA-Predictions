import pandas as pd
import requests

def fetch_season_games(season_year: str) -> pd.DataFrame:
    """
    Fetches season game logs directly from the NBA's mobile/data CDN API.
    Bypasses stats.nba.com firewall blocks entirely.
    """
    print(f"📡 Querying NBA mobile CDN for the {season_year} season...")
    
    # Format '2025-26' into '2025' for the URL string
    start_year = season_year.split('-')[0]
    
    # Direct CDN URL for complete league schedule and results
    url = f"https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{start_year}/league/00_full_schedule.json"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Parse out the games list from the nested JSON structure
        games_list = []
        for month in data['l']['m']:
            for game in month['g']:
                # Filter to only look at regular season games (Season stage 2)
                if game['stg'] == 2:
                    # The CDN lists game results. We append standard keys to match our model structure
                    games_list.append({
                        'GAME_ID': game['gid'],
                        'GAME_DATE': pd.to_datetime(game['gdte']),
                        'MATCHUP': f"{game['v']['tn']} @ {game['h']['tn']}",
                        'TEAM_ID': game['h']['tid'],
                        'TEAM_NAME': game['h']['tn'],
                        'PTS': int(game['h']['s']) if game['h']['s'] else 0,
                        'PLUS_MINUS': (int(game['h']['s']) - int(game['v']['s'])) if (game['h']['s'] and game['v']['s']) else 0,
                        'WL': 'W' if (game['h']['s'] and int(game['h']['s']) > int(game['v']['s'])) else 'L',
                        'TOV': 12 # Stand-in average baseline metric since basic CDN omits box score turnovers
                    })
                    # Add the corresponding Away team row to keep team-centric pairing intact
                    games_list.append({
                        'GAME_ID': game['gid'],
                        'GAME_DATE': pd.to_datetime(game['gdte']),
                        'MATCHUP': f"{game['v']['tn']} vs. {game['h']['tn']}",
                        'TEAM_ID': game['v']['tid'],
                        'TEAM_NAME': game['v']['tn'],
                        'PTS': int(game['v']['s']) if game['v']['s'] else 0,
                        'PLUS_MINUS': (int(game['v']['s']) - int(game['h']['s'])) if (game['h']['s'] and game['v']['s']) else 0,
                        'WL': 'W' if (game['v']['s'] and int(game['v']['s']) > int(game['h']['s'])) else 'L',
                        'TOV': 12
                    })
                    
        df = pd.DataFrame(games_list)
        # Filter down to games that have actually been played (contain score data)
        df = df[df['PTS'] > 0].sort_values(by='GAME_DATE').reset_index(drop=True)
        
        print(f"✅ Successfully retrieved {len(df)} historical team-game records from CDN.")
        return df
        
    except Exception as e:
        raise ConnectionError(f"❌ Failed to reach alternate NBA CDN endpoint: {e}")
