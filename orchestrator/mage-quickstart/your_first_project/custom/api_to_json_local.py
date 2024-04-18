import json
import requests
import os
import logging
import hashlib
import argparse

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

BASE_URL = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/"
PRESIDENT_ENDPOINT = "ppwp"
DPR_ENDPOINT = "pdpr"
PRESIDENT_BASE_URL = "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw"

def process_and_save_json(data, url, tingkat):
    """
    Extracts the code from the URL, creates a filename, and saves the JSON
    """
    url_parts = url.split('/')
    code = url_parts[-1].split('.')[0]  
    filename = f"{code}_tingkat_{tingkat}.json"

    output_dir = "/home/src/election_data/location"
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)
    if os.path.exists(file_path):  
        logging.info(f"File exists: {file_path}. Skipping...")
    else:
        with open(file_path, 'w') as f:  
            json.dump(data, f)

def fetch_and_process(start_url, tingkat=1, codes=[], resume=False):
    logging.info(f"Fetching Level {tingkat}: {start_url}")

    if resume:  
        url_parts = start_url.split('/')
        last_code = url_parts[-1].split('.')[0]
        if last_code not in codes:
            logging.info(f"Skipping processed code: {last_code}")
            return  

    response = requests.get(start_url)

    if response.status_code == 200:
        data = response.json()
        process_and_save_json(data, start_url, tingkat)

        if tingkat < 5:
            for item in data:
                if 'kode' in item:
                    next_code = item['kode']
                    updated_codes = codes + [next_code] 

                    # Construct the next level URL dynamically
                    if tingkat == 1:   
                        next_url = BASE_URL + f"{next_code}.json"
                    else:  
                        next_url = '/'.join(BASE_URL.split('/')[:-1]) + '/' + '/'.join(updated_codes) + '.json'

                    fetch_and_process(next_url, tingkat + 1, updated_codes[:])

        else:  
            # Collect codes for president/DPR fetching
            president_dpr_codes = []
            for item in data:
                if 'kode' in item:
                    president_dpr_codes.append((item['kode'], item.get('last_chain', '025')))

            # Fetch president/DPR data after recursion is complete
            for kode, last_chain in president_dpr_codes:
                president_url = construct_data_url(kode, PRESIDENT_ENDPOINT, last_chain)
                dpr_url = construct_data_url(kode, DPR_ENDPOINT, last_chain)
                
                fetch_and_save_data(president_url, "president")
                fetch_and_save_data(dpr_url, "dpr")

        save_resume_data(start_url, tingkat, codes) 
    else: 
        logging.error(f"Error fetching data for URL: {start_url}") 
        logging.error(f"Response Status Code: {response.status_code}") 
        logging.error(response.text[:100]) 

def construct_data_url(kode, endpoint, last_chain):
    url_parts = []
    if endpoint in [PRESIDENT_ENDPOINT, DPR_ENDPOINT]: 
        url_parts.extend([PRESIDENT_BASE_URL, endpoint])

        # Dynamically construct the path components
        lengths = [2, 4, 6, 10]  # Specify the desired lengths
        for length in lengths:
            url_parts.append(kode[:length]) 
        url_parts.append(kode + ".json")
    else:
        url_parts.extend(BASE_URL.split('/')[:-1])  
    
    print(f"Constructed URL: {'/'.join(url_parts)}")  # Keep the print statement
    return '/'.join(url_parts)  

def fetch_and_save_data(url, data_type):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        checksum = calculate_checksum(data)

        if 'checksum' in data:
            if data['checksum'] != checksum:  
                logging.info(f"Checksum differs for {data_type} data at {url}. Replacing...")
                return save_data(data, url, data_type)  # Return the filepath 

        else:
            logging.info(f"No checksum found for {data_type} data from {url}. Skipping...") 
            return save_data(data, url, data_type)
        
        return None
    else:
        logging.error(f"Error fetching {data_type} data from {url}. Status Code: {response.status_code}")
        return None

def save_data(data, url, data_type):
    # Extract information to build the filename
    url_parts = url.split('/')
    kode = url_parts[-2]
    last_chain = url_parts[-1].split('.')[0].split(kode)[1]  # Extract last_chain

    filename = f"{kode}_{data_type}_{last_chain}.json"
    output_dir = "/home/src/election_data/president_dpr_data"  # Example output directory
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, 'w') as f:
            json.dump(data, f)
        logging.info(f"Saved {data_type} data to: {filepath}")
        return filepath
    except (IOError, OSError) as e:
        logging.error(f"Error saving {data_type} data: {e}")
        return None

def calculate_checksum(data):
    json_string = json.dumps(data, sort_keys=True).encode()  
    return hashlib.sha256(json_string).hexdigest() 

def load_resume_data():
    if os.path.exists("/home/src/election_data/resume_data.json"):
        with open("/home/src/election_data/resume_data.json", "r") as f:
            return json.load(f)
    else:
        return None  

def save_resume_data(url, tingkat, codes):
    data = {
        "resume_url": url,
        "resume_tingkat": tingkat,
        "resume_codes": codes
    }
    with open("/home/src/election_data/resume_data.json", "w") as f:
        json.dump(data, f) 


@custom
def transform_custom(*args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here

    # Argument Parsing
    parser = argparse.ArgumentParser(description="Process data and support resuming")
    parser.add_argument("--fresh", action="store_true", help="Start the process from the beginning, ignoring any resume data")
    args = parser.parse_args(kwargs.get('__cliargs') or []) 

    # Resume Logic
    resume_data = load_resume_data()
    if resume_data and not args.fresh:
        logging.info("Resume data found. Resuming process...")
        RESUME_URL = resume_data["resume_url"]
        RESUME_TINGKAT = resume_data["resume_tingkat"]
        RESUME_CODES = resume_data["resume_codes"]
        resume = True
    else:
        logging.info("No resume data found or --fresh flag provided. Starting from the beginning...")
        # Your default starting values
        RESUME_URL = 'https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json'
        RESUME_TINGKAT = 1
        RESUME_CODES = []
        resume = False

    # Core Processing Logic
    # ... (Your logic to fetch, process data. Call process_and_save_json as needed) ... 

    
    # Core Processing Logic
    file_paths = []  # To store the saved file paths

    # Fetch initial JSON
    initial_file_path = fetch_and_process(RESUME_URL, RESUME_TINGKAT, RESUME_CODES, resume)
    if initial_file_path:
        file_paths.append(initial_file_path)

    print(file_paths)   # Return the collected file paths

@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
