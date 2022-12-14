import requests
from api_secrets import ASSEMBLY_AI_API_KEY
import time
import logging

logging.basicConfig(filename='data/logs/conversation.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
                    
class speechToText:

    UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
    TRANSCRIPTION_ENDPOINT = "https://api.assemblyai.com/v2/transcript"
    TRANSCRIPTION_JOB_ENDPOINT = "https://api.assemblyai.com/v2/transcript/"

    def __init__(self):
        # Specify API key in header for authentication
        self.headers = {'authorization': ASSEMBLY_AI_API_KEY}
    
    # Read wav file
    def _read_file(self, filename: str, chunk_size=5242880) -> bytes:

        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    # 1. UPLOAD LOCAL AUDIO
    def upload_audio(self, audio_file_path: str) -> dict:

        # Send POST request
        logging.info(f"Upload recorded audio to Assembly AI API")
        response = requests.post(url=speechToText.UPLOAD_ENDPOINT,
                                headers=self.headers,
                                data=self._read_file(filename=audio_file_path))
        # Return response in json format
        json_response = response.json()
        # Get uploaded audio url
        audio_url =json_response["upload_url"]
        logging.info(f"Fetched corresponding audio URL")
        return audio_url

    # 2. SUBMIT UPLOADED AUDIO FILE FOR TRANSCRIPTION
    def submit_for_transcription(self, audio_url: str) -> dict:

        json = {"audio_url": audio_url}
        response = requests.post(url=speechToText.TRANSCRIPTION_ENDPOINT,
                                headers=self.headers,
                                json=json)
        logging.info(f"Submit audio URL to Assembly AI API to initiate transcription job")
        json_response = response.json()
        transcription_job_id = json_response["id"]
        logging.info(f"Fetched transcription job ID")
        return transcription_job_id

    # 3. GET TRANSCRIPTION
    def get_transcription(self, transcription_job_id: str) -> str:
        
        url = speechToText.TRANSCRIPTION_JOB_ENDPOINT+transcription_job_id
        logging.info(f"Poll Assembly AI API to get check transcription job status")
        while True:
            response = requests.get(url=url, headers=self.headers)
            json_response = response.json()
            if json_response["status"] == "queued":
                logging.info("Transcription job is queued...")
                continue
            elif json_response["status"] == "processing":
                logging.info("Transcription job is running...")
                logging.info("Waiting for 2 seconds...")
                print(f"Running transcription job...", end='\r')
                time.sleep(2)
                continue
            else:
                logging.info(f"Transcription job complete")
                return json_response["text"]

def main():
    pass

if __name__ == "__main__":
    main()