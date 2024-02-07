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

4. create another file **.env** which will hold the development credentials and add the following variables. Update the azure openai details, OCI object storage details and bhashini endpoint URL and API Key.

    ```bash
    OPENAI_API_VERSION=<AZURE_OPENAI_API_VERSION>
    OPENAI_API_BASE=<AZURE_OPENAI_BASE_URL>
    OPENAI_API_TYPE=azure 
    GPT_MODEL=<AZURE_OPENAI_MODEL_NAME>
    OPENAI_API_KEY=<your_openai_key>
    LOG_LEVEL=<log_level>  # INFO, DEBUG, ERROR
    BHASHINI_ENDPOINT_URL=<your_bhashini_endpoint_url>
    BHASHINI_API_KEY=<your_bhashini_api_key>
    OCI_ENDPOINT_URL=<oracle_bucket_name>
    OCI_REGION_NAME=<oracle_region_name>
    OCI_BUCKET_NAME=<oracle_bucket_name>
    OCI_SECRET_ACCESS_KEY=<oracle_secret_access_key>
    OCI_ACCESS_KEY_ID=<oracle_access_key_id>
    TELEMETRY_ENDPOINT_URL=<TELEMETRY_ENDPOINT_URL> 
    TELEMETRY_LOG_ENABLED=<TELEMETRY_LOG_ENABLED> 
    ```

# 🏃🏻 2. Running

Once the above installation steps are completed, run the following command in home directory of the repository in terminal

```bash
uvicorn main:app
```

# 📃 3. API Specification and Documentation

### `POST /v1/context`

#### API Function
API is used to extract context information of chosen attributes from an user's query. To achieve the same, Few-shot learning has been implemented which requires a set of 'examples' and necessary 'instructions' to be given to LLM (openAI) in order to generate an answer in the instructed format. Configuration of 'instructions' and 'examples' are available in 'config.ini'.

#### Supported language codes in request:
```text
en,bn,gu,hi,kn,ml,mr,or,pa,ta,te
```

#### Request

Required inputs are 'text', 'audio' and 'language'.

Either of the 'text'(string) or 'audio'(string) should be present. If both the values are given, exception is thrown. Another requirement is that the 'language' should be same as the one given in text and audio (i.e, if you pass English as 'language', then your 'text'/'audio' should contain queries in English language). The audio should either contain a publicly downloadable url of mp3 file or base64 encoded text of the mp3.

```json
{
    "text": "ನನ್ನ ಮಗುವಿಗೆ ವಾಟರ್ ಪೇಂಟಿಂಗ್ ಅನ್ನು ಹೇಗೆ ಕಲಿಸುವುದು",
    "language": "kn"
}
```

#### Successful Response

```json
{
    "input": {
        "sourceText": "ನನ್ನ ಮಗುವಿಗೆ ವಾಟರ್ ಪೇಂಟಿಂಗ್ ಅನ್ನು ಹೇಗೆ ಕಲಿಸುವುದು",
        "englishText": "How to Teach My Child Water Painting"
    },
    "context": {
        "category": [
            "Activities"
        ],
        "persona": [
            "Parent"
        ],
        "age": [
            "3-5"
        ],
        "keywords": [
            "water painting"
        ],
        "domain": [
            "Aesthetic and Cultural Development"
        ],
        "curricularGoal": [
            "CG-12: Children develop abilities and sensibilities in visual and performing arts and express their emotions through art in meaningful and joyful ways"
        ]
    }
}
```

---

### `POST /v1/translation`

#### API Function
API is used to achieve translation of text/audio from one language to another language in text/audio format. To achieve the same, Bhashini has been integrated. OCI object storage has been used to store translated audio files when audio is chosen as target output format.

#### Supported language codess in request:
```text
en,bn,gu,hi,kn,ml,mr,or,pa,ta,te
```

#### Request

Required inputs are 'input.text', 'input.audio', 'input.language', 'output.language' and 'output.format'.

