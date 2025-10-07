'''
Translating quarto epub
to a different language using openai
'''

from openai import OpenAI
import glob
import shutil

client = OpenAI()

language = 'Spanish' # 'French', 'Spanish'
base_folder = 'English'
effort = 'medium' # could be 'minimal', 'low', 'medium', 'high'
model = 'gpt-5'


system_prompt = fr"""I am going to give a set of text for a book in markdown format. I want you to translate the text from English to {language}. Do not change text inside of special markdown, Latex, or html sections. So for example this section

::: {{.callout-note icon=false}}
When using different paths to file locations, Windows machines use backslashes, e.g. `C:\Users\andre`, whereas Mac and Unix machines use forward slashes, `/users/andre`.
:::

You would not change the lines with the three colons, nor the text inside of the backticks. But you would change the rest of the text to {language}."""

def translate(text,system_prompt=system_prompt,effort=effort,client=client,model=model):
    response = client.responses.create(
        model=model,
        reasoning={"effort": effort},
        input=[
                {"role": "developer","content": system_prompt},
                {"role": "user","content": text}
              ]
    )
    res_text = response.output_text
    return res_text


def get_qmd(folder=base_folder):
    file_paths = glob.glob(f"{folder}/*.qmd")
    fp = {}
    for p in file_paths:
        with open(p, "r", encoding="utf-8") as f:
            fp[p] = f.read()
    return fp

def split_text(text):
    back_tick = False
    s1 = text.split("\n\n")
    # for sections that are ```, combining them back
    s2 = []
    for s in s1:
        if back_tick:
            st += "\n\n" + s
            if s[-3:] == '```':
                back_tick = False
                s2.append(st)
        else:
            st = s
            if s[:3] == '```':
                if s[-3:] == '```':
                    s2.append(s)
                    back_tick = False
                else:
                    back_tick = True
            else:
                back_tick = False
                s2.append(s)
    return s2

def trans_file(in_folder=base_folder,out_folder=language):
    shutil.copytree(in_folder,out_folder, dirs_exist_ok=True)
    qmd = get_qmd(folder=out_folder)
    for qfile, qtext in qmd.items():
        print(f'Translating {qfile}')
        stext = split_text(qtext)
        print(f'There are a total of {len(stext)} sections to translate')
        snew = []
        for i,s in enumerate(stext):
            if s[:3] == '```':
                print('Code block skipping')
                snew.append(s)
            elif s[:4] == '![](':
                print('Image skipping')
                snew.append(s)
            elif s == '':
                print('Blank Line')
                snew.append(s)
            else:
                res = translate(s)
                snew.append(res)
            print(f'Translated {i+1}')
        sfin = "\n\n".join(snew)
        with open(qfile, "w", encoding="utf-8") as f:
            f.write(sfin)


if __name__ == '__main__':
    trans_file()

