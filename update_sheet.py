from datetime import date, datetime
import os.path
import sys

import pygsheets
import numpy as np
import re
import pandas as pd

from get_functs import access, get_player_answers, get_matchups, get_answers
from get_functs import get_questions

def correct(player, answer):
    right= [player.values[i].decode('utf-8').upper() ==
            answer.values[i].decode('utf-8') for i in range(len(answer))]
    for i in range(len(right)):
        if not right[i] and not player.values[i] == 'x':
            print 'Player Answer: ', player.values[i]
            print 'Answer: ', answer.values[i]
            right[i]=int(raw_input('Is this correct? '))
    return right

def determine_winner(data, p1, p2):
    player1=data.loc[:,p1+'_pts':p1+'_correct']
    player2=data.loc[:,p2+'_pts':p2+'_correct']
    result=pd.DataFrame(columns=['Q',p1, p2])
    result['Q']=range(1,7)
    result[p1]=player2.iloc[:,0]
    result[p2]=player1.iloc[:,0]
    p1score= (player1.iloc[:,1].values*result[p1].values).sum()
    p2score=(player2.iloc[:,1].values*result[p2].values).sum()
    score= [['Total',p1score,p2score]]
    result=result.append(pd.DataFrame(score, columns=result.columns.values)
                  ,ignore_index=True)

    colors=pd.DataFrame()
    if p1score > p2score:
        match={'winner':p1,'loser':p2, 'tie':False}
        colors[p1]=np.append(player1.iloc[:,1].values,1)
        colors[p2]=np.append(player2.iloc[:,1].values,0)
    elif p1score == p2score:
        match={'winner':p1,'loser':p2, 'tie':True}
        colors[p1]=np.append(player1.iloc[:,1].values,2)
        colors[p2]=np.append(player2.iloc[:,1].values,2)
    else:
        match={'winner':p2,'loser':p1, 'tie':False}
        colors[p1]=np.append(player1.iloc[:,1].values,0)
        colors[p2]=np.append(player2.iloc[:,1].values,1)

    # write results to sheet

  
    sheet=access()
    wks=sheet.worksheet_by_title("Results")
    green=(0,1,0,0)
    space=wks.range('A1:C8')

    for i in range(1,8):
        for j in range(1,3):
            space[i][j].unlink()
            if colors.iloc[i-1,j-1]==1:
                space[i][j].color=green
                space[i][j].link(wks)
                space[i][j].update()
            elif colors.iloc[i-1,j-1]==2:
                space[i][j].color=(.5,.5,.5,0)
                space[i][j].link(wks)
                space[i][j].update()
    wks.set_dataframe(result,(1,1))
    wks.adjust_column_width(0,pixel_size=35)
    wks.adjust_column_width(1,pixel_size=60)
    wks.adjust_column_width(2,pixel_size=60)
    day=datetime.today()
    date=(datetime.strftime(day,'%m/%d/%y'))
    wks.update_cell('B9',date)
    wks.insert_cols(0, number=4)
    wks.unlink()
    return match

def write_qa(s, md, perc):
    sheet=access()
    wks=sheet.worksheet_by_title("Results")
    ans=get_answers(s,md)
    del ans['Unnamed: 0']
    quest=get_questions(s,md)
    total=pd.concat([quest,ans, perc], axis=1)
    total.columns.values[0]='NUMBER'
    total.columns.values[6]='PERC_US'
    total['NUMBER'].add(1)
    wks.set_dataframe(total, start='J11')
    wks.unlink()


def get_perc(data, people):
    perc=pd.DataFrame([data[key+'_correct'].values for key in people])
    return perc.sum(axis=0)/float(len(perc))*100

def append_md(data, s, md):
    data['Season']=s
    data['Match Day']=md
    if os.path.isfile('all_data.csv'):
        all_data=pd.read_csv('all_data.csv')
        all_data=all_data.append(data, ignore_index=True)
        all_data.to_csv('all_data.csv')
    else:
        data.to_csv('all_data.csv')

