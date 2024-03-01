import pandas as pd
import numpy as np
import re # Regex Library
from difflib import SequenceMatcher # Sequence Scoring
import os,sys


class Deduplication:

    data = pd.DataFrame()
    processed_data = pd.DataFrame()

    """
    Initialize Deduplication class that automatically normalize data and find duplicates.
    """
    def __init__(self, path):
        self.data = pd.read_csv(path)
        self.processed_data = self.normalize(self.data)
        self.level1dup(self.processed_data)
        self.level2dup(self.processed_data)
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
    Find the first level of duplication. This is where the duplication is extremely obviously (90% similarity).
    Args:
        test_data (pd.DataFrame): the data to find duplication
    Returns:
        None
    """
    def level1dup(self,test_data : pd.DataFrame) -> None:
        new_data = pd.DataFrame(columns=self.data.columns.to_list())
        new_data.insert(0, "DUPLICATE_ID",value=None, allow_duplicates=True) # Add new duplicate id for grouping
        dup_index = 0
        for index, row in test_data.iterrows():
            increment = False
            for index2, row2 in test_data.iloc[index+1:].iterrows():
                scores=[]
                scores.append(SequenceMatcher(None, row["FIRSTNAME"],row2["FIRSTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["LASTNAME"],row2["LASTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["EMAIL"], row2["EMAIL"]).ratio())
                scores.append(SequenceMatcher(None, str(row["OTHERSTREET"]),str(row2["OTHERSTREET"])).ratio())
                if str(row["PHONE"]) != "0000000000" and str(row2["PHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["PHONE"]),str(row2["PHONE"])).ratio())
                if str(row["OTHERPHONE"]) != "0000000000" and str(row2["OTHERPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["OTHERPHONE"]),str(row2["OTHERPHONE"])).ratio())
                if str(row["MOBILEPHONE"]) != "0000000000" and str(row2["MOBILEPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["MOBILEPHONE"]),str(row2["MOBILEPHONE"])).ratio())
                if (self.harmonic_mean(scores) >= 0.9):
                    new_data = pd.concat([new_data,row.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    new_data = pd.concat([new_data,row2.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    test_data = test_data.drop(index=index2)
                    increment = True
            if increment:
                dup_index += 1
                increment = False
        new_data.to_csv("duplicates/level1duplicate.csv", index=False)

    """
    Find the second level of duplication. This is where the duplication is somewhat visible (75% similarity).
    Args:
        test_data (pd.DataFrame): the data to find duplication
    Returns:
        None
    """
    def level2dup(self,test_data : pd.DataFrame) -> None:
        new_data = pd.DataFrame(columns=self.data.columns.to_list())
        new_data.insert(0, "DUPLICATE_ID",value=None, allow_duplicates=True) # Add new duplicate id for grouping
        dup_index = 0
        for index, row in test_data.iterrows():
            increment = False
            for index2, row2 in test_data.iloc[index+1:].iterrows():
                scores=[]
                scores.append(SequenceMatcher(None, row["FIRSTNAME"],row2["FIRSTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["LASTNAME"],row2["LASTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["EMAIL"], row2["EMAIL"]).ratio())
                scores.append(SequenceMatcher(None, str(row["OTHERSTREET"]),str(row2["OTHERSTREET"])).ratio())
                if str(row["PHONE"]) != "0000000000" and str(row2["PHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["PHONE"]),str(row2["PHONE"])).ratio())
                if str(row["OTHERPHONE"]) != "0000000000" and str(row2["OTHERPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["OTHERPHONE"]),str(row2["OTHERPHONE"])).ratio())
                if str(row["MOBILEPHONE"]) != "0000000000" and str(row2["MOBILEPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["MOBILEPHONE"]),str(row2["MOBILEPHONE"])).ratio())
                if (self.harmonic_mean(scores) >= 0.75):
                    new_data = pd.concat([new_data,row.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    new_data = pd.concat([new_data,row2.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    test_data = test_data.drop(index=index2)
                    increment = True
            if increment:
                dup_index += 1
                increment = False
        new_data.to_csv("duplicates/level2duplicate.csv", index=False)

    """
    Find the third level of duplication. This is where the duplication is 50/50 (50% similarity).
    Args:
        test_data (pd.DataFrame): the data to find duplication
    Returns:
        None
    """
    def level2dup(self,test_data : pd.DataFrame) -> None:
        new_data = pd.DataFrame(columns=self.data.columns.to_list())
        new_data.insert(0, "DUPLICATE_ID",value=None, allow_duplicates=True) # Add new duplicate id for grouping
        dup_index = 0
        for index, row in test_data.iterrows():
            increment = False
            for index2, row2 in test_data.iloc[index+1:].iterrows():
                scores=[]
                scores.append(SequenceMatcher(None, row["FIRSTNAME"],row2["FIRSTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["LASTNAME"],row2["LASTNAME"]).ratio())
                scores.append(SequenceMatcher(None, row["EMAIL"], row2["EMAIL"]).ratio())
                scores.append(SequenceMatcher(None, str(row["OTHERSTREET"]),str(row2["OTHERSTREET"])).ratio())
                if str(row["PHONE"]) != "0000000000" and str(row2["PHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["PHONE"]),str(row2["PHONE"])).ratio())
                if str(row["OTHERPHONE"]) != "0000000000" and str(row2["OTHERPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["OTHERPHONE"]),str(row2["OTHERPHONE"])).ratio())
                if str(row["MOBILEPHONE"]) != "0000000000" and str(row2["MOBILEPHONE"]) != "0000000000":
                    scores.append(SequenceMatcher(None, str(row["MOBILEPHONE"]),str(row2["MOBILEPHONE"])).ratio())
                if (self.harmonic_mean(scores) >= 0.5):
                    new_data = pd.concat([new_data,row.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    new_data = pd.concat([new_data,row2.to_frame().T], ignore_index=True)
                    new_data.loc[new_data.shape[0]-1,"DUPLICATE_ID"] = dup_index
                    test_data = test_data.drop(index=index2)
                    increment = True
            if increment:
                dup_index += 1
                increment = False
        new_data.to_csv("duplicates/level3duplicate.csv", index=False)

if __name__ == "__main__":
    try: 
        dedupl = Deduplication(os.getcwd() + "/" + sys.argv[1])
    except IndexError:
        raise Exception("Missing path to file. Try \"python3 script.py <path/to/file>\"")

