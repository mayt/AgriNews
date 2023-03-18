import argparse
import os
import openai
from dotenv import load_dotenv
import itertools
import deepl
from utils import get_original_text
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.llms import OpenAIChat

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
deepl_api_key = os.getenv("DEEPL_API_KEY")
deepl_translator = deepl.Translator(deepl_api_key)


def nouns_extraction(text, model="gpt-3.5-turbo"):
    system_message_prompt = """Your job is to pick out all proper nouns, people's names, places' name, brand names, quoted names, and technical jargon in Japanese for your peer translator. You will attempt to translate the words.

For companies, use the romanji name. For example, "明治生命" => "Meiji Life Insurance Co.".

You will respond in the following format:

農水省=Ministry of Agriculture, Forestry and Fisheries (MAFF)
農泊=Nouhaku or Agritourism
鶏がゆ=chicken porridge
"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message_prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=1000,
    )
    return response.choices[0].message.content

def translate_extraction(text, dictionary, model="gpt-3.5-turbo"):
    system_message_prompt = """You are a Japanese to EN-US translator. You translate newspaper articles for the Japanese Agricultural Newspaper. You must keep the paragraphing of the original document but do your best to make the translated article easily readable for EN-US native speakers.

Remove salutations (minister Tanaka => Tanaka, chief Tanaka => Tanaka) for names when only referring to the last name.

Keep title catchy and short. Name and abbreviations should be consistent from the main text. For example, if you use "Ministry of Agriculture, Forestry and Fisheries (MAFF)" in the first paragraph, then use MAFF in the rest of the article. If the abbreviation is not used, then do not include it in the rest of the article.

Write your response in markdown, keeping the same formatting.

For lines that begin with "Figure:" translate those and put them in the same place with the prefix "Figure:".

You will use the following dictionary to help you with the translation.
{dictionary}
"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message_prompt.format(dictionary=dictionary)},
            {"role": "user", "content": text},
        ],
        temperature=0.6,
        max_tokens=1500,
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="url to parse")
    parser.add_argument("-v", "--verbose", help="print verbose", action="store_true")
    parser.add_argument("-m", "--model", help="model to use", default="gpt-3.5-turbo")
    parser.add_argument("-r", "--regenerate-dict", help="regenerate dictionary", action="store_true")

    opt = parser.parse_args()
    orig_text = get_original_text(opt.url)

    if opt.regenerate_dict:
        nouns = nouns_extraction(orig_text, model=opt.model)
        print(nouns)
        with open(f"{opt.url.split('/')[-1]}.txt", "w") as f:
            f.write(nouns)
        print(f"Dictionary generated under {opt.url.split('/')[-1]}.txt")
        input("Press Enter to continue...")

    with open(f"{opt.url.split('/')[-1]}.txt") as f:
        loaded_dict = f.readlines()
    translation = translate_extraction(orig_text, loaded_dict, model=opt.model)
    print("First pass:")

    print(translation)



if __name__ == "__main__":
    main()
