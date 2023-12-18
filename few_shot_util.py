import outlines
import os

from guidance import models, gen
from guidance import user, system, assistant


@outlines.prompt
def few_shots(instructions, examples, question):
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

    Q: {{ question }}
    A:
    """

gpt = models.OpenAI("gpt-3.5-turbo", api_key=os.environ["OPENAI_API_KEY"])
gpt.max_calls = 50

async def invokeLLM(instructions, examples, question):
    prompt = few_shots(instructions, examples, question)
    print("PROMPT::: ", prompt)

    with system():
        lm = gpt + prompt

    with user():
        lm += question

    with assistant():
        lm += gen("answer", stop=".")

    return lm