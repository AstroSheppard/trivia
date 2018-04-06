import pygsheets
import pandas as pd

# Functions that retrieve information from LL website or google sheet

def access():
    """Authorize access to google sheet"""
    json='trivia-727e12dbc64c.json'
    ### Get credentials/ authorize
    gc=pygsheets.authorize(service_file='trivia-727e12dbc64c.json')
    ### Read in entire sheet
    sheet = gc.open("Trivia")
    return sheet

def get_player_answers(player):
    """ Get answers as Pandas DataFrame from 
    player x from google sheet"""
    sheet=access()
    wks=sheet.worksheet_by_title(player)
    ans=wks.get_as_df(start='B2',end='C8')
    wks.unlink()
    return ans

def get_matchups(our_md):
    """Read in matchups from schedule as a dict"""
    df = pd.read_csv('schedule.csv')
    matchups=df[df['Match Day'] == int(our_md)].to_dict(orient='records')[0]
    matchups.pop('Match Day')
    return matchups

def get_answers(s, md): 
    """Read in answers from csv as Pandas dataframe"""
    template='./answers/ll{season}md{match}_answers.csv'
    a=pd.read_csv(template.format(season=s, match=md))
    return a

def get_questions(s, md):
    """Read in questions from csv as Pandas dataframe"""
    template='./questions/ll{season}md{match}.csv'
    q=pd.read_csv(template.format(season=s, match=md))
    return q