def update_player(player, correct):
    sheet=access()
    wks=sheet.worksheet_by_title(player)

    wks.unlink()
    ### Define colors
    green=(0,1,0,0)
    red=(1,.5,.5,0)
    white=(1,1,1,1)

    inputs=wks.get_as_df(start='B3',end='C8')
    wks.clear(start='B3', end='C8')
    old=wks.range('B3:C8')
    # Set the color to green if right
    for i in range(len(correct)):
        old[i][0].unlink()
        if correct[i]==1:
            old[i][0].color=green
            old[i][0].link(wks)
            old[i][0].update()
    wks.set_dataframe(inputs, 'B3')

    # Move answers from yesterday over
    wks.insert_cols(0, number=4)

    # Remake table for current day
    
    head=wks.get_values('E2','G2', returnas='matrix')
    num=wks.get_values('E3','E8', returnas='matrix')
    wks.update_cells(crange='A2:C2',values=head)
    wks.update_cells(crange='A3:A8',values=num)
    wks.adjust_column_width(1,pixel_size=120)

    # Get date
    day=datetime.today()
    date=(datetime.strftime(day,'%m/%d/%y'))

    wks.update_cell('B1',date)

def update_standings(results):
    sheet=access()
    wks=sheet.worksheet_by_title('Standings')
    wks.unlink()
    standings1=wks.get_as_df(start='B1',end='F5')
    standings2=wks.get_as_df(start='B9', end='F13')
    w=results['winner']
    l=results['loser']
    if results['tie']:
        if w in standings1['NAME'].values:
            standings1.loc[standings1['NAME']==w,'T']+=1
            standings1.loc[standings1['NAME']==w,'MP']+=1
        else:
            standings2.loc[standings2['NAME']==w,'T']+=1
            standings2.loc[standings2['NAME']==w,'MP']+=1
        if l in standings1['NAME'].values:
            standings1.loc[standings1['NAME']==l,'T']+=1
            standings1.loc[standings1['NAME']==l,'MP']+=1
        else:
            standings2.loc[standings2['NAME']==l,'T']+=1
            standings2.loc[standings2['NAME']==l,'MP']+=1
    else:
        if w in standings1['NAME'].values:
            standings1.loc[standings1['NAME']==w,'W']+=1
            standings1.loc[standings1['NAME']==w,'MP']+=2
        else:
            standings2.loc[standings2['NAME']==w,'W']+=1
            standings2.loc[standings2['NAME']==w,'MP']+=2
        if l in standings1['NAME'].values:
            standings1.loc[standings1['NAME']==l,'L']+=1
        else:
            standings2.loc[standings2['NAME']==l,'L']+=1
    standings1=standings1.sort_values('MP', ascending=False)
    standings2=standings2.sort_values('MP', ascending=False)
    wks.set_dataframe(standings1, 'B1')
    wks.set_dataframe(standings2, 'B9')
    wks.sync()
    
#########################################################################
################################# MAIN ##################################
#########################################################################
if __name__ == "__main__":
    s=sys.argv[1]
    md=sys.argv[2]
    our_md=sys.argv[3]
    data=pd.DataFrame()
    data['categories']=get_questions(s,md)['CATEGORY']
    data['answers']=get_answers(s, md)['ANSWERS']
    matchups=get_matchups(our_md)
    done=set()

    for key in matchups:
        if key not in done:
            p1=get_player_answers(key)
            data[key+'_ans']=p1['ANSWER']
            data[key+'_pts']=p1['PTS']
            data[key+'_correct']=correct(p1['ANSWER'], data['answers'])
            p2=get_player_answers(matchups[key])
            data[matchups[key]+'_ans']=p2['ANSWER']
            data[matchups[key]+'_pts']=p2['PTS']
            data[matchups[key]+'_correct']=correct(p2['ANSWER']
                                                   ,data['answers'])

            win=determine_winner(data, matchups[key], key)
            
            update_standings(win) 
            update_player(key, data[key+'_correct'].values)
            update_player(matchups[key], data[matchups[key]+'_correct'].values)
        
            done.add(matchups[key])
     
    perc=get_perc(data, matchups)
    write_qa(s, md, perc)

    data=data.reindex(sorted(data.columns), axis=1)
    append_md(data,s, md)


