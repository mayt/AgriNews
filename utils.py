import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md, MarkdownConverter

class BlockConverter(MarkdownConverter):

    def convert_p(self, el, text, convert_as_inline):
        if text.strip().startswith('■この記事の'):
            return ''
        return super().convert_p(el, text, convert_as_inline)
    
    def convert_h1(self, el, text, convert_as_inline):
        return '# ' + text.strip() + '\n\n'

    def convert_figure(self, el, text, convert_as_inline):
        if text.strip() == '':
            return ''
        return 'Figure: ' + text.strip()
        

def get_original_text(url):
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, "html.parser")
    title = soup.body.find('h1', attrs={'class': 'uk-article-title'}).text.strip()
    #text = soup.body.find('div', attrs={'class': 'hk-article-body'}).get_text(separator = '\n', strip = True).strip()

    article = soup.body.find('div', attrs={'class': 'hk-article-body'})
    # # remove all images and quotes in article content
    # for element in article.children:
    #     if element.name == 'span' or element.name == 'div':
    #         element.clear()
    # text = article.get_text(separator = '\n', strip = True).strip()
    # text = '\n\n'.join([x.strip() for x in text.split('\n')])
    #title = re.sub(r'(?<=[^\W\d_])\s+(?=[^\W\d_])', '', title)
    #text = f"# {title}\n\n{text}"
    
    text = BlockConverter(strip="img").convert(f"<h1>{title}</h1>{article}")

    print("title\n", title, "\ntext\n", text, "\n\n")
    return text