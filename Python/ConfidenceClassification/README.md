# Confidence in Classification using Conformal Inference

This project shows how to take the log probabilities from an LLM, and determine thresholds to set the recall or estimate the false positive rate given a probability threshold.

It uses data from the [Jigsaw toxic comment Kaggle competition](https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge/data). You need to download the `train.csv.zip` file to be able to replicate. Run the code in 01 (which requires to wait until a prior batch is finished to submit the next batch), then once all batches are finished, can run 02. 03 then analyzes the data.

For python environment, just need the openai library, requests, scipy, and pandas.

Uses OpenAI (gpt-4o-mini) to do the classification and get the log-probs in batches.

See blog post [for description](https://crimede-coder.com/blogposts/2026/ConfClassification)

This is an appendix to the book, [Large Language Models for Mortals: A Practical Guide for Analysts with Python](https://crimede-coder.com/blogposts/2026/LLMsForMortals). Buy the book!

