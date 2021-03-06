import sys

import pygsheets
import pandas as pd
import numpy as np

from get_functs import access


def clean_data(data,s, md, players):
    data=data[(data['Season']==int(s)) & (data['Match Day']==int(md))]
    labels=['Season','Match Day', 'Unnamed: 0','answers']
    for player in players:
        labels.append(player+'_pts')
        labels.append(player+'_ans')
    data=data.drop(labels, axis=1)
    return data

if __name__ == "__main__":
    s=sys.argv[1]
    md=sys.argv[2]
    sheet=access()
    wks=sheet.worksheet_by_title('Stats')


    # read in stats dataframe
    stats=wks.get_as_df(start='A2', end='Q20', index_colum=1)
    players=wks.get_as_df(start='A1', end='S1')
    players= filter(None, players)
    data=clean_data(pd.read_csv('all_data.csv'),s,md, players)
    pc=[item+'_correct' for item in players]
    pr=[item+' Right' for item in players]
    pw=[item+' Wrong' for item in players]
    for i, cat in enumerate(data['categories'].values):
        sub=data.iloc[i,:-1].apply(pd.to_numeric, errors='ignore')
        for j,name in enumerate(pc):
            if sub.loc[name] in [1, 'True']:
                stats.loc[cat.strip(),pr[j]]+=1
            else:
                stats.loc[cat.strip(),pw[j]]+=1

    wks.set_dataframe(stats, 'B2')


