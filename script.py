import pandas as pd
import numpy as np
import re # Regex Library
from difflib import SequenceMatcher # Sequence Scoring

data = pd.read_csv("data/test.csv")
modified_data = data.copy()
modified_data["FIRSTNAME"] = modified_data["FIRSTNAME"].str.lower().str.strip() # Normalize names
modified_data["MOBILEPHONE"] = modified_data["MOBILEPHONE"].apply(lambda x : "".join(re.findall(r'\d+',x))) # Remove non-numerical characters 
modified_data["MOBILEPHONE"] = modified_data["MOBILEPHONE"].fillna("0000000000") # Fill NaN with 0's
modified_data["PHONE"] = modified_data["PHONE"].fillna("0000000000") # Fill NaN with 0's
modified_data["PHONE"] = modified_data["PHONE"].apply(lambda x : "".join(re.findall(r'\d+',x))) # Remove non-numerical characters
modified_data["MIDDLENAME"] = modified_data["MIDDLENAME"].fillna(" ")
"""
for a, b in zip(modified_data["FIRSTNAME"], modified_data["FIRSTNAME"]):
    print(a)
    print(b)
    print(f"Score: {SequenceMatcher(None, a,b).ratio()}")
"""

"""
Implementing Harmonic Mean to Calculate the Average of Sequence Matcher ratio score
"""
def harmonic_mean(variables):
    n = len(variables)
    return n / sum(1 / (x if x != 0 else 0.000001) for x in variables ) # thresholding to avoid division by zero

"""
Find the first level of duplication. This is where the duplication is extremely obviously.
Args:
    test_data (DataFrame): the data to find duplication
Returns:
    None
"""
def level1dup(test_data) -> None:
    new_data = pd.DataFrame(columns=data.columns.to_list())
    for index, row in test_data.iterrows():
        for index2, row2 in test_data.iloc[index+1:].iterrows():
            score_fname = SequenceMatcher(None, row["FIRSTNAME"],row2["FIRSTNAME"]).ratio()
            score_lname = SequenceMatcher(None, row["LASTNAME"],row2["LASTNAME"]).ratio()
            if (harmonic_mean([score_lname,score_fname]) >= 0.7):
                new_data = pd.concat([new_data,row.to_frame().T], ignore_index=True)
                new_data = pd.concat([new_data,row2.to_frame().T], ignore_index=True)
                test_data = test_data.drop(index=index2)
    print(test_data)
    print(new_data)
level1dup(modified_data)
