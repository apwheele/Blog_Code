'''
Functions to work with Bedrock
'''

import boto3
import json
import traceback
import time
from datetime import datetime
import os
from . import chat_helpers




def get_models():
    """
    Get available foundation models from AWS Bedrock.
    
    Returns:
        dict: Dictionary of available models where key is the model name and value is the ARN.
              For inference profile models, it replaces part of the ARN with the account info.
    """
    client = boto3.client('sts')
    acct = client.get_caller_identity()['Account']
    region = client.meta.region_name
    bedrock_client = boto3.client(service_name="bedrock", region_name=region)
    response = bedrock_client.list_foundation_models()
    ms = response["modelSummaries"]
    models = {}
    for m in ms:
        # may need to check 'inferenceTypesSupported
        if 'INFERENCE_PROFILE' in m['inferenceTypesSupported']:
            # Note need the us.
            models[m['modelName']] = m['modelArn'].replace(":foundation-model/",f"{acct}:inference-profile/us.")
        elif 'ON_DEMAND' in m['inferenceTypesSupported']:
            models[m['modelName']] = m['modelArn']
    return models


models = get_models()

class ClaudeModel:
    '''
    Model Base Class, many of the args are for Claude currently
    but should be able to make it more generic
    '''
    def __init__(self,
                 model=models['Claude Sonnet 4'],
                 version='bedrock-2023-05-31',
                 max_tokens=4000,
                 top_k=250,
                 stop_sequences=[],
                 temperature=1,
                 top_p=0.999,
                 system=None,
                 ):
        self.client = boto3.client("bedrock-runtime")
        self.model_id = model
        self.version = version
        self.max_tokens = max_tokens
        self.top_k = top_k
        self.stop_sequences = stop_sequences
        self.temperature = temperature
        self.top_p = top_p
        self.system = system
        self.chat_history = []
        self.invoke_history = []
        self.inference_config = {"maxTokens": max_tokens, 
                                 "temperature": temperature,
                                 "topP": top_p}
        self.input_tokens = 0
        self.output_tokens = 0
        self.chat_summary = None
    def build_content(self,text,image=None,assistant=None,role='user',type_input=False):
        """
        Build content structure for API request.
        
        Args:
            text (str): Text content to include in the message
            image (str, optional): Image data to include in the message. Defaults to None.
            assistant (str, optional): Assistant's response to include. Defaults to None.
            role (str, optional): Role of the message sender. Defaults to 'user'.
            type_input (bool, optional): Whether to use new format with explicit type. Defaults to False.
            
        Returns:
            dict or list: Message content structure for API request
        """
        if type_input:
            res = {'role': role,
                   'content': [{'type':'text', 'text':text}]
                   }
        else:
            res = {'role': role,
                   'content': [{'text': text}]
                   }
        # need to finish this for images and PDF documents
        if image:
            # read in file
            image_di = {'type':'image',
                        'source': {"type": "base64",
                                   "media_type": "image/????",
                                   "data": "?????"}}
            res['content'].append(image_di)
        if assistant:
            rm = []
            if type_input:
                ass_di = {'role':'assistant', 
                          'content': [{'type':'text','text': assistant}]}
            else:
                ass_di = {'role':'assistant', 
                          'content': [{'text': assistant}]}
            rm = [res,ass_di]
            return rm
        return res
    def build_native(self,messages,system=None,stop_sequences=None):
        """
        Build native request format for Anthropic Claude model.
        
        Args:
            messages (list): List of message objects to include in the request
            system (str, optional): System prompt to use. Defaults to None.
            stop_sequences (list, optional): Custom stop sequences. Defaults to None.
            
        Returns:
            str: JSON string of the complete request body
        """
        native_request = {'anthropic_version': self.version,
                          'max_tokens': self.max_tokens,
                          'top_k': self.top_k,
                          'stop_sequences': self.stop_sequences,
                          'temperature': self.temperature,
                          'top_p': self.top_p,
                          'messages': messages}
        if system is None:
            if self.system:
                native_request['system'] = self.system
        else:
            native_request['system'] = system
        if stop_sequences:
            native_request['stop_sequences'] = stop_sequences
        return json.dumps(native_request)
    def invoke(self,text,image=None,assistant=None,system=None,stop_sequences=None):
        """
        Invoke the model with a single message.
        
        Args:
            text (str): Text content to send to the model
            image (str, optional): Image data to include. Defaults to None.
            assistant (str, optional): Assistant's response to include. Defaults to None.
            system (str, optional): System prompt to use. Defaults to None.
            stop_sequences (list, optional): Custom stop sequences. Defaults to None.
            
        Returns:
            str: Model's response text
        """
        begin = datetime.utcnow()
        jsonR = self.build_native([self.build_content(text,image,type_input=True)],
                                  system=system,
                                  stop_sequences=stop_sequences)
        response = self.client.invoke_model(modelId=self.model_id,body=jsonR)
        model_response = json.loads(response["body"].read())
        response_text = model_response['content'][0]['text']
        input_tokens = model_response['usage']['input_tokens']
        output_tokens = model_response['usage']['output_tokens']
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.invoke_history.append([text,input_tokens,output_tokens,response_text,begin,datetime.utcnow()])
        return response_text
    def static_fix_json(self,text):
        """
        Apply static fixes to malformed JSON text.
        
        Args:
            text (str): Potentially malformed JSON string
            
        Returns:
            str: Fixed JSON string with proper brackets
        """
        tu = text
        # search for "{", sometimes it has filler text
        lb = tu.find("{")
        rb = tu.rfind("}")
        if lb == -1:
            tu = "{" + tu
        elif lb >= 0:
            tu = tu[lb:]
        if rb == -1:
            tu = tu + "}"
        elif rb >= 0:
            rb2 = tu.rfind("}") # redo, as it may have changed
            tu = tu[:rb2]
        # may need another step to remove left/right brackets inside of string
        return tu
    def valid_json(self,text,attempts=1,sleep=5):
        """
        Validate and fix JSON using the model if necessary.
        
        Args:
            text (str): JSON string to validate
            attempts (int, optional): Number of attempts to fix the JSON. Defaults to 1.
            sleep (int, optional): Seconds to sleep between attempts. Defaults to 5.
            
        Returns:
            dict: Parsed JSON object if successful, or error information if all attempts fail
        """
        tu = self.static_fix_json(text)
        # bare try at first
        try:
            return json.loads(tu)
        except Exception:
            er = traceback.format_exc()
        er_find = er.find("JSONDecodeError")
        er_sub = er[er_find:]
        sys_text = f"The following json is invalid because {er_sub}, please fix it. Only return the json"
        for i in range(attempts):
            time.sleep(sleep)
            tu = self.invoke(tu,system=sys_text,assistant="Here is the correct format {")
            tu = self.static_fix_json(tu)
            try:
                return json.loads(tu)
            except Exception:
                er = traceback.format_exc()
                er_find = er.find("JSONDecodeError")
                er_sub = er[er_find:]
                sys_text = f"The following json is invalid because {er_sub}, please fix it. Only return the json"
        # if it gets here, you only have errors
        res = {'attempts': attempts, 'last_error': er_sub, 'string': tu}
        return res
    def struct_output(self,text,assistant="return {",stop_sequences=["}"],attempts=1):
        """
        Get structured output from the model in JSON format.
        
        Args:
            text (str): Input text to send to the model
            assistant (str, optional): Initial assistant message. Defaults to "return {".
            stop_sequences (list, optional): Sequences to stop generation. Defaults to ["}"]. 
            attempts (int, optional): Number of attempts to fix invalid JSON. Defaults to 1.
            
        Returns:
            dict: Structured output from the model as a Python dictionary
        """
        res = self.invoke(text,assistant=assistant,stop_sequences=stop_sequences)
        rd = self.valid_json(res,attempts=attempts)
        return rd
    def build_context(self,context):
        """
        Build context for retrieval-augmented generation (RAG).
        
        Args:
            context: Context information for RAG
            
        Note:
            This is a placeholder method for RAG implementation.
        """
        # method to build context
        # for RAG
        pass
    def build_chathistory(self,limit_history=5000):
        """
        Build chat history for API request with token limits.
        
        Args:
            limit_history (int, optional): Maximum number of tokens to include. Defaults to 5000.
            
        Returns:
            tuple: (list of message objects for API, total token count used)
        """
        cum_tokens = 0
        ind = len(self.chat_history)
        for r in reversed(self.chat_history):
            cum_tokens += r[1] + r[2]
            if cum_tokens < limit_history:
                ind -= 1
            else:
                break
        res = []
        hist_tokens = 0
        for r in self.chat_history[ind:]:
            hist_tokens += r[1] + r[2]
            diuser = {'role':'user', 'content':[{'text': r[0]}]}
            res.append(diuser)
            # this currently does not append images into the chat history
            diresponse = {'role':'assistant', 'content':[{'text':r[4]}]}
            res.append(diresponse)
        return res, hist_tokens
    def chat(self,text,image=None,limit_history=2000):
        """
        Chat with the model using conversation history.
        
        Args:
            text (str): User input text
            image (str, optional): Image data to include. Defaults to None.
            limit_history (int, optional): Maximum history tokens to include. Defaults to 2000.
            
        Returns:
            str: Model's response text
        """
        begin = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        history, hist_tokens = self.build_chathistory(limit_history=limit_history)
        mess = []
        mess.append(self.build_content(text,image))
        history += mess
        # To get streaming, you use 
        response = self.client.converse(modelId=self.model_id,
                                        messages=history,
                                        inferenceConfig=self.inference_config)
        response_text = response["output"]["message"]["content"][0]["text"]
        input_tokens = response['usage']['inputTokens']
        output_tokens = response['usage']['outputTokens']
        self.input_tokens += input_tokens - hist_tokens
        self.output_tokens += output_tokens
        self.chat_history.append([text,input_tokens,output_tokens,hist_tokens,response_text,begin,datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),image])
        return response_text
    def load_chat(self,name):
        """
        Load chat history from a JSON file.
        
        Args:
            name (str): Name of the chat history to load, or 'No Selection' to clear history
        """
        if name == 'No Selection':
            self.chat_history = []
            self.chat_summary = None
        else:
            with open(f"./chathistory/{name}.json", 'r') as f:
                ch = json.load(f)
            self.chat_history = ch['history']
            self.chat_summary = ch['summary']
    def load_chat_dropdown(self,dropdown):
        """
        Load chat history from a dropdown selection.
        
        Args:
            dropdown (str): Dropdown selection string containing the chat name
        """
        nm = chat_helpers.parse_dropdown(dropdown)
        self.load_chat(nm)
    def save_chat(self,name):
        """
        Save current chat history to a JSON file.
        
        Args:
            name (str): Name to save the chat history as
            
        Returns:
            str: Summary of the chat
        """
        history, tokens = self.build_chathistory(999999999)
        no_summary = self.chat_history.copy()
        if self.chat_summary is None:
            summary = self.chat('create a short 4-7 word summary of the chat history. Do not include any special characters, just the words. Do not include filler like "Here is a 4-7 word summary. Just the summary.')
            self.chat_summary = summary
        else:
            summary = self.chat_summary
        histinfo = {'summary': self.chat_summary,
                    'total_tokens': tokens,
                    'history': no_summary}
        with open(f"./chathistory/{name}.json", "w") as f:
            json.dump(histinfo,f)
        return summary
