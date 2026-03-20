## Using LLMs to Extract Data from Text

While many vendors say they use AI in vague ways, most real use cases I am famiar with tend to be quite boring. I wrote previously about applications of [natural language processing](/blogposts/2023/NLP), which under the hood often use the same models as those that power ChatGPT or Claude. Another example is extracting information from plain text inputs. This is often called *structured outputs*. 

Here I will show an example using python + Anthropic's models (called using AWS Bedrock, so it is CJIS compliant), to extract information out of police narratives. This can be useful for crime analysts or researchers, if you have historical data and want to categorize different elements out of those narratives that were not captured at the time of the report. I have posted the full set of [code on github](https://github.com/apwheele/Blog_Code/tree/master/Python/StructuredOutputs). Below though is a simple example from police narratives publicly available from Dallas PD. 

Imagine you want to look at burglaries, and characterize the method of entry and the location when the burglar entered. You can give the large language model some instructions and prior examples, and then it will respond with the data in the format you requested:

    from src import bedrock # custom functions to call bedrock models
    
    # System prompt
    system = '''I will give you a description of a burglary please return json that determines the method of entry, and the location of the entry
    for example:
    
    The offender pushed in the AC unit on the west side of the house.
    return {"moe":"window", "loc": "side"}
    
    The offender entered via the unlocked front door.
    return {"moe":"unforced", "loc": "front"}
    
    The burglary narrative is'''
    
    # My class for using AWS bedrock
    sonnet = bedrock.ClaudeModel(system=system)
    
    # Example new burglary narrative
    narr = "The offender broke in a window on the back door to enter the residence."
    
    data = sonnet.struct_output(narr)
    print(data)
    # returns {'moe': 'window', 'loc': 'back'}

This is called zero-shot prompting. It is not a specialized model that extracts out information from burglary narratives, but a generalized LLM (here Sonnet 4). You can replace the instructions with whatever information you want to extract, and give a few examples.

The github code has a more complicated example later on, generating a larger system prompt from 10 examples, and extracting out more information:

    # Slightly more complicated example, categorizing more crimes and more elements
    narr_data = pd.read_csv('Narr.zip')
    examples = pd.read_csv('SampleSet.csv') # 10 cases I labeled
    
    el = []
    for i,s,r,o in examples.itertuples():
        t = f"<offense_narrative>{o}</offense_narrative>"
        t += f"<output>{r}</output>"
        el.append(t)
    
    shot = "\n".join(el)
    
    prompt = f"""
    {shot}
    
    You will be analyzing an offense narrative and classifying various elements within it. Your task is to identify and categorize specific pieces of information from the narrative based on a provided list of elements.
    
    crime, weapon, modus-operandi, vehicle-type, items
    
    The narratives may contain other events that are not crimes, like traffic collisions or evidence collection. All narratives should have a crime type listed, but may not have the other types. Burglary and motor vehicle theft will sometimes have modus operandi. Shootings will sometimes have a type of gun listed, e.g. handgun or rifle. Larceny, theft from mv, and burglary will sometimes have specific items listed as stolen. Place those in a list.
    
    Return the output in json format, only return the json, do not return any further description
    
    <offense_narrative>
    """
    
    haiku = bedrock.ClaudeModel(system=prompt,model=bedrock.models['Claude 3.5 Haiku'])
    
    # looping over 10 cases
    for i,num,off_narr,off_date in narr_data.head(10).itertuples():
        print("")
        print(f'Row {i}')
        print(off_narr)
        data = haiku.invoke(off_narr,assistant="</offense_narrative><output>")
        print("")
        print(data)

