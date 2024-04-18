from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from pandas import DataFrame
from os import path
import pandas as pd
import json
import os
from math import ceil  

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_google_cloud_storage(df: DataFrame, **kwargs) -> None:
    """
    Exports DataFrames to Google Cloud Storage, processing JSON files in chunks.
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    bucket_name = 'indoelection2024'
    base_folder = "/home/src/election_data/location" 
    location_subfolder = 'location'
    chunk_size = 100

    file_paths = os.listdir(base_folder)
    num_chunks = ceil(len(file_paths) / chunk_size)  

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = min((i + 1) * chunk_size, len(file_paths))
        chunk_files = file_paths[start_index:end_index]

        dfs = []  
        for file_path in chunk_files:
            if file_path.endswith(".json"):
                full_file_path = os.path.join(base_folder, file_path)

                with open(full_file_path, 'r') as f:
                    data = json.load(f)

                extracted_df = pd.DataFrame(data).reset_index(drop=True)  # Or your DataFrame creation
                dfs.append(extracted_df)  

        # Generate a filename for the combined DataFrame 
        filename = f'chunk_{i}.csv'  
        object_key = os.path.join(location_subfolder, filename) 

        combined_df = pd.concat(dfs, ignore_index=True) 

        GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile)).export(
            combined_df,
            bucket_name,
            object_key,
            )