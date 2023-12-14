import configparser

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from cloud_storage_oci import *
from few_shot_util import *
from io_processing import *
from logger import logger

app = FastAPI()


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"


class ContextRequest(BaseModel):
    text: str = None
    audio: str = None
    source_language: str = None


class TranslationRequest(BaseModel):
    text: str = None
    audio: str = None
    source_language: str = None
    target_language: str = "English"
    target_format: str = "text"


class TranslationResponse(BaseModel):
    trans_text: str = None
    trans_audio: str = None


config = configparser.ConfigParser()
config.read('config.ini')
language_code_map = config['lang_code']


@app.get(
    "/health",
    tags=["Health Check"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    include_in_schema=True
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


@app.post("/context_extractor", tags=["API for fetching query context information"])
async def query_context_extraction(request: ContextRequest):
    load_dotenv()

    text = None
    audio = None
    source_language = None
    answer = None
    load_dotenv()

    logger.info({"text": request.text, "audio": request.audio, "source_language": request.source_language})
    if request.text is not None:
        text = request.text.strip()
    if request.audio is not None:
        audio = request.audio.strip()
    if request.source_language is not None:
        source_language = request.source_language.strip()

    few_shot_config = config['few_shot.config']

    logger.info({"text": text, "audio": audio, "source_language": source_language})
    if text is None and audio is None:
        raise HTTPException(status_code=422, detail="Either 'text' or 'audio' should be present!")
    elif (text is None or text == "") and (audio is None or audio == ""):
        raise HTTPException(status_code=422, detail="Either 'text' or 'audio' should be present!")
    elif text is not None and audio is not None and text != "" and audio != "":
        raise HTTPException(status_code=422, detail="Both 'text' and 'audio' cannot be taken as input! Either 'text' "
                                                    "or 'audio' is allowed.")
    elif source_language is None or source_language == "":
        raise HTTPException(status_code=400, detail="Invalid Request! Please provide Source Language,!")
    else:
        try:
            src_lang_code = language_code_map[source_language.lower()]
            if src_lang_code is None or src_lang_code == "":
                raise HTTPException(status_code=400, detail="Unsupported language!")
        except Exception as ex:
            raise HTTPException(status_code=400, detail="Unsupported language!")

        if text is not None and text != "":
            logger.info({"text": text, "src_lang_code": src_lang_code})
            eng_text, error_message = translate_text_to_english(text, src_lang_code)
        else:
            if not is_url(audio) and not is_base64(audio):
                raise HTTPException(status_code=422, detail="Invalid audio input!")
            logger.info({"src_lang_code:", src_lang_code})
            src_lang_text, eng_text, error_message = transcribe_audio_to_reg_eng_text(audio, src_lang_code)
            logger.info({"src_lang_text:", src_lang_text, "eng_text:", eng_text})

        try:
            instructions = few_shot_config['instructions']
            examples = json.loads(few_shot_config['examples'])
        except Exception as ex:
            print(type(ex))  # the exception type
            print(ex.args)  # arguments stored in .args
            print(ex)
            raise HTTPException(status_code=503, detail="Unable to parse configurations!")

        print("instructions:: ", instructions)
        print("examples:: ", examples)
        print("query:: ", eng_text)
        try:
            response = await invokeLLM(instructions, examples, eng_text)
            print("response:: ", response)
            answer = json.loads(response["answer"].replace("\'", "\""))
            print("answer:: ", answer)
        except Exception as ex:
            print(type(ex))  # the exception type
            print(ex.args)  # arguments stored in .args
            print(ex)
            raise HTTPException(status_code=503, detail="Failed to generate a response!")

    response = {
        "context": answer
    }
    return response


@app.post("/translation", tags=["API for translation of text and audio in English and Indic languages"])
async def translator(request: TranslationRequest) -> TranslationResponse:
    load_dotenv()

    text = None
    audio = None
    source_language = None
    target_language = None
    target_format = None
    trans_text = None
    trans_audio = None

    if request.text is not None:
        text = request.text.strip()
    if request.audio is not None:
        audio = request.audio.strip()
    if request.source_language is not None:
        source_language = request.source_language.strip()
    if request.target_language is not None:
        target_language = request.target_language.strip()
    if request.target_format is not None:
        target_format = request.target_format.strip()

    logger.info(
        {"text": text, "audio": audio, "source_language": source_language, "target_language": target_language,
         "target_format": target_format})
    if text is None and audio is None:
        raise HTTPException(status_code=422, detail="Either 'text' or 'audio' should be present!")
    elif (text is None or text == "") and (audio is None or audio == ""):
        raise HTTPException(status_code=422, detail="Either 'text' or 'audio' should be present!")
    elif text is not None and audio is not None and text != "" and audio != "":
        raise HTTPException(status_code=422, detail="Both 'text' and 'audio' cannot be taken as input! Either 'text' "
                                                    "or 'audio' is allowed.")
    elif source_language is None or source_language == "":
        raise HTTPException(status_code=400, detail="Invalid Request! Please provide valid source Language!")
    elif target_format != "text" and target_format != "audio":
        raise HTTPException(status_code=400, detail="Please provide valid target format: text or audio!")
    elif (source_language == target_language) and (
            (text is not None and text != "" and target_format == "text") or (
            audio is not None and audio != "" and target_format == "audio")):
        raise HTTPException(status_code=400, detail="Invalid Request! Please check Source Language, Target Language,"
                                                    "Input Format and Output Format combination.")
    else:
        try:
            src_lang_code = language_code_map[source_language]
            if src_lang_code is None or src_lang_code == "":
                raise HTTPException(status_code=400, detail="Unsupported source language!")
        except Exception as ex:
            raise HTTPException(status_code=400, detail="Unsupported source language!")

        try:
            tgt_lang_code = language_code_map[target_language.lower()]
            if tgt_lang_code is None or tgt_lang_code == "":
                raise HTTPException(status_code=400, detail="Unsupported target language!")
        except Exception as ex:
            raise HTTPException(status_code=400, detail="Unsupported target language!")

        if target_format == "text" and text is not None and text != "":
            logger.info("TRANSLATE TEXT TO TEXT OF OTHER LANGUAGE::: ")
            logger.info({"text": text, "src_lang_code": src_lang_code, "tgt_lang_code": tgt_lang_code})
            trans_text, error_message = translate_text(text, src_lang_code, tgt_lang_code)
        elif target_format == "audio" and text is not None and text != "" and src_lang_code == tgt_lang_code:
            logger.info("TRANSLATE TEXT TO AUDIO OF SAME LANGUAGE::: ")
            logger.info({"text": text, "src_lang_code": src_lang_code})
            trans_audio = convert_to_audio(text, src_lang_code)
        elif target_format == "audio" and text is not None and text != "" and src_lang_code != tgt_lang_code:
            logger.info("TRANSLATE TEXT TO AUDIO OF OTHER LANGUAGE::: ")
            logger.info({"text": text, "src_lang_code": src_lang_code, "tgt_lang_code": tgt_lang_code})
            trans_text, error_message = translate_text(text, src_lang_code, tgt_lang_code)
            trans_audio = convert_to_audio(trans_text, tgt_lang_code)
        elif target_format == "text" and audio is not None and audio != "" and src_lang_code == tgt_lang_code:
            if not is_url(audio) and not is_base64(audio):
                raise HTTPException(status_code=422, detail="Invalid audio input!")
            logger.info("TRANSLATE AUDIO TO TEXT OF SAME LANGUAGE::: ")
            logger.info({"text": text, "src_lang_code": src_lang_code})
            trans_text = audio_input_to_text(audio, src_lang_code)
        elif target_format == "text" and audio is not None and audio != "" and src_lang_code != tgt_lang_code:
            if not is_url(audio) and not is_base64(audio):
                raise HTTPException(status_code=422, detail="Invalid audio input!")
            logger.info("TRANSLATE AUDIO TO TEXT OF OTHER LANGUAGE::: ")
            logger.info({"text": text, "src_lang_code": src_lang_code, "tgt_lang_code": tgt_lang_code})
            trans_text_same_lang = audio_input_to_text(audio, src_lang_code)
            trans_text, error_message = translate_text(trans_text_same_lang, src_lang_code, tgt_lang_code)
        elif target_format == "audio" and audio is not None and audio != "":
            if not is_url(audio) and not is_base64(audio):
                raise HTTPException(status_code=422, detail="Invalid audio input!")
            logger.info("TRANSLATE AUDIO TO AUDIO OF OTHER LANGUAGE::: ")
            src_trans_text = audio_input_to_text(audio, src_lang_code)
            trans_text, error_message = translate_text(src_trans_text, src_lang_code, tgt_lang_code)
            trans_audio = convert_to_audio(trans_text, tgt_lang_code)

    response = TranslationResponse()
    response.trans_text = trans_text
    response.trans_audio = trans_audio
    logger.info(msg=response)
    return response


def is_base64(base64_string):
    try:
        base64.b64decode(base64_string)
        return True
    except (binascii.Error, UnicodeDecodeError):
        # If an error occurs during decoding, the string is not Base64
        return False


def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def convert_to_audio(text, tgt_lang_code):
    output_file, error_message = convert_text_to_audio(text, tgt_lang_code)
    if output_file is not None:
        upload_file_object(output_file.name)
        trans_audio_url, error_message = give_public_url(output_file.name)
        logger.debug("Audio Output URL:: ", trans_audio_url)
        output_file.close()
        os.remove(output_file.name)
        return trans_audio_url
    else:
        raise HTTPException(status_code=503, detail="Failed to generate a response!")
