import pandas as pd

# Function to normalize team names to match the team_data index
def normalize_team_name_updated(name, year):
    # Mapping of full team names to city names as they appear in the team_data index
    team_name_mapping = {
        'Baltimore Ravens': 'Baltimore',
        'Dallas Cowboys': 'Dallas',
        'Indianapolis Colts': 'Indianapolis',
        'New England Patriots': 'New England',
        'Buffalo Bills': 'Buffalo',
        'Pittsburgh Steelers': 'Pittsburgh',
        'Tennessee Titans': 'Tennessee',
        'Tampa Bay Buccaneers': 'Tampa Bay',
        'Arizona Cardinals': 'Arizona',
        'Los Angeles Chargers': 'LA Chargers',
        'LA Chargers': 'LA Chargers',
        'Los Angeles Rams': 'LA Rams',
        'LA Rams': 'LA Rams',
        'St. Louis Rams': 'LA Rams',
        'Miami Dolphins': 'Miami',
        'Atlanta Falcons': 'Atlanta',
        'Jacksonville Jaguars': 'Jacksonville',
        'Cleveland Browns': 'Cleveland',
        'Detroit Lions': 'Detroit',
        'New Orleans Saints': 'New Orleans',
        'Washington Redskins': 'Washington',
        'Washington Football Team': 'Washington',
        'Washington Commanders': 'Washington',
        'Carolina Panthers': 'Carolina',
        'Minnesota Vikings': 'Minnesota',
        'Denver Broncos': 'Denver',
        'Green Bay Packers': 'Green Bay',
        'Kansas City Chiefs': 'Kansas City',
        'Oakland Raiders': 'Las Vegas',
        'Las Vegas Raiders': 'Las Vegas',
        'Philadelphia Eagles': 'Philadelphia',
        'Cincinnati Bengals': 'Cincinnati',
        'Houston Texans': 'Houston',
        'New York Giants': 'NY Giants',
        'New York Jets': 'NY Jets',
        'San Francisco 49ers': 'San Francisco',
        'Seattle Seahawks': 'Seattle',
        'Chicago Bears': 'Chicago'
    }
    normalized_name = team_name_mapping.get(name, None)
    if normalized_name:
        return normalized_name + str(year)
    else:
        return None  # If a name can't be normalized, we'll return None

# Function to extract year from the headings and map it correctly to each game
def extract_season_year(df):
    # Initialize a column for the season year
    df['Season_Year'] = None
    current_year = None

    # Loop through the dataframe to assign the correct season year
    for index, row in df.iterrows():
        if 'Regular Season' in str(row['Unnamed: 0']) or 'Playoffs' in str(row['Unnamed: 0']):
            current_year = str(row['Unnamed: 0']).split(' ')[0]
        df.at[index, 'Season_Year'] = current_year

    # Drop rows without a game date
    df = df[pd.to_datetime(df['Unnamed: 1'], errors='coerce', format='%b %d, %Y').notnull()]
    return df

# Function to add team stats to spread data
def add_team_stats(spread_data, team_data):
    favorite_team_stats = team_data.loc[spread_data['FavoriteTeamYear']].reset_index(drop=True)
    favorite_team_stats.columns = ['Favorite' + col for col in favorite_team_stats.columns]
    
    underdog_team_stats = team_data.loc[spread_data['UnderdogTeamYear']].reset_index(drop=True)
    underdog_team_stats.columns = ['Underdog' + col for col in underdog_team_stats.columns]
    
    final_data = pd.concat([spread_data.reset_index(drop=True), favorite_team_stats, underdog_team_stats], axis=1)
    return final_data

# Load the spreads data
spread_data_path = 'NFL_Spread_Data_2002-2021 - Sheet1.csv'
spread_data = pd.read_csv(spread_data_path)

# Extract season year from the headings
spread_data_with_year = extract_season_year(spread_data)

# Clean the data and rename the columns
spread_data_with_year = spread_data_with_year.rename(columns={
    'Unnamed: 0': 'Day', 'Unnamed: 1': 'Date', 'Unnamed: 2': 'Time', 'Unnamed: 4': 'Favorite',
    'Unnamed: 5': 'Score', 'Unnamed: 6': 'Spread', 'Unnamed: 8': 'Underdog', 'Unnamed: 9': 'OverUnder'
})

# Remove unnecessary columns and rows
spread_data_with_year = spread_data_with_year[['Day', 'Date', 'Time', 'Favorite', 'Score', 'Spread', 'Underdog', 'OverUnder', 'Season_Year']]
spread_data_with_year = spread_data_with_year.dropna(subset=['Day', 'Date'])

# Load the team data
team_data_path = 'NFL_Team_Data.csv'
team_data = pd.read_csv(team_data_path)
team_data.set_index('Team', inplace=True)

# Normalize team names and merge data
spread_data_with_year['FavoriteTeamYear'] = spread_data_with_year.apply(
    lambda row: normalize_team_name_updated(row['Favorite'], int(row['Season_Year'])), axis=1)
spread_data_with_year['UnderdogTeamYear'] = spread_data_with_year.apply(
    lambda row: normalize_team_name_updated(row['Underdog'], int(row['Season_Year'])), axis=1)
spread_data_with_year.dropna(subset=['FavoriteTeamYear', 'UnderdogTeamYear'], inplace=True)

# Add team stats to the cleaned spread data
final_dataset_all_years = add_team_stats(spread_data_with_year, team_data)

# Save the final dataset to a CSV file
final_dataset_path = 'Final_NFL_Spread_and_Team_Stats_2002-2021.csv'
final_dataset_all_years.to_csv(final_dataset_path, index=False)