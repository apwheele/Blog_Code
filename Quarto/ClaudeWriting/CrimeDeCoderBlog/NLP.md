## NLP Applications in Crime Analysis

Generative Artificial Intelligence (e.g. ChatGPT) is all the rage these days. But most applications of natural language processing (NLP) in crime analysis are not GenAI. This post I discuss examples that are likely to be more relevant to crime analysts: named entity recognition (NER), semantic similarity search (e.g. vector embeddings), and supervised learning using text.

**Named Entity Recognition**: Or NER for short, is the application of finding/extracting specific entities in a free text string. Common examples of NER are finding names or addresses. Intelligence analysts analyzing dark web forums often want to identify when social security or bank account numbers are listed. For example, a text on a dark web forum may say "Hacked this noobs info :) checkout Andy Wheelers social 999+99/9999". NER models can take that text input and identify that "Andy Wheeler" is a name, and the number string is a personal identifier.

**Semantic Similarity Search**: Large language models reduce complicated input text into numeric embeddings. One can then use those numeric embeddings to see if two text strings are similar to one another. For example, if you created a vector database of modus operandi, if you search "pushed in A/C", and a prior text had "forced window unit", these two strings do not share any words, but are semantically similar. These can be used to index idiosyncratic databases with text, or identify similar strings of repeat crimes based on victim or officer narratives.

**Supervised Learning**: Supervised learning is fitting a machine learning model to predict a specific outcome. Examples of supervised learning using text are [identifying hate speech](https://www.kaggle.com/datasets/mrmorj/hate-speech-and-offensive-language-dataset), or [rating police narratives](https://www.cleveland.com/crime/2023/09/can-ai-solve-rape-cases-to-find-out-a-cleveland-professor-programmed-a-computer-to-analyze-thousands-of-police-reports.html) for quality purposes.

This is not to say that tools like ChatGPT cannot be useful -- one shot learning for example may work quite well in scenarios where you do not have enough data to train new models. But that being said, ChatGPT is not CJIS compliant, and so is [innapropriate to use for many crime analysis applications](https://andrewpwheeler.com/2023/08/18/security-issues-with-sending-chatgpt-sensitive-data/).

If you have interest in NLP applications and want to learn how to deploy them in a secure way, get in touch with [CRIME De-Coder](/contact). 



