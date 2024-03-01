import pandas as pd
import numpy as np
import re # Regex Library
from difflib import SequenceMatcher # Sequence Scoring


class Deduplication:
    data = pd.DataFrame()
    processed_data = pd.DataFrame()

    def __init__(self):
        self.data = pd.read_csv("data/test.csv")
        self.processed_data = self.normalize(self.data)
        self.level1dup(self.processed_data)
    """
    Clean and apply data normalization.
    Params:
        data (pd.DataFrame): the data to be processed
    Returns:
        (pd.DataFrame) the new processed data
    """
    def normalize(self,data: pd.DataFrame) -> pd.DataFrame:
        data = self.data.copy()
        data["FIRSTNAME"] = data["FIRSTNAME"].str.lower().str.strip() # Normalize names
        data["MOBILEPHONE"] = data["MOBILEPHONE"].apply(lambda x : "".join(re.findall(r'\d+',x))) # Remove non-numerical characters 
        data["MOBILEPHONE"] = data["MOBILEPHONE"].fillna("0000000000") # Fill NaN with 0's
        data["PHONE"] = data["PHONE"].fillna("0000000000") # Fill NaN with 0's
        data["PHONE"] = data["PHONE"].apply(lambda x : "".join(re.findall(r'\d+',x))) # Remove non-numerical characters
        data["MIDDLENAME"] = data["MIDDLENAME"].fillna(" ")
        return data

    """
    Implementing harmonic mean to calculate the average of the Sequence Matcher ratio score.
    Params:
        variables (list[int]): the scores of Sequence Matcher
    Returns:
        (int) The harmonic mean of the list
    """
    def harmonic_mean(self,variables : list[int]) -> int:
        n = len(variables)
        return n / sum(1 / (x if x != 0 else 0.000001) for x in variables ) # thresholding to avoid division by zero

    """
    Find the first level of duplication. This is where the duplication is extremely obviously.
    Args:
        test_data (pd.DataFrame): the data to find duplication
    Returns:
        None
    """
    def level1dup(self,test_data : pd.DataFrame) -> None:
        new_data = pd.DataFrame(columns=self.data.columns.to_list())
        for index, row in test_data.iterrows():
            for index2, row2 in test_data.iloc[index+1:].iterrows():
                score_fname = SequenceMatcher(None, row["FIRSTNAME"],row2["FIRSTNAME"]).ratio()
                score_lname = SequenceMatcher(None, row["LASTNAME"],row2["LASTNAME"]).ratio()
                if (self.harmonic_mean([score_lname,score_fname]) >= 0.8):
                    new_data = pd.concat([new_data,row.to_frame().T], ignore_index=True)
                    new_data = pd.concat([new_data,row2.to_frame().T], ignore_index=True)
                    test_data = test_data.drop(index=index2)
        print(test_data)
        print(new_data)

dedupl = Deduplication()