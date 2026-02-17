# code to get and save the batch results

from openai import OpenAI
import json
import pandas as pd
import glob
import gzip
from math import exp

client = OpenAI()

# I just check later, do not worry about polling
with open("conf_batch_id.txt","r") as f:
    conf_batch_id = f.read().strip()

conf_batch_job = client.batches.retrieve(conf_batch_id)
print(conf_batch_job.status) # should be completed

conf_result_file = client.files.content(conf_batch_job.output_file_id)
with gzip.open('batch_conf_result.jsonl.gz', 'wt', encoding='utf-8') as f:
    f.write(conf_result_file.text)

# Parse the results
results = []
for line in conf_result_file.text.strip().split("\n"):
    r = json.loads(line)
    cid = r['custom_id']
    info = {'row': int(cid)}
    ch = r['response']['body']['choices'][0]
    ref = ch['message']['refusal']
    if ref is None:
        lpr = []
        lps = ch['logprobs']['content'][0]['top_logprobs']
        for i,lp in enumerate(lps):
            ifill = str(i+1).zfill(2)
            info[f'Token_{ifill}'] = lp['token']
            info[f'lp_{ifill}'] = lp['logprob']
    else:
        info['refusal'] = 1
    results.append(info)

# Save those results
conf_res = pd.DataFrame(results)
conf_res.to_csv('conf_probs.csv.zip',index=False)

# Lets get the top prob for true/false
tokenF, logprobF = [], []
for i in range(20):
    iz = str(i+1).zfill(2)
    tokenF.append(f'Token_{iz}')
    logprobF.append(f'lp_{iz}')

def top_prob(x,token_find='True'):
    tokens = x[:20]
    lps = x[20:]
    for t,l in zip(tokens,lps):
        if t == token_find:
            return exp(l)
    return 0.0

conf_res['TrueProb'] = conf_res[tokenF + logprobF].apply(top_prob,axis=1)
conf_res['FalseProb'] = conf_res[tokenF + logprobF].apply(top_prob,token_find='False',axis=1)

# Lets merge in actual and get the info I need
conf_samp = pd.read_csv('conf_samp.csv.zip')
fk = ['row','comment_text','obscene','toxic']
conf_res = conf_res.merge(conf_samp[fk],on='row')

fk += ['FalseProb','TrueProb']
fk.remove('comment_text')
conf_res[fk].to_csv('MetricConfSamp.csv.zip')

# Now getting the batches for the test sample
test_files = glob.glob("test_batch_id_*.txt")

# test that they are all done first
for t in test_files:
    print(t)
    with open(t,"r") as f:
        batch_id = f.read().strip()
    batch_job = client.batches.retrieve(batch_id)
    print(batch_job.status) # should all be completed


test_dfl = []
for t in test_files:
    with open(t,"r") as f:
        batch_id = f.read().strip()
    batch_job = client.batches.retrieve(batch_id)
    print(batch_job.status) # should be completed
    tn = t.replace(".txt",".jsonl.gz")
    result_file = client.files.content(batch_job.output_file_id)
    with gzip.open(f'br_{tn}','wt', encoding='utf-8') as f:
        f.write(result_file.text)
    # Parse the results
    results = []
    for line in result_file.text.strip().split("\n"):
        r = json.loads(line)
        cid = r['custom_id']
        info = {'row': int(cid)}
        ch = r['response']['body']['choices'][0]
        ref = ch['message']['refusal']
        if ref is None:
            lpr = []
            lps = ch['logprobs']['content'][0]['top_logprobs']
            for i,lp in enumerate(lps):
                ifill = str(i+1).zfill(2)
                info[f'Token_{ifill}'] = lp['token']
                info[f'lp_{ifill}'] = lp['logprob']
            info['usage'] = r['response']['body']['usage']
        else:
            info['refusal'] = 1
        results.append(info)
    tres = pd.DataFrame(results)
    test_dfl.append(tres.copy())

tres_full = pd.concat(test_dfl)
tres_full.to_csv('test_probs.csv.zip',index=False)

# Merge in full sample, 

tres_full['TrueProb'] = tres_full[tokenF + logprobF].apply(top_prob,axis=1)
tres_full['FalseProb'] = tres_full[tokenF + logprobF].apply(top_prob,token_find='False',axis=1)

# Lets merge in actual and get the info I need
tres_samp = pd.read_csv('llm_test_samp.csv.zip')
fk = ['row','comment_text','obscene','toxic']
tres_full = tres_full.merge(tres_samp[fk],on='row')

fk += ['FalseProb','TrueProb']
fk.remove('comment_text')
tres_full[fk].to_csv('MetricTestSamp.csv.zip')
