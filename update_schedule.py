import sys

import pygsheets
import pandas as pd

from get_functs import access

def update_schedule(md):
    sheet=access()
    wks=sheet.worksheet_by_title('Schedule')
    wks.unlink()
    test=wks.range('A2:I14')
    start='A'+str(int(md)+1)
    end='I'+str(int(md)+1)
    hold=wks.get_as_df(start=start, end=end)
    wks.clear(start=start, end=end)
    row=start+':'+end
    cells=wks.range(row)[0]

    start2='A'+str(int(md))
    end2='I'+str(int(md))
    hold2=wks.get_as_df(start=start2, end=end2)
    wks.clear(start=start2, end=end2)
    row2=start2+':'+end2
    cells2=wks.range(row2)[0]
    
    for i in range(len(cells)):
        cells[i].color=(1,1,.5,.3)
        cells2[i].color=(1,1,1,1)
    wks.set_dataframe(hold,start)
    wks.set_dataframe(hold2,start2)
    wks.sync()

if __name__ == "__main__":
    md=sys.argv[1]
    update_schedule(md)