Either of the 'text'(string) or 'audio'(string) should be present in the 'input'. If both the values are given, exception is thrown. Another requirement is that the 'input.language' should be same as the one given in text and audio (i.e, if you pass English as 'input.language', then your 'text'/'audio' should contain queries in English language). The audio should either contain a publicly downloadable url of mp3 file or base64 encoded text of the mp3. If 'output.language' is not passed in the request, 'English' will be the default value. 'output.format' can only take 'text'/'audio' as values. If 'output.format' is not passed in the request, 'text' will be the default value.

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
    "translation": {
        "text": "ಮಕ್ಕಳಿಗೆ ಆಟವಾಡಲು ಕಲಿಸುವುದು ಹೇಗೆ?",
        "audio": null
    }
}
```

---

# 🚀 4. Deployment

This repository comes with a Dockerfile. You can use this dockerfile to deploy your version of this application to Cloud Run.
Make the necessary changes to your dockerfile with respect to your new changes. (Note: The given Dockerfile will deploy the base code without any error, provided you added the required environment variables (mentioned in the .env file) to either the Dockerfile or the cloud run revision)


## Feature request and contribution

*   We are currently in the alpha stage and hence need all the inputs, feedbacks and contributions we can.
*   Kindly visit our project board to see what is it that we are prioritizing.


---
 
# UTILITY SERVICE SERVER DEPLOYMENT:
### Making System ready for Docker:
```text
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
### Installing latest Docker: 
```text
$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin	
```
### Installing PIP: 
```text
$ sudo apt install python3-pip
```
### Clone Repo: 
```text
$ git clone https://github.com/DJP-Digital-Jaaduii-Pitara/sakhi-utility-service.git
```
### CD to cloned repo: 
```text
$ cd sakhi-utility-service
```
### Build Docker Image of the repo: 
```text
$ sudo docker build -t sakhiutilityimage .
```
### Create Container: 
```text
$ sudo docker run -d -p 8000:8000 --name sakhi-utility-service \
-e OPENAI_API_VERSION=$AZURE_OPENAI_API_VERSION 
-e OPENAI_API_BASE=$AZURE_OPENAI_BASE_URL
-e OPENAI_API_TYPE=azure 
-e GPT_MODEL=$AZURE_OPENAI_MODEL_NAME
-e OPENAI_API_KEY=$OPENAI_API_KEY \
-e LOG_LEVEL=INFO  \
-e BHASHINI_ENDPOINT_URL=$BHASHINI_ENDPOINT_URL \
-e BHASHINI_API_KEY=$BHASHINI_API_KEY \
-e OCI_ENDPOINT_URL=$OCI_ENDPOINT_URL \
-e OCI_REGION_NAME=$OCI_REGION_NAME \
-e DISABLE_NEST_ASYNCIO=True \
-e OCI_BUCKET_NAME=$OCI_BUCKET_NAME \
-e OCI_SECRET_ACCESS_KEY=$OCI_SECRET_ACCESS_KEY \
-e OCI_ACCESS_KEY_ID=$OCI_ACCESS_KEY_ID \
-e TELEMETRY_ENDPOINT_URL=$TELEMETRY_ENDPOINT_URL \
-e TELEMETRY_LOG_ENABLED=$TELEMETRY_LOG_ENABLED \
sakhiutilityimage
```

---

 
# Configuration (config.ini)

| Variable                        | Description                                                                                    | Default Value                        |
|:--------------------------------|------------------------------------------------------------------------------------------------|--------------------------------------|
| few_shot_config.instructions    | System prompt for GEN AI to perform the context recognition for user's query                   |                                      |
| few_shot_config.examples        | Context examples inserted to System prompt for GEN AI to perform few shot learning             |                                      |
| database.docs_min_score         | Minimum score of the documents based on which filtration happens on retrieved documents        | 0.4                                  |
| lang_code.supported_lang_codes  | Supported languages by the service                                                             | en,bn,gu,hi,kn,ml,mr,or,pa,ta,te     |
| min_words.length | Minimum length of words in user's query for which context extraction get enabled by Gen AI                    | 6                                    |
| llm.gpt_model                   | Gen AI GPT Model value                                                                         |                                      |
| telemetry.telemetry_log_enabled | Flag to enable or disable telemetry events logging to Sunbird Telemetry service                | true                                 |
| telemetry.environment           | service environment from where telemetry is generated from, in telemetry service               | dev                                  |
| telemetry.service_id            | service identifier to be passed to Sunbird telemetry service                                   |                                      |
| telemetry.service_ver           | service version to be passed to Sunbird telemetry service                                      |                                      |
| telemetry.actor_id              | service actor id to be passed to Sunbird telemetry service                                     |                                      |
| telemetry.channel               | channel value to be passed to Sunbird telemetry service                                        |                                      |
| telemetry.pdata_id              | pdata_id value to be passed to Sunbird telemetry service                                       |                                      |
| telemetry.events_threshold      | telemetry events batch size upon which events will be passed to Sunbird telemetry service      | 5                                    |