Here are the results for those 10 narratives and the outcomes. You can see that in this sample it does quite well.

    Row 0
    ON LISTED DATE AND TIME, THE COMPLAINANT WAS DISCOVERED DECEASED INSIDE HIS RESIDENCE. IT APPEARED THE COMPLAINANT WAS SHOT MULTIPLE TIMES. THERE WAS EVIDENCE TO SUGGEST ROBBERY WAS THE MOTIVE BECAUSE THE RESIDENCE WAS UNLOCKED AND THERE WAS AN UNDETERMINED AMOUNT OF US CURRENCY FOUND JUST OUTSIDE THE COMPLAINANT'S FRONT DOOR.
    
    {"crime": "murder","weapon": "gun","modus-operandi": "robbery"}
    
    Row 1
    THE COMP STATED THAT ON THE LISTED DATE AND TIME, UNK SUSP(S) TOOK THE  LISTED VEH WITHOUT THE KEYS AND WITHOUT PERMISSION. THE VEH WAS PARKED  ON THE STREET, IN FRONT OF COMP'S RESIDENCE. TOW/REPO WAS NEGATIVE. THE COMP IS THE OWNER, HAS TITLE, BUT THE VEH IS STILL UNDER THE ORIGINAL OWNER'S NAME. COMP FILLED OUT AN AUTO THEFT STOLEN VEH AFFIDAVIT. NFI. END OF ELEMENTS
    
    {"crime": "mv theft"}
    
    Row 2
    THE COMP. STATED THAT HE LAST SAW HIS MOTORCYCLE IN FRONT OF HIS APARTMENT AROUND 8PM LAST NIGHT. THE COMP. CAME OUT TO WHERE THE CYCLE  WAS AND DISCOVERED THAT AN UNK. SUSPECT TOOK HIS MOTORCYCLE WITHOUT PERMISSION.  END OF ELEMENTS
    
    {"crime": "mv theft","vehicle-type": "motorcycle"}
    
    Row 3
    KNOWN SUSP TOOK THE COMP'S VEHICLE AND REFUSES TO RETURN THE VEHICLE AT THIS TIME. END OF ELEMENTS
    
    {"crime": "mv theft"}
    
    Row 4
    SUSPECT SHOT AT COMPLAINANT WITH A 9MM HANDGUN. END OF ELEMENTS
    
    {"crime": "shooting","weapon": "9mm handgun"}
    
    Row 5
    ON LISTED DATE AND TIMES UNKNOWN SUSPECT TOOK COMP VEH WIHOUT PERMISSIONEND OF ELEMENTS
    
    {"crime": "mv theft"}
    
    Row 6
    THE COMP TOLD RO THAT HE PARKED HIS MOTORCYCLE AT AN APT COMPLEX AROUND THE 9500 BLOCK OF GARLAND RD AROUND THE LISTED DATE AND TIME. THE COMP  DISCOVERED IT MISSING ON THE LISTED DATE AND APPROX TIME. NO SUSP OR WIT INFO WAS AVAILABLE. THE COMP COMPLETED A STOLEN VEHICLE AFFIDAVIT. END OF ELEMENTS
    
    {"crime": "mv theft","vehicle-type": "motorcycle"}
    
    Row 7
    RP WHO IS THE OWNER STATED THAT AT ABOUT 7:12 AM ON LISTED DATE UNK. SUSPECTS ENTER THROUGH THE BACK DOOR OF THE BUSINESS. SUSPS WENT STRAIGHT TO THE OFFICE AND PRIED THE OFFICE DOOR OPEN. SUSPECTS THEN    REMOVED THE SAFE AND DRAGGED IT OUT THE SIDE DOOR. SUSPECTS ALSO TOOK COMPL'S LAPTOP. PES WAS REQUESTED.NFI.END OF ELEMENTS
    
    {"crime": "burglary","modus-operandi": "pried door open",items": ["safe", "laptop"]}
    
    Row 8
    ON LISTED DATE/TIME/LOCATION R/OS WERE DISPATCHED TO A REQUEST FOR      POLICE ABOUT AN UNKNOWN DECEASED FEMALE. HOMICIDE, ME, PES AND SGT. TREJO #4534 WERE NOTIFIED. NFI END OF ELEMENTS
    
    {"crime": "homicide"}
    
    Row 9
    SUSP TOOK COMP'S VEH W/O CONSENT. END OF ELEMENTS
    
    {"crime": "mv theft"}

While this is an example for police narratives, there are many different potential applications; monitoring web-forums for mentions of specific illicit activity, taking transcripts from body worn cameras and extracting out specific elements of the interaction, identifying key elements in long PDF documents, qualitatively coding different narratives.

If extracting out information from complicated textual inputs using LLMs is something you would like help with, get in touch.