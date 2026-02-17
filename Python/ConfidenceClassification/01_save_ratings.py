# Generating probabilities
# for toxic comments 
# data via
# https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge/data

from openai import OpenAI
import pandas as pd
import os
import tiktoken
import json
from math import ceil
import time

client = OpenAI()

train = pd.read_csv('train.csv.zip')
train['row'] = train.index

# Working with obscene
field = 'obscene'

# Lets get a sample of positive/negative/other toxic for many-shot
positive = train[train[field] == 1]
negative = train[train['toxic'] == 0]
other = train[(train[field] == 0) & (train['toxic'] == 1)]

k_sample = 10
seed = 10

pos_samp = positive.sample(k_sample,random_state=seed)
neg_samp = negative.sample(k_sample,random_state=seed)
oth_samp = other.sample(k_sample,random_state=seed)

# should be shuffled randomly by original row
comb_samp = pd.concat([pos_samp,neg_samp,oth_samp]).sort_values(by='row')


# Building the prompt

pos_txt = "--------------------------------"
for i in comb_samp.itertuples():
    pos_txt += f"\nExample: {i.comment_text}\n"
    if i._asdict()[field] == 1:
        pos_txt += "Output: True"
    else:
        pos_txt += "Output: False\n"
    pos_txt += "--------------------------------"



system = f"""You are classifying online comments for toxic speech. 
Here we are identifying obscene comments. These include vulgar commentary
and profanity. Here are examples of comments and the expected binary classification:

{pos_txt}

I am now going to present a new comment. Return True if the comment is obscene, otherwise
return False. Only return True or False.

Example:
"""

# This will be the sample I use to estimate the conformal limits
# need to sample on the outcome
conf_size = 1000

# taking out the k-shot examples
pc_samp = positive[~positive['row'].isin(pos_samp['row'])].sample(conf_size,random_state=seed)
nc_samp = negative[~negative['row'].isin(neg_samp['row'])].sample(conf_size,random_state=seed)
ot_samp = other[~other['row'].isin(oth_samp['row'])].sample(conf_size,random_state=seed)

conf_samp = pd.concat([pc_samp,nc_samp,ot_samp])
conf_samp.to_csv('conf_samp.csv.zip',index=False)


# BUILDING BATCH FOR CONF SAMPLE

# Build the batch requests
conf_batch_requests = []

for i in conf_samp.itertuples():
    request = {
        "custom_id": str(i.row),
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "prompt_cache_key": "identify_obscene",
            "max_tokens": 1,
            "logprobs": True,
            "top_logprobs": 20,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": i.comment_text},
                {"role": "assistant", "content": "Output:"}
            ]
        }
    }
    conf_batch_requests.append(request)

# See if this file exists, if it does, move on
if os.path.exists("conf_batch_input.jsonl"):
    pass
