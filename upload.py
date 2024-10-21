import os
import glob
import yaml
import requests
import json
import pandas as pd

def upload_audio(config, audio_path):
    # File to upload
    file_path = f'{config["path"]["audio"]}/{audio_path}'

    # Set up the API endpoint and headers
    url = f'{config["label-studio"]["url"]}/api/projects/{config["label-studio"]["project-id"]}/import'

    headers = {
        "Authorization": f'Token {config["label-studio"]["api-token"]}'
    }

    # Upload the file
    with open(file_path, 'rb') as f:
        response = requests.post(url, headers=headers, files={"file": f})

    # Check the response
    if response.status_code == 201:
        print(f"File {audio_path} imported successfully!")
    else:
        print("Failed to import file:", response.status_code, response.text)

def check_update(config):
    LABEL_STUDIO_URL = config["label-studio"]["url"]
    PROJECT_ID = config["label-studio"]["project-id"]
    API_TOKEN = config["label-studio"]["api-token"]
    tasks_url = f"{LABEL_STUDIO_URL}/api/projects/{PROJECT_ID}/tasks/"
    response = requests.get(tasks_url, headers={"Authorization": f"Token {API_TOKEN}"})

    if response.status_code == 200:
        tasks = response.json()
        for task in tasks:
            print(f"Task ID: {task['id']}, Data: {task['data']}")
    else:
        print("Failed to retrieve tasks:", response.status_code, response.text)

if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    PROJECT_ID = config["label-studio"]["project-id"]
    MP3_PATH = config["path"]["audio"]
    MEDIA_DB_DIR = fr'{config["label-studio"]["db-and-media-dir"]}'
    audio_paths = os.listdir(config["path"]["audio"])

    # Load all predictions with speaker diarization, emotion and transcription
    all_preds = pd.read_csv("predictions.csv", encoding="utf-8").set_index("Name")
    all_preds = all_preds.to_dict("index")

    # Load all audio in directory
    for audio in audio_paths:
        # Upload audio
        upload_audio(config, audio_path = audio)

        audio_name = audio.split(".mp3")[0]
        preds = all_preds[audio_name]["result"]

        # Replace single quote to double quote
        preds = preds.replace("'", '"')
        preds = json.loads(preds)

        # Get audio path from LabelStudio database
        audios = glob.glob(f'{MEDIA_DB_DIR}/media/upload/{PROJECT_ID}/*{audio_name}*')
        AUDIO_PATH = audios[0].split("\\")[-1]

        # Headers for authentication
        headers = {
            "Authorization": f'Token {config["label-studio"]["api-token"]}',
            "Content-Type": "application/json"
        }

        # Task data: replace with your actual audio file path and predictions
        task_data = [
            {
                "data": {
                    "audio": f"/data/upload/{PROJECT_ID}/{AUDIO_PATH}"
                },
                "predictions": [
                    {
                        "model_version": "model-predict",  # Optional: model version or any identifier
                        "result": preds
                    }]
            }
        ]

        # API endpoint to create tasks
        url = f'{config["label-studio"]["url"]}/api/projects/{PROJECT_ID}/import'

        # Send POST request to create the task
        response = requests.post(url, headers=headers, json=task_data)

        if response.status_code == 201:
            print("Task created successfully!")
        else:
            print(f"Failed to create task. Status code: {response.status_code}")
            print(f"Response: {response.json()}")


    # Check upload status
    check_update(config)
