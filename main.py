import argparse
import os
from bs4 import BeautifulSoup
import requests
import openai
from dotenv import load_dotenv
import itertools

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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

Rewrite the input text to proper American English. The target writing style is for an argriculture newspaper article. The paragraph count should match the original.:
Output text:

"""
    #print("prompt\n", prompt, "\n\n")
    return prompt

def merge_prompt_builder(original, alternatives):
    prompt = f"Original:\n{original}\n\n"
    for i in range(len(alternatives)):
        prompt += f"Version {i+1}:\n{alternatives[i]}\n\n"
    prompt += "Take the drafts and write the merged version. The writing should look like a sentence from an argriculture newspaper article." \
            + "\nFinal Version:\n"
    #print("prompt\n", prompt, "\n\n")
    return prompt

def clean_prompt_builder(original, dirty_copy):
    prompt = f"""Original:
{original}

Translated:
{dirty_copy}


Fix any writing inconsistencies for the above translated an argriculture newspaper article. Be sure to consistently use abbreviations correctly and to only expand it once. Numbers should remain consistent. The paragraph count should match the original.
Fixed Version:
"""
    #print("prompt\n", prompt, "\n\n")
    return prompt


def get_original_text(url):
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, "html.parser")
    title = soup.body.find('h1', attrs={'class': 'uk-article-title'}).text.strip()
    #text = soup.body.find('div', attrs={'class': 'hk-article-body'}).get_text(separator = '\n', strip = True).strip()

    article = soup.body.find('div', attrs={'class': 'hk-article-body'})
    # remove all images and quotes in article content
    for element in article.children:
        if element.name == 'span' or element.name == 'div':
            element.clear()
    text = article.get_text(separator = '\n', strip = True).strip()
    text = '\n\n'.join([x.strip() for x in text.split('\n')])
    #title = re.sub(r'(?<=[^\W\d_])\s+(?=[^\W\d_])', '', title)
    #text = f"# {title}\n\n{text}"
    print("title\n", title, "\ntext\n", text, "\n\n")
    return text

def translate(input_text):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=translate_prompt_builder(input_text),
            temperature=0.5,
            max_tokens=1000,
        )
    return response.choices[0].text

def merge(sentenses_tuple):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=merge_prompt_builder(sentenses_tuple[0], sentenses_tuple[1:]),
            temperature=0.2,
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


    opt = parser.parse_args()
    orig_text = get_original_text(opt.url)
    
    versions = []
    for i in range(opt.revisions):
        translated_text = translate(orig_text)
        if (opt.verbose):
            print(f"translated text v{i+1}\n", translated_text, "\n\n")
        else: 
            generated_lines = translated_text.split('\n\n')
            print(f"Translation {i+1}/{opt.revisions} done", f" ({len(generated_lines)} lines generated)")
        versions.append(translated_text.split("\n\n"))

    merged_text = ""
    for i, sentenses_tuple in enumerate(itertools.zip_longest(orig_text.split("\n\n"), *versions, fillvalue="")):
        merged = merge(sentenses_tuple)
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