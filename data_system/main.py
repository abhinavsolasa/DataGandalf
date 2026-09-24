import shutil, os, sys, getopt

from data_fetching import kaggle
from data_fetching.extractor_interface import MetadataExtractor
#from data_uploading.uploader_interface import MetadataUploader

from data_fetching.kaggle_extractor import KaggleExtractor

#from data_uploading.json_to_db_uploader import JsonToDbUploader

# CONFIGURATION

# Whether to save downloaded CSV files from the datasets. 
SAVE_CSV = False
DATASET_FOLDER = "datasets"

# Whether to save the metadata JSON objects created. Should be true if you want the ability to edit.
SAVE_METADATA = False
METADATA_FOLDER = "metadata"

# The topics to query from. 
TOPICS = ['sports', 'education', 'housing', 'health', 'finance', 'energy', 'politics', 'agriculture', 'chemistry', 'entertainment']

# Number of datasets to fetch per topic.
DATASETS_PER_TOPIC = 2

# Source to query. 
SOURCE = "kaggle"

# Which Stages to Run- "FETCH", "EXTRACT", "UPLOAD"
STAGES = ["FETCH", "EXTRACT"]

# READ CONFIGURATION FROM CLI
if __name__ == '__main__':
    topics_specified = False
    stages_specified = False
    options, arguments = getopt.getopt(sys.argv[1:], "feucmt:n:", ["topic=", "num_datasets="])

    for option, value in options:
        if option == '-c':
            SAVE_CSV = True
        elif option == '-m':
            SAVE_METADATA = True
        elif option == '-f':
            if not stages_specified:
                stages_specified = True
                STAGES = []
            STAGES.append("FETCH")
        elif option == '-e':
            if not stages_specified:
                stages_specified = True
                STAGES = []
            STAGES.append("EXTRACT")
        elif option == '-u':
            if not stages_specified:
                stages_specified = True
                STAGES = []
            STAGES.append("UPLOAD")
        elif option in ('-t', '--topic'):
            if not topics_specified:
                topics_specified = True
                TOPICS = []
            TOPICS.append(value.lower())
        elif option in ('-n', '--num_datasets'):
            DATASETS_PER_TOPIC = int(value)
            if DATASETS_PER_TOPIC <= 0:
                raise ValueError("Number of datasets (-n) must be >= 0.")
        

# Initialize default objects to be overridden. 
extractor = MetadataExtractor(DATASET_FOLDER)
#uploader = MetadataUploader()

# Override extractor and uploader objects. 
if SOURCE == "kaggle":
    if "FETCH" in STAGES:
        kaggle.fetch(topics=TOPICS, num_datasets=DATASETS_PER_TOPIC, output_folder=DATASET_FOLDER)
    extractor = KaggleExtractor(file_input_path=DATASET_FOLDER, file_output_path=METADATA_FOLDER)
    #uploader = JsonToDbUploader(file_input_path=METADATA_FOLDER)

if "EXTRACT" in STAGES:
    # Extract Topics. 
    extractor.extract_topics(TOPICS)

    print("SUCCESSFULLY EXTRACTED TOPICS.")

if "UPLOAD" in STAGES:
    # Upload Topics. 
    #uploader.prepare_upload(topics=TOPICS)
    #uploader.upload()

    print("SUCCESSFULLY UPLOADED METADATA.")

if "EXTRACT" in STAGES:
    extractor.report_issues()

#if "UPLOAD" in STAGES:
    #uploader.report_issues()
    
# Delete Unnecessary data. 
if not SAVE_CSV:
    for topic in TOPICS:
        path = os.path.join(DATASET_FOLDER, topic)
        if os.path.exists(path):
            shutil.rmtree(path)

if not SAVE_METADATA:
    for topic in TOPICS:
        path = os.path.join(METADATA_FOLDER, topic)
        if os.path.exists(path):
            shutil.rmtree(path)