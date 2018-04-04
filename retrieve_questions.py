# Run as python2 get_questions.py ll# MD#
# For LL 39-42 will get questions and images in one file,
# answers and percent right in another
# 43-51 need different parsing
# 52 works

from urllib2 import urlopen
import bs4
from bs4 import BeautifulSoup as bs
import pygsheets
import pandas as pd
import numpy as np
import sys
import re


s=sys.argv[1]
si=int(s)
md=sys.argv[2]

# url that we are scraping
if si > 51:
    template="https://learnedleague.com/match.php?{season}&{match}"
else:
    template = "https://learnedleague.com/ll{season}/questions/ll{season}md{match}questions.htm"

# this is the html from the given url

url=template.format(season=s,match=md)
link = urlopen(url)

soup =bs(link,'html.parser')

row=[]
ans=[]
images=[]
image_temp="https://learnedleague.com{im}"


# Depending on the season, the html stores answers, % right, categories
# and images differently. We extract those based on the season
if si > 51:
   
    z=soup.findAll(class_=re.compile('ind-Q20'))
    a=soup.findAll(class_=re.compile('answer3'))
    for item in z:
        item.span.extract()
        if item.a != None:
            images.append(image_temp.format(im=item.a.get('href')))
        else:
            images.append('')
 
    questions=[item.getText().encode('utf-8').partition('-')[2].strip()
               for item in z]
    categories=[item.getText().encode('utf-8').partition('-')[0].strip()
                for item in z]
    ans=[item.getText().encode('utf-8').partition('wer')[2].strip() for item in a]
    perc_right = soup.findAll('tr')[-2].getText().splitlines()[3:-1]

    


elif si > 42:
    perc_right = [td.getText() for td in soup.findAll('tr')[-2].findAll('td')][2:-1]
    z=soup.findAll(class_=re.compile('ind-Q2'))
    for item in z:
        item.span.extract()
        ans.append(item.span.extract().getText().encode('utf-8'))
        if item.a != None:
            im=item.a.get('href')
            images.append(image_temp.format(im=im))
        else:
            images.append('')
    questions=[item.getText().partition('-')[2].strip() for item in z]
    categories=[item.getText().partition('-')[0].strip() for item in z]



else:
    column_headers = [th.getText() for th in soup.findAll('tr', limit=2)[1]]
    col=["Questions"]+column_headers
    data_rows = soup.findAll('tr')[2:]  # skip the first 2 header rows
    league = [[td.getText() for td in data_rows[i].findAll('td')] for i in
              range(len(data_rows)-1)]
    df = pd.DataFrame(league, columns=col)
    perc_right=df['R'].values
    z=soup.findAll(class_=re.compile('ind-Q'))[1:]
    for item in z[:-1]:
        # print item.contents
        a=item.span
        ans.append(a.getText().encode('utf-8'))
        item.span.extract()
        row.append(item.getText().encode('utf-8'))
        if item.a != None:
            im=item.a.get('href')
            images.append(image_temp.format(im=im))
        else:
            images.append('')

    categories=[item.partition('-')[0] for item in row]
    questions=[item.partition('-')[2].partition('\xc2\xa0')[0]
               for item in row]


# Now we combine the categories, questions, and images to a data frame to be
# written to the google sheet, and the answers and percent right to a CSV
# to be saved.
data=np.asarray([categories, questions,images]).T
trivia=pd.DataFrame(data, columns=['CATEGORY','QUESTION','IMAGE'])
answers=pd.DataFrame(np.asarray([ans, perc_right]).T,
                     columns=['ANSWERS','PERC_RIGHT'])

    
    
### Save answers to a csv
temp2='./answers/ll{s}md{m}_answers.csv'
answers.to_csv(temp2.format(s=s, m=md))
temp3='./questions/ll{s}md{m}.csv'
trivia.to_csv(temp3.format(s=s, m=md))

# Write questions to the google sheet

json='trivia-727e12dbc64c.json'

### Get credentials/ authorize
gc=pygsheets.authorize(service_file='trivia-727e12dbc64c.json')


### Read in entire sheet
sheet = gc.open("Trivia")
### Get worksheet
wks=sheet.worksheet_by_title("Home")
    
wks.set_dataframe(trivia,(10,1))