else:
    # Write to JSONL file
    with open("conf_batch_input.jsonl", "w") as f:
        for req in conf_batch_requests:
            f.write(json.dumps(req) + "\n")
    # size should be ok, need to be under 200mb or 50k requests
    size_mb = os.path.getsize("conf_batch_input.jsonl") / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
    # Upload the batch input file
    conf_batch_file = client.files.create(
        file=open("conf_batch_input.jsonl", "rb"),
        purpose="batch"
    )
    conf_batch_job = client.batches.create(
        input_file_id=conf_batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    # Save batch ID to a file for later retrieval
    with open("conf_batch_id.txt", "w") as f:
        f.write(conf_batch_job.id)


###############################
# COST ESTIMATES PER 10K RECORDS

# For 4o-mini, note with large amounts of caching
# 5-mini may actually be cheaper

encoding = tiktoken.encoding_for_model("gpt-4o-mini")
system_tokens = len(encoding.encode(system)) # this should get cache hits


if system_tokens > 1024:
    not_cache_part = system_tokens % 128
    cache_part = system_tokens - not_cache_part
else:
    not_cache_part = system_tokens
    cache_part = 0

ss = train['comment_text'].sample(1000,random_state=seed)
comment_sample_tokens = [len(encoding.encode(i)) for i in ss]
mean_comment_tokens = sum(comment_sample_tokens)/len(comment_sample_tokens) + not_cache_part

batch = True
total_records = 10000

if batch:
    cache_hit = 0.0 # I am not getting any caching with batching
    input_cost = mean_comment_tokens*(0.15/1e6)*total_records
    cache_cost = 0
    not_cache_cost = cache_part*(0.15/1e6)*(total_records*(1-cache_hit))
    output_cost = 1*(0.60/1e6)*total_records
    total_cost_per_record = input_cost + cache_cost + not_cache_cost + output_cost
    print(f'Estimated cost per 10k batch records ${total_cost_per_record/2:,.2f}')
else:
    cache_hit = 0.99 # will probably be higher than this
    input_cost = mean_comment_tokens*(0.15/1e6)*total_records
    cache_cost = cache_part*(0.075/1e6)*(total_records*cache_hit)
    not_cache_cost = cache_part*(0.15/1e6)*(total_records*(1-cache_hit))
    output_cost = 1*(0.60/1e6)*total_records
    total_cost_per_record = input_cost + cache_cost + not_cache_cost + output_cost
    print(f'Estimated cost per 10k records ${total_cost_per_record:,.2f}')
###############################


# LARGER SAMPLE TO TEST OUT CONFORMAL BANDS

# Now lets score another large batch
llm_size = 50000
batch_size = 10000

# taking out the k-shot examples and conformal samples
samp_keys = comb_samp['row'].to_list() + conf_samp['row'].to_list()

llm_test = train[~train['row'].isin(samp_keys)].sample(llm_size,random_state=seed)
llm_test.to_csv('llm_test_samp.csv.zip',index=False)

# BUILDING BATCH FOR TEST SAMPLE
batch_size = 10000 # entire 50 k is too large

b,e = 0, batch_size

n_batches = ceil(llm_size/batch_size)

for j in range(n_batches):
    sub = llm_test.iloc[b:min(e,llm_test.shape[0]),]
    # Build the batch requests
    test_batch_requests = []
    for i in sub.itertuples():
        request = {
            "custom_id": str(i.row),
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "prompt_cache_key": "identify_obscene",
                "max_tokens": 1,
                "logprobs": True,
                "top_logprobs": 20,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": i.comment_text},
                    {"role": "assistant", "content": "Output:"}
                ]
            }
        }
        test_batch_requests.append(request)
    # Write to JSONL file
    with open(f"test_batch_input_{j}.jsonl", "w") as f:
        for req in test_batch_requests:
            f.write(json.dumps(req) + "\n")
    # size should be ok, need to be under 200mb or 50k requests
    size_mb = os.path.getsize(f"test_batch_input_{j}.jsonl") / (1024 * 1024)
    print(f"File size batch {j}: {size_mb:.2f} MB")
    # Upload the batch input file
    #test_batch_file = client.files.create(
    #    file=open(f"test_batch_input_{j}.jsonl", "rb"),
    #    purpose="batch"
    #)
    #test_batch_job = client.batches.create(
    #    input_file_id=test_batch_file.id,
    #    endpoint="/v1/chat/completions",
    #    completion_window="24h"
    #)
    ## Save batch ID to a file for later retrieval
    #with open(f"test_batch_id_{j}.txt", "w") as f:
    #    f.write(test_batch_job.id)
    b += batch_size
    e += batch_size

# I get error
# 'Enqueued token limit reached for gpt-4o-mini in organization ..... 
# Limit: 40,000,000 enqueued tokens
# so need to wait for batch 0 to complete before going to batch 2
# so I just ran this manually for each of the 5 batches

def upload_check_batch(j):
    test_batch_file = client.files.create(
        file=open(f"test_batch_input_{j}.jsonl", "rb"),
        purpose="batch"
    )
    test_batch_job = client.batches.create(
        input_file_id=test_batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    # Save batch ID to a file for later retrieval
    with open(f"test_batch_id_{j}.txt", "w") as f:
        f.write(test_batch_job.id)
    time.sleep(2*60) # wait two minutes to validate
    batch_job = client.batches.retrieve(test_batch_job.id)
    print(batch_job.status) # should not have failed, need to wait for after validating