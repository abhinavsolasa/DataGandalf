import os
class MetadataExtractor:
    """Provides general functionality for extracting metadata from a folder 
    containing topics folders that contain dataset folders (see file_input_path Attribute).
    Requires subclasses to implement
    extract_from_dataset to define how to produce the metadata as well as output_data to define 
    how to save the metadata.
    
    Attributes
    ----------
    file_input_path : str
        the path of the folder containing topic folders (e.g. file_input_path/{topic}/{dataset}). 
    metadata_suffix : str
        The suffix to use when saving metadata files (e.g. {dataset_name}/metadatasuffix). 
    datasets_processed : list
        The list of datasets that have been successfully processed. Used for reporting results.
    problem_files : int
        The list of files causing exceptions for the extractor. Used for reporting results
            
    Methods
    -------
    extract_topics(topics: list) -> None
        Calls self.extract_topic on each topic. 

    extract_topic(topic: str) -> None
        Calls self.extract_from_dataset and self.output_data on each dataset
        folder in the file_input_path/{topic} directory. Outputs metadata with 
        the filename {dataset_name}/{self.metadata_suffix}. 

    extract_from_dataset(dataset_folder:str, topic:str) -> dict
        Empty method to be overridden by subclass. Should define how to convert from a folder
        dataset to a python dictionary. 

    output_data(metadata: dict, target_folder: str, filename: str) -> None
        Empty method to be overridden by subclass. Should define how to read in a python
        dictionary and produce output of desired format (JSON file in case of kaggle extractor).
    
    report_issues() -> None
        Reports any issues encountered using self.problem_files.
    """


    def __init__(self, file_input_path: str):
        """
        Parameters
        ----------
        file_input_path : str
            The folder that contains topic folders that contain dataset folders.
        """
        self.file_input_path:str = file_input_path
        self.metadata_suffix: str = '_metadata.json'
        self.datasets_processed: list = []
        self.problem_files: list = []

    def extract_topics(self, topics: list[str]):
        """
        Calls extract_topic on en each topic. 

        Parameters
        ----------
        topics : list[str]
            Names of topic folders to extract metadata from.
        """
        for topic in topics:
            self.extract_topic(topic)

    def extract_topic(self, topic):
        """
        Calls self.extract_from_dataset and self.output_data on each dataset
        folder in the {self.file_input_path}/{topic} directory. Outputs metadata with 
        the filename {dataset_name}/{self.metadata_suffix}.

        Parameters
        ----------
        topic : str
            The folder ({self.file_input_path}/{topic}) to extract datasets from.
        """

        topic_folder = os.path.join(self.file_input_path, topic)
        for dataset_folder in os.listdir(topic_folder):
            try:
                # Get Path
                dataset_path:str = os.path.join(topic_folder, dataset_folder)

                # Extract Metadata
                metadata:dict = self.extract_from_dataset(dataset_path, topic)

                filename = str("".join(filter(lambda x: x.isalpha(), metadata['title'])) + self.metadata_suffix)
                
                self.output_data(metadata, target_folder=topic, filename=filename)
            except Exception as e:
                self.problem_files.append(str(dataset_folder + ": " + str(e)))
                print("Problem:", e)

    def extract_from_dataset(self, dataset_folder: str, topic: str) -> dict:
        """
        Empty method to be overridden by subclass. Should define how to convert from a folder
        dataset to a python dictionary. 

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
        pass
    
    # Output the data gained from extraction.
    def output_data(self, metadata: dict, target_folder: str, filename: str):
        """
        Empty method to be overridden by subclass. Should define how to read in a python
        dictionary and produce output of desired format (JSON file in case of kaggle extractor).

        Parameters
        ----------
        metadata : dict
            The metadata to output. 

        target_folder : str
            Specifies a folder to output metadata to. 

        filename : str
            Specifies the filename to output metadata to. 
        """
        pass

    # Report any issues.
    def report_issues(self):
        """
        Reports any issues encountered during extraction using self.problem_files.
        """
        pass
