import os, json

import pandas as pd
from data_fetching.extractor_interface import MetadataExtractor


class KaggleExtractor(MetadataExtractor):
    """Provides functionality for extracting metadata from a folder that's
    containing topics folders that contain dataset folders (see file_input_path Attribute) 
    populated using kaggle.py. Extends MetadataExtractor to utilize extract_topics, extract_topic. 
    
    Superclass Attributes
    ---------------------
    file_input_path : str
        the path of the folder containing topic folders (e.g. file_input_path/{topic}/{dataset}). 
    metadata_suffix : str
        The suffix to use when saving metadata files (e.g. {dataset_name}/metadatasuffix). 
    datasets_processed : list
        The list of datasets that have been successfully processed. Used for reporting results.
    problem_files : int
        The list of files causing exceptions for the extractor. Used for reporting results

            
    Superclass Methods
    -------------------
    extract_topics(topics: list) -> None
        Calls self.extract_topic on each topic. 

    extract_topic(topic: str) -> None
        Calls self.extract_from_dataset and self.output_data on each dataset
        folder in the file_input_path/{topic} directory. Outputs metadata with 
        the filename {dataset_name}/{self.metadata_suffix}. 

        
    Class Attributes
    ----------------
    file_output_path : str
        Defines the folder used to output metadata when calling self.output_data.

    source : str
        Defines the source of the data to populate metadata['source']. 

    Class Methods
    -------------
    extract_from_dataset(dataset_folder:str, topic:str) -> dict
        Combines pandas analysis of CSV files in {self.dataset_folder} with values 
        from metadatta in {self.dataset_folder} to produce a final metadata dictionary.

    output_data(metadata: dict, target_folder: str, filename: str) -> None
        Formats and outputs a .JSON file containing metadata from the dictionary.
    
    report_issues() -> None
        Reports any issues encountered using self.problem_files.
    """

    def __init__(self, file_input_path, file_output_path):
        """    
        Parameters
        ----------
        file_input_path : str
            Defines the folder to search for topic folders that contain dataset folders. 

        file_output_path : str
            Defines the folder used to output metadata when calling self.output_data.

        source : str
            Defines the source of the data to populate metadata['source']."""
        self.file_output_path = file_output_path
        self.source = "kaggle"

        super().__init__(file_input_path)

    def extract_topics(self, topics):
        return super().extract_topics(topics)

    def extract_topic(self, topic):
        return super().extract_topic(topic)

    # Extract a single dataset from a folder of CSVs and JSON.
    def extract_from_dataset(self, dataset_folder, topic) -> dict:
        """
        Convert from a folder dataset generated from kaggle.py to a python dictionary.  

        Parameters
        ----------
        dataset_folder : str
            The folder to extract a dataset from.

        topic : str
            The topic of the dataset, used for populating metadata['title']. 


        Return
        ------
        metadata : dict
            A dictionary containing all metadata representing the dataset in dataset_folder. 
        """
        metadata:dict = {}
        for filename in os.listdir(dataset_folder):
            try:
                # If CSV, run pandas analysis
                if filename[len(filename) - 4:] == '.csv':
                    file = os.path.join(dataset_folder, filename)
                    df = pd.read_csv(file, encoding='unicode_escape')
                    metadata = self.update_metadata_from_df(df, metadata)
                
                # If JSON, take relevant metadata
                elif filename == 'dataset-metadata.json':
                    file = open(os.path.join(dataset_folder, filename), 'r')
                    given_metadata = json.load(file)
                    file.close()
                    metadata['source'] = self.source
                    metadata['topic'] = topic
                    metadata['usability'] = given_metadata['usabilityRating']
                    metadata['title'] = given_metadata['title']
                    metadata['description'] = given_metadata['description']
                    metadata['tags'] = given_metadata['keywords']
                    metadata['url'] = given_metadata['url']
                    metadata['licenses'] = given_metadata['licenses']

                # Otherwise, ignore
                else:
                    continue
            except Exception as e:
                print(e)
                self.problem_files.append(str(filename + ": " + str(e)))
        self.datasets_processed.append(metadata['title'])
        return metadata
    
    # Output metadata to a target file.
    def output_data(self, metadata, target_folder, filename):
        """
        Reads in a python dictionary generated from extract_from-dataset 
        and produce output of desired format (JSON file in case of kaggle extractor).

        Parameters
        ----------
        metadata : dict
            The metadata to output. 

        target_folder : str
            Specifies a folder to output metadata to. 

        filename : str
            Specifies the filename to output metadata to. 
        """

        # full_folder_path:str = os.path.join(self.file_output_path, target_folder)

        if not os.path.exists(self.file_output_path):
            os.makedirs(self.file_output_path)
        
        full_path = os.path.join(self.file_output_path, filename)

        meta_json:json = json.dumps(metadata, indent=4, sort_keys=True)
        
        with open(full_path, "w+") as newfile:
            newfile.write(meta_json)

    # Updates metadata dict from a dataframe (one data file).
    def update_metadata_from_df(self, df: pd.DataFrame, metadata: dict) -> dict:
        """
        Updates the metadata dictionary with a dataframe representing a table. 
        Adds column names, null count, row count, num entries. 

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to use to update metadata. 

        metadata : dict
            The metadata to be modified and returned. 

        Return
        ------
        metadata : dict
            The updated metadata.
        """

        # Compute Values
        null_count:int = int(df.isnull().sum().sum()) 
        metadata['null_count'] = null_count + metadata.get('null_count', 0)

        num_entries:int = int(df.size)
        metadata['num_entries'] = num_entries + metadata.get('num_entries', 0)

        row_count:int = int(df.shape[0])
        metadata['row_count'] = row_count + metadata.get('row_count', 0)

        col_count:int = int(df.shape[1])
        metadata['col_count'] = col_count + metadata.get('col_count', 0)

        col_names:list[str] = df.columns.tolist()
        if 'col_names' not in metadata:
            metadata['col_names'] = col_names

        for name in col_names:
            if not name in metadata['col_names']:
                metadata['col_names'].append(name)

        return metadata

    # Reports any issues. 
    def report_issues(self):  
        """
        Reports the number of datasets successfully extracted and how many had problems. 
        Writes to a file with the list of files that caused exceptions.
        """
        # Report issues
        with open("data_fetching/problem-files.txt", "w+") as newfile:
            newfile.write(json.dumps(self.problem_files))
        print("Successfully extracted", len(self.datasets_processed), "datasets.")
        print("Found", len(self.problem_files), "problem files while extracting. Look at data_fetching/problem-files.txt for a list.")
        return len(self.problem_files)


