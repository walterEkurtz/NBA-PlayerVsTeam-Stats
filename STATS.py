import requests
from bs4 import BeautifulSoup

# Define ANSI escape sequences for colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

# Function to fetch the player's URL based on their name
def get_player_url(player_name):
    player_name = player_name.strip()
    search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={player_name.replace(' ', '+')}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    player_link = None
    for link in soup.select('a[href^="/players/"]'):
        if player_name.lower() in link.text.lower():
            player_link = link['href']
            break
    if player_link:
        return "https://www.basketball-reference.com" + player_link
    else:
        print(f"{Colors.RED}Player not found.{Colors.RESET}")
        return None

# Function to fetch game logs for a player directly from the game log URL for a specific season
def get_game_logs(player_url, opposing_team_abbr, season):
    game_log_url = player_url.replace('.html', f'/gamelog/{season}')
    print(f"{Colors.CYAN}Game Log URL: {game_log_url}{Colors.RESET}")
    response = requests.get(game_log_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"{Colors.YELLOW}Response Status Code: {response.status_code}{Colors.RESET}")
    table = soup.find('table', {'id': 'pgl_basic'})
    if not table:
        print(f"{Colors.RED}No game log table found for this player.{Colors.RESET}")
        return []
    rows = table.find_all('tr')
    games = []
    for row in rows[1:]:
        columns = row.find_all('td')
        if columns and len(columns) >= 27:
            opponent_abbr = columns[5].text.strip()
            if opponent_abbr == opposing_team_abbr:
                date = columns[1].text.strip()
                points = columns[26].text.strip()
                assists = columns[21].text.strip()
                rebounds = columns[20].text.strip()
                blocks = columns[23].text.strip()
                steals = columns[22].text.strip()
                turnovers = columns[24].text.strip()
                fg_percentage = columns[11].text.strip()
                minutes_played = columns[8].text.strip()  # Updated to column 7 for minutes played
                three_pointers_made = columns[12].text.strip()  # 3P made
                three_pointers_attempted = columns[13].text.strip()  # 3P attempted
                games.append((date, points, assists, rebounds, blocks, steals, turnovers, fg_percentage, minutes_played, three_pointers_made, three_pointers_attempted))
    return games

# Main function to coordinate the process
def main():
    while True:
        player_name = input(f"{Colors.BLUE}Enter the player's name: {Colors.RESET}")
        opposing_team_name = input(f"{Colors.BLUE}Enter the opposing team's name: {Colors.RESET}")
        team_abbreviations = {
            "Chicago Bulls": "CHI",
            "Brooklyn Nets": "BRK",
            "Los Angeles Lakers": "LAL",
            "Boston Celtics": "BOS",
            "Portland Trail Blazers": "POR",
            "Miami Heat": "MIA",
            "Golden State Warriors": "GSW",
            "Philadelphia 76ers": "PHI",
            "Houston Rockets": "HOU",
            "New York Knicks": "NYK",
            "Toronto Raptors": "TOR",
            "Dallas Mavericks": "DAL",
            "Denver Nuggets": "DEN",
            "Utah Jazz": "UTA",
            "Sacramento Kings": "SAC",
            "Oklahoma City Thunder": "OKC",
            "Atlanta Hawks": "ATL",
            "Charlotte Hornets": "CHA",
            "New Orleans Pelicans": "NOP",
            "Minnesota Timberwolves": "MIN",
            "Phoenix Suns": "PHO",
            "Milwaukee Bucks": "MIL",
            "Washington Wizards": "WAS",
            "Los Angeles Clippers": "LAC",
            "Cleveland Cavaliers": "CLE",
            "Orlando Magic": "ORL",
            "Detroit Pistons": "DET",
            "Indiana Pacers": "IND",
            "San Antonio Spurs": "SAS",
            "Memphis Grizzlies": "MEM"
        }
        opposing_team_abbr = team_abbreviations.get(opposing_team_name)
        if not opposing_team_abbr:
            print(f"{Colors.RED}Team '{opposing_team_name}' not recognized.{Colors.RESET}")
            continue
        player_url = get_player_url(player_name)
        if player_url is None:
            continue
        print(f"{Colors.GREEN}Fetching stats for {player_name} against {opposing_team_name}...{Colors.RESET}")
        
        # Fetch game logs for multiple seasons
        seasons_to_check = ['2023', '2024', '2025']  # Add more seasons as needed
        all_games = []
        for season in seasons_to_check:
            games = get_game_logs(player_url, opposing_team_abbr, season)
            all_games.extend(games)
            if len(all_games) >= 10:  # Stop fetching if we have 10 games
                break
        
        # Sort games by date (most recent first)
        all_games.sort(key=lambda x: x[0], reverse=True)
        
        # Limit to the last 10 games
        all_games = all_games[:10]
        
        if not all_games:
            print(f"{Colors.RED}No games found for {player_name} against {opposing_team_abbr}.{Colors.RESET}")
            continue
        
        print(f"{Colors.GREEN}Last 10 games for {player_name} against {opposing_team_abbr}:{Colors.RESET}")
        for game in all_games:
            date, points, assists, rebounds, blocks, steals, turnovers, fg_percentage, minutes_played, three_pointers_made, three_pointers_attempted = game
            print(f"{Colors.YELLOW}Date: {date}, Points: {points}, Assists: {assists}, "
                  f"Rebounds: {rebounds}, Blocks: {blocks}, Steals: {steals}, "
                  f"Turnovers: {turnovers}, FG%: {fg_percentage}, Minutes Played: {minutes_played}, "
                  f"3P Made: {three_pointers_made}, 3P Attempted: {three_pointers_attempted}{Colors.RESET}")
        
        # Ask if the user wants to continue or exit
        continue_choice = input(f"{Colors.BLUE}Would you like to check another player? (yes/no): {Colors.RESET}").strip().lower()
        if continue_choice not in ['yes', 'y']:
            print(f"{Colors.GREEN}Exiting the program. Goodbye!{Colors.RESET}")
            break

if __name__ == "__main__":
    main()