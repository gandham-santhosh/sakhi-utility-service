import json

import outlines
import os
import openai
from openai import AzureOpenAI

from config_util import get_config_value

llm_type = get_config_value("llm", "llm_type", None).lower()
gpt_model = get_config_value("llm", "gpt_model", None)
instructions = get_config_value('few_shot_config', 'instructions', None)
examples = json.loads(get_config_value('few_shot_config', 'examples', None))

if llm_type == "azure":
    client = AzureOpenAI(
        azure_endpoint=os.environ["OPENAI_API_BASE"],
        api_key=os.environ["OPENAI_API_KEY"],
        api_version=os.environ["OPENAI_API_VERSION"]
    )
elif llm_type == "openai":
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@outlines.prompt
def few_shots(instructions, examples):
    """{{ instructions }}

    Examples
    --------
       {% for item_group, items in examples.items() %}
            {% if items %}
                {% for item in items %}
                    Q: {{ item.question }}
                    A: {{ item.answer }}
                    {% if not loop.last %}

                    {% endif %}
                {% endfor %}
            {% endif %}
       {% endfor %}
    Question
    --------

    Q: user_question
    A:
    """


prompt = few_shots(instructions, examples)


def invokeLLM(question):
    system_rules = prompt.replace("user_question", question)
    print("system_rules::: ", system_rules)

    res = client.chat.completions.create(
        model=gpt_model,
        temperature=0,
        messages=[
            {"role": "system", "content": system_rules},
            {"role": "user", "content": question}
        ],
    )

    return res.choices[0].message.model_dump()
