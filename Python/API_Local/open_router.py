'''
Example motivated from 
https://gmcirco.github.io/blog/posts/mini-model-data-extraction/workflow.html

comparing API cost vs self hosting
'''

from datetime import datetime
import json
import os
import pandas as pd
from openai import OpenAI
from string import Template
from enum import Enum
from pydantic import BaseModel, Field, ValidationError

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Define some extraction schema
class CityAgency(str, Enum):
    DHS = "Department of Homeless Services"
    DOB = "Department of Buildings"
    DSNY = "Department of Sanitation"
    DEP = "Department of Environmental Protection"
    NYPD = "New York City Police Department"
    HPD = "Department of Housing Preservation and Development"
    DPR = "Department of Parks and Recreation"
    DOT = "Department of Transportation"
    DCWP = "Department of Consumer and Worker Protection"

class AgencyExtraction(BaseModel):
    """Schema for extracting city agency mentions from text."""
    complaint: str = Field(
        description="5 word or less description of the complaint"
    )
    agency: CityAgency = Field(
        description="Agency most responsible for the complaint"
    )

ROLE = ("You route New York City resident complaints to the most relevant agency."
        "Select only from the provided list of agencies")

BASE_PROMPT_STR = """
Closely follow these instructions for routing resident complaints:
1. Review the resident complaint and identify the core issue
2. Based on determination of the core issue, assign the complaint to the most relevant city agency
3. Return your output as a JSON output strictly following the schema below:

${extraction_schema}

TEXT TO PROCESS:
${complaint}
"""

# Create the template object
prompt_template = Template(BASE_PROMPT_STR)

# Schema can just dump once
schema_str = json.dumps(AgencyExtraction.model_json_schema(), indent=2)


# Load in the data, 
complaints_df = pd.read_csv("Public_feedback_on_311_request_complaint_types_20260310.csv").head(20) 
complaint_list = complaints_df["Customer Message"].dropna().astype(str).tolist()


def invoke(user_complaint,client=client,ROLE=ROLE,schema_str=schema_str):
    beg = datetime.now()
    prompt = prompt_template.substitute(
        extraction_schema=schema_str,
        complaint=user_complaint
    )
    try:
        response = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': ROLE},
                {'role': 'user', 'content': prompt}
            ],
            model="qwen/qwen3.5-9b",
            temperature=0,
            extra_body={"reasoning": {"enabled": False}},
            response_format={"type": "json_object"}
        )
        raw_content = response.choices[0].message.content
        ext_json = json.loads(raw_content)
        ext_json['completion_tokens'] = response.usage.completion_tokens
        ext_json['prompt_tokens'] = response.usage.prompt_tokens
        ext_json['cost'] = response.usage.cost_details['upstream_inference_cost']
        end = datetime.now()
        ext_json['time'] = (end - beg).total_seconds()
        return ext_json
    except (ValidationError, Exception) as e:
        print(f"Error during LLM invocation or validation: {e}")
        return None

res = []

for c in complaint_list:
    r = invoke(c)
    res.append(r)

res_df = pd.DataFrame(res)
res_df.describe()
res_df.to_csv('results.csv',index=False)
