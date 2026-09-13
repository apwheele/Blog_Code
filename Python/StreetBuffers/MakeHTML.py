'''
Converts BuffersVsNetwork.md to a standalone html page. Images already point
at raw.githubusercontent.com, so the html works on its own with nothing local.
'''

import re
import markdown

SRC, OUT = 'BuffersVsNetwork.md', 'BuffersVsNetwork.html'
TITLE = 'Fixed width buffers versus street network measures'

CSS = '''
body {font-family: Verdana, Geneva, sans-serif; font-size: 15px;
      line-height: 1.65; color: #222; max-width: 860px;
      margin: 40px auto; padding: 0 20px;}
h1 {font-size: 26px; border-bottom: 2px solid #286090; padding-bottom: 6px;
    margin-top: 42px;}
h2 {font-size: 20px; margin-top: 32px;}
a {color: #286090;}
img {max-width: 100%; height: auto; display: block; margin: 18px auto;}
pre {background: #f5f5f5; border-left: 3px solid #455778; padding: 12px 14px;
     overflow-x: auto; font-size: 13px; line-height: 1.45;}
code {font-family: Consolas, Monaco, monospace; font-size: 13px;}
pre code {background: none;}
p code, li code {background: #f5f5f5; padding: 1px 4px; border-radius: 3px;}
table {border-collapse: collapse; margin: 18px 0; font-size: 13px;
       display: block; overflow-x: auto; max-width: 100%;}
th, td {border: 1px solid #ddd; padding: 5px 9px; text-align: right;}
th {background: #455778; color: white; font-weight: normal;}
tr:nth-child(even) {background: #f7f7f7;}
blockquote {border-left: 3px solid #C5C88F; margin-left: 0; padding-left: 14px;
            color: #555;}
'''

PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
'''


def convert():
    md = open(SRC, encoding='utf-8').read()
    # drop the leading title comment, it is for my own filing
    md = re.sub(r'^<!---.*?-->\s*', '', md, flags=re.S)
    body = markdown.markdown(md, extensions=['tables', 'fenced_code',
                                             'sane_lists'])
    html = PAGE.format(title=TITLE, css=CSS, body=body)
    open(OUT, 'w', encoding='utf-8').write(html)
    print(f'wrote {OUT} ({len(html):,} bytes)')


if __name__ == '__main__':
    convert()
