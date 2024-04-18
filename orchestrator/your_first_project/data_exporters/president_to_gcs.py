from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.google_cloud_storage import GoogleCloudStorage
from pandas import DataFrame
from os import path
import os
import json
import pandas as pd
from math import ceil

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_google_cloud_storage(df: DataFrame, **kwargs) -> None:
    """
    Exports DataFrames to Google Cloud Storage, processing multiple JSON files.
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    bucket_name = 'indoelection2024'
    base_folder = "/home/src/election_data/president_dpr_data" 
    location_subfolder = 'president'
    chunk_size = 100  # Adjust as needed

    file_paths = os.listdir(base_folder)
    num_chunks = ceil(len(file_paths) / chunk_size) 

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = min((i + 1) * chunk_size, len(file_paths))
        chunk_files = file_paths[start_index:end_index]

        dfs = []  

        for file_path in chunk_files:
            if file_path.endswith(".json") and 'dpr' not in file_path:
                full_file_path = os.path.join(base_folder, file_path)
                object_key = os.path.join(location_subfolder, file_path.split(".")[0] + ".csv")

                df = pd.DataFrame(columns=['100025', '100026', '100027', 'desa', 'tps', 'ts'])
                desa = full_file_path.split("/")[-1].split("_")[0]
                tps = full_file_path.split("/")[-1].split("_")[-1].split(".")[0]

                with open(full_file_path, 'r') as f:
                    data = json.load(f)

                try:
                    if data.get('chart'): 
                        chart_data = [{'key': key, 'value': value} for key, value in data['chart'].items() if key != 'null' and value is not None]
                        temp_df = pd.DataFrame(chart_data).set_index('key').T
                        temp_df['desa'] = desa
                        temp_df['tps'] = tps
                        temp_df['ts'] = data['ts']
                        df = pd.concat([df, temp_df], ignore_index=True) 
                    else:
                        df.loc[len(df)] = [0, 0, 0, desa, tps, data['ts']]

                except (KeyError, ValueError) as e: 
                    print(f"Error processing file {file_path}: {e}")


                df = df.reset_index(drop=True)
                dfs.append(df)  

        # Generate a filename for the combined DataFrame 
        filename = f'chunk_{i}.csv'  
        object_key = os.path.join(location_subfolder, filename) 

        combined_df = pd.concat(dfs, ignore_index=True) 

        GoogleCloudStorage.with_config(ConfigFileLoader(config_path, config_profile)).export(
            combined_df,
            bucket_name,
            object_key,
        )
