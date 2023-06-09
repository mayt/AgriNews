import argparse
import os
from bs4 import BeautifulSoup
import requests
import openai
from dotenv import load_dotenv
import itertools
import deepl
from utils import get_original_text

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
deepl_api_key = os.getenv("DEEPL_API_KEY")
deepl_translator = deepl.Translator(deepl_api_key)

def translate_prompt_builder(input):
    prompt =  f"""Input text:
東日本大震災と東京電力福島第１原子力発電所事故の発生から、もうすぐ１２年を迎える中、ＪＡ福島さくら復興推進課の職員が、昨年８月に避難指示が解除された福島県双葉町にあるＪＡ関連施設を訪れた。内部は１２年間ほぼ手つかずの状態。大地震、原発事故と立て続けに大災害に見舞われた当時の混乱の形跡が今も鮮明に残る。本紙記者が訪問に同行した。（染谷臨太郎）

福島・双葉町　ＪＡ福島さくら関連施設

「悲しさやむなしさよりも懐かしい気持ち」。２月中旬、旧ＪＡふたば北部営農センターを訪問した同課の田中宏課長は、室内を見回し、そうつぶやいた。２００７年まで、カントリーエレベーターのオペレーターとして、ここで勤務した。震災後に訪れたのは初めてという。

かつて職員が出入りした施設裏手の通用口は、長年使われることがなく、隙間からつる性の植物が侵入。枯れ葉が積もっていた。

組合員が訪れていた事務所には、１１年３月の予定表が今もかかる。震災当日の１１日の翌日に当たる１２日の欄に記された「事業推進大会」は開かれず、以降の予定は空白のままだ。

地震発生時、ＪＡ職員らは震災後すぐに重要書類を運び出した。机には飲みかけの缶コーヒーや給与明細などが今も残り、当時の混乱を今に伝える。

12年前の3月の予定が記されたホワイトボード。12日以降は空白となっている（福島県双葉町で） 12年前の3月の予定が記されたホワイトボード。12日以降は空白となっている（福島県双葉町で）
書類や飲料のペットボトルなどが散乱した事務所の机（福島県双葉町で） 書類や飲料のペットボトルなどが散乱した事務所の机（福島県双葉町で）
組合員の応対に使っていたカウンター代わりのキャビネットには、２１年に解体された双葉カントリーエレベーターの利用申込書が散らばる。


Output text:
FUKUSHIMA, Mar. 7 – Almost twelve years have passed since the massive earthquake and the accident at the Tokyo Electric Power Company’s Fukushima No.1 Nuclear Power Plant hit the eastern part of Japan. In mid-February this year, a reconstruction promotion manager of a local agricultural cooperative in Fukushima Prefecture (JA Fukushima Sakura) visited an ex-JA building in Futaba Town, Fukushima Prefecture, for the first time after the evacuation order was lifted in August last year. Everything inside the building has been left almost untouched for 12 years, and traces of the turmoil are everywhere. A Japan Agricultural News reporter accompanied him on the visit.

“This brings back good memories of the past rather than sadness and emptiness,” said Hiroshi Tanaka inside the former JA Futaba Northern Farming Center. He worked here as a grain elevator operator until 2007. We saw long trailing vines of plants growing in the back door entrance hall, though the door for staff members has been closed for many years. The hall was covered by dry leaves.

What we saw in the office was a whiteboard calendar on the wall with some schedules for March 2011. The last one was a note about an event on March 12, which was never held.

JA staff took out important documents immediately after the quake, leaving unfinished canned coffee, pay stubs, and such on the table behind in a mess.

We also saw papers scattered on the cabinet, which also served as a counter to welcome JA members. They are application forms for users of the Futaba Grain Elevator, which was dismantled in 2021.


Input text:
{input}

Rewrite the input text to proper American English targing the writing style of the New York Times newspaper article but written by the Japan Agricultural newspaper being sure the borrowed romanji words are correct. The paragraph count should match the original.:
Output text:

"""
    #print("prompt\n", prompt, "\n\n")
    return prompt

def merge_prompt_builder(prev_line, original_line, alternatives):
    prompt = f"Target line from original to translate:\n{original_line}\n\n"
    for i in range(len(alternatives)):
        prompt += f"Translated candidates {i+1}:\n{alternatives[i]}\n\n"
    prompt += "Using the translated candidates and the original source, produce a line that would appear in a newspaper while sticking to the contents and meanings of original text.\n\n" \
        + "Final Translated Version:\n"
    #print("prompt\n", prompt, "\n\n")
    return prompt

def clean_prompt_builder(original, dirty_copy):
    prompt = f"""Task: Revise the translated copy, making it print quality for the Japan Agricultural newspaper. Besure to give extra weight to the original as the translated copy may have mistakes. Fix abbreviations. Fix inconsistencies. Only introducing the full names of people, places, and groups once. Verify that translated names are consistent and have the right romanji. The paragraph count should match the original.
Translated copy:
{dirty_copy}


Original:
{original}


Result:
"""
    #print("prompt\n", prompt, "\n\n")
    return prompt




def translate(input_text, iteration=1, total=2):
    total = max(total, 2)
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=translate_prompt_builder(input_text),
            temperature=0.5+(0.2*iteration/(total-1)),
            max_tokens=1000,
        )
    return response.choices[0].text

def merge(prev_line, sentenses_tuple):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=merge_prompt_builder(prev_line, sentenses_tuple[0], sentenses_tuple[1:]),
            temperature=0.3,
            max_tokens=1000,
        )
    return response.choices[0].text

def clean(orig_text, merged_text):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=clean_prompt_builder(orig_text, merged_text),
            temperature=0.2,
            max_tokens=1000,
        )
    return response.choices[0].text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='url to parse')
    parser.add_argument('--revisions', default=5, help='revisions to generate', type=int)
    parser.add_argument('-v', "--verbose", help='print verbose',action="store_true")
    parser.add_argument("--deepl", help='use deepl',action="store_true")


    opt = parser.parse_args()
    orig_text = get_original_text(opt.url)

    deepl_text = ""
    if opt.deepl:
        deepl_text = deepl_translator.translate_text(orig_text, target_lang="EN-US")
        if (opt.verbose):
            print(f"deepl_text\n", deepl_text, "\n\n")
        else:
            print("Deepl translation done")

    versions = []
    for i in range(opt.revisions):
        translated_text = translate(orig_text, iteration=i, total=opt.revisions)
        if (opt.verbose):
            print(f"translated text v{i+1}\n", translated_text, "\n\n")
        else: 
            generated_lines = translated_text.split('\n\n')
            print(f"Translation {i+1}/{opt.revisions} done", f" ({len(generated_lines)} lines generated)")
        versions.append(translated_text.split("\n\n"))

    merged_text = ""
    prev_line = ""
    zip_tuple =  (orig_text.split("\n\n"), deepl_text.text.split('\n\n'), *versions) if opt.deepl else (orig_text.split("\n\n"), *versions)
    for i, sentenses_tuple in enumerate(itertools.zip_longest(*zip_tuple, fillvalue="")):
        merged = merge(prev_line, sentenses_tuple)
        prev_line=merged
        if (opt.verbose):
            print(f"merged text \n", merged, "\n\n")
        else:
            print(f"Merge {i+1}/{len(versions[0])} done")
        merged_text += merged + "\n\n"
    
    cleaned = clean(orig_text, merged_text)
    print("Cleaned translation:\n")
    print(cleaned)




if __name__ == "__main__":
    main()