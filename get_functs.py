import pygsheets
import pandas as pd

# Functions that retrieve information f

def access():
    json='trivia-727e12dbc64c.json'
    ### Get credentials/ authorize
    gc=pygsheets.authorize(service_file='trivia-727e12dbc64c.json')
    ### Read in entire sheet
    sheet = gc.open("Trivia")
    return sheet

def get_player_answers(player):
    sheet=access()
    wks=sheet.worksheet_by_title(player)
    ans=wks.get_as_df(start='B2',end='C8')
    wks.unlink()
    return ans

def get_matchups(md):
    df = pd.read_csv('schedule.csv')
    matchups=df[df['Match Day'] == int(md)].to_dict(orient='records')[0]
    matchups.pop('Match Day')
    return matchups

def get_answers(s, md):
    template='./answers/ll{season}md{match}_answers.csv'
    a=pd.read_csv(template.format(season=s, match=md))
    return a

def get_questions(s, md):
    template='./questions/ll{season}md{match}.csv'
    q=pd.read_csv(template.format(season=s, match=md))
    return q
