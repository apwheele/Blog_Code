'''
This creates the report
but changes the date for the 
html file
'''

import os
import sys
from datetime import datetime

today = datetime.today()
cdate = today.strftime("%Y_%m_%d")
report_name = f'StatsReport_{cdate}.html'
cmd = f'jupyter nbconvert --execute example_report.ipynb --no-input --to html'
os.system(cmd) # generating report

# If report with date currently exists, remove
if os.path.exists(report_name):
  os.remove(report_name)

# Now renaming the base report to the current date
if sys.platform == 'win32':
    # If on windows use ren
    os.system(f'ren example_report.html {report_name}')
else:
    # Else use mv
    os.system(f'mv example_report.html {report_name}')