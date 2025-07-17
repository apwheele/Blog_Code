# Structured Outputs

This is an example of applying structured outputs -- getting information out of plain text narratives using LLMs -- applied to extracting information out of police narratives. For a few examples, the output are in the brackets, and the input is the text following the pipe.

    {'crime': 'larceny'} | SUSP TOOK COMP'S PROPERTY WITHOUT CONSENT. END OF ELEMENTS.
    
    {'crime': 'burglary'} | INV OF BURGLARY. END OF ELEMENTS
    
    {'crime': 'shooting', 'weapon': 'gun'} | SEE RELATED RPT #101608B. ON LISTED DATE AND TIME, SUSP SHOT AT COMP'S  DIRECTION INTENDING TO ASSAULT HIM. END OF ELEMENTS.
    
    {'crime': 'theft from mv', 'modusoperandi': 'pried open window', 'vehicle-type': 'Silverado', 'items': ['laptop','ipad']} | BETWEEN THE HOURS OF 5:00PM AND 7:00PM AT THE OFFENSE LOCATION 3501     SAMUELL BLVD, TENSION PARK GOLF COURSE. THE COMP AND THE CC LEFT THEIR  BELONGS, 2 LAPTOP AND IPAD 4, IN TWO SEPARATE LAPTOP BAGS IN THE REAR   SEAT OF THE COMP'S VEHICLE A 2007 CHEVY SILVERADO. UNK SUSP PRIED OPEN  THE COMP'S REAR DRIVERSIDE WINDOW, MADE ENTRY, AND TOOK THE COMP'S AND  CC'S LISTED PROPERTY WITHOUT CONSENT. SUSP FLED IN UNK DIRECTION BY UNK MEANS.NF END OF ELEMENT
    
    {'crime': 'burglary', 'modusoperandi': 'Pushed Air Conditioner'} | ON LISTED DATE AND TIMES SUSP REMOVED THE AC FROM THE FRONT WINDOW OF   THE LISTED LOCATION. SUSP THEN ENTERED AND TOOK THE LISTED PROPERTY FROMINSIDE THE LISTED LOCATION WITHOUT THE OWNERS CONSENT. SUSP FLED IN THE SUSP VEHICLE AND STUCK HIS MIDDLE FINGER UP AT THE WITNESS AS HE FLED.  SUSP WAS WEARING A GRAY HOODED SWEATSHIRT. PES WAS ORDERED TO THE SCENE.COMP WAS AT WORK WHEN THE OFFENSE HAPPENED.NFI. END OF ELEMENTS

This repo shows how to prompt an LLM (Anthropic's Haiku, called using AWS Bedrock, but you can use any model).

To recreate the environment, I set up my AWS CLI account, and then turned on access to the different Anthropic models.

## Data Prep

Example data comes from [Dallas PD Open Data on narratives](https://www.dallasopendata.com/Archive/Bulk-Police-Narrative/inke-qqax/about_data). 

I prepped that data via the following:

    import pandas as pd
    
    #narr = pd.read_csv('Bulk_Police_Narrative_20250711.csv')
    #narr = narr[~narr['offensenarrative'].isna()]
    #narr['offensedate'] = narr['offensedate'].str[:10]
    #narr[['offenseservicenumber','offensenarrative','offensedate']].to_csv('Narr.zip',index=False)
    narr = pd.read_csv('Narr.zip')
    
    ns = narr.sample(10)
    ns.to_csv('SampleSet.csv',index=False)

Then for the `ns` dataset of 10 cases, I coded the information in them.