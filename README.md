# sakhi-context-service


[Jugalbandi API](https://api.jugalbandi.ai/docs) is a system of APIs that allows users to build Q&A style applications on their private and public datasets. The system creates Open API 3.0 specification endpoints using FastAPI.


# 🔧 1. Installation

To use the code, you need to follow these steps:

1. Clone the repository from GitHub: 
    
    ```bash
    git clone https://github.com/DJP-Digital-Jaaduii-Pitara/sakhi-utility-service.git
    ```

2. The code requires **Python 3.7 or higher** and some additional python packages. To install these packages, run the following command in your terminal:

    ```bash
    pip install requirements.txt
    ```

3. You will need a OCI account to store the audio file for response.

4. create another file **.env** which will hold the development credentials and add the following variables. Update the openai_api_key, OCI object storage details and bhashini endpoint URL and API Key.

    ```bash
    OPENAI_API_KEY=<your_openai_key>
    LOG_LEVEL=<log_level>  # INFO, DEBUG, ERROR
    BHASHINI_ENDPOINT_URL=<your_bhashini_endpoint_url>
    BHASHINI_API_KEY=<your_bhashini_api_key>
    OCI_ENDPOINT_URL=<oracle_bucket_name>
    OCI_REGION_NAME=<oracle_region_name>
    OCI_BUCKET_NAME=<oracle_bucket_name>
    OCI_SECRET_ACCESS_KEY=<oracle_secret_access_key>
    OCI_ACCESS_KEY_ID=<oracle_access_key_id>
    ```

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in home directory of the repository in terminal

```bash
uvicorn main:app
```

# 📃 3. API Specification and Documentation

### `POST /context_extractor`

#### API Function
API is used to extract context information of chosen attributes from an user's query. To achieve the same, Few-shot learning has been implemented which requires a set of 'examples' and necessary 'instructions' to be given to LLM (openAI) in order to generate an answer in the instructed format. Configuration of 'instructions' and 'examples' are available in 'config.ini'.

#### Supported language codes in request:
```text
en,bn,gu,hi,kn,ml,mr,or,pa,ta,te
```

#### Request

Required inputs are 'text', 'audio' and 'source_language'.

Either of the 'text'(string) or 'audio'(string) should be present. If both the values are given, exception is thrown. Another requirement is that the 'source_language' should be same as the one given in text and audio (i.e, if you pass English as 'source_language', then your 'text'/'audio' should contain queries in English language). The audio should either contain a publicly downloadable url of mp3 file or base64 encoded text of the mp3.

```json
{
    "text": "How to Teach Kids to Play Games",
    "source_language": "en"
}
```

#### Successful Response

```json
{
    "context": {
        "persona": [
            "Parent",
            "Teacher"
        ],
        "age": [
            "3-8"
        ],
        "format": [
            "video",
            "document",
            "audio"
        ]
    }
}
```

---

### `POST /translation`

#### API Function
API is used to achieve translation of text/audio from one language to another language in text/audio format. To achieve the same, Bhashini has been integrated. OCI object storage has been used to store translated audio files when audio is chosen as target output format.

#### Supported language codess in request:
```text
en,bn,gu,hi,kn,ml,mr,or,pa,ta,te
```

#### Request

Required inputs are 'text', 'audio', 'source_language', 'target_language' and 'target_format'.

Either of the 'text'(string) or 'audio'(string) should be present. If both the values are given, exception is thrown. Another requirement is that the 'source_language' should be same as the one given in text and audio (i.e, if you pass English as 'source_language', then your 'text'/'audio' should contain queries in English language). The audio should either contain a publicly downloadable url of mp3 file or base64 encoded text of the mp3. If 'target_language' is not passed in the request, 'English' will be chosen. If 'target_format' is not passed in the request, 'text' will be chosen.

```json
{
    "input": {
        "text": "How to Teach Kids to Play Games",
        "language": "en"
    },
    "output": {
        "language": "kn",
        "format": "text"
    }
}
```

#### Successful Response

```json
{
    "translated_text": "ಮಕ್ಕಳಿಗೆ ಆಟವಾಡಲು ಕಲಿಸುವುದು ಹೇಗೆ?",
    "translated_audio": null
}
```

---

# 🚀 4. Deployment

This repository comes with a Dockerfile. You can use this dockerfile to deploy your version of this application to Cloud Run.
Make the necessary changes to your dockerfile with respect to your new changes. (Note: The given Dockerfile will deploy the base code without any error, provided you added the required environment variables (mentioned in the .env file) to either the Dockerfile or the cloud run revision)


## Feature request and contribution

*   We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
*   Kindly visit our project board to see what is it that we are prioritizing.

 
