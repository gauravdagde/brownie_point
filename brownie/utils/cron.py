import logging
import re
import string
from datetime import datetime, timezone

import matplotlib.pyplot as plt
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud

from brownie.interview_request.models import InterviewRequest
from brownie.utils.tasks import execute_interview_request

LOGGER = logging.getLogger('apps.runs.tasks')

alphabet_list = ['A', 'B', 'C', 'D', 'E', 'F']

tag_dict = {
    'funding': {
        'keywords': ['funding', 'investor', 'valuation', 'term sheet', 'venture capital', 'venture debt'],
        'mail_tag_line': 'Type {}: Funding'
    },
    'acquisition': {
        'keywords': ['acquisition', 'acquired'],
        'mail_tag_line': 'Type {}: Acquisition'
    },
    'collabaration': {
        'keywords': ['collabarate', 'collabaration'],
        'mail_tag_line': 'Type {}: Collabaration'
    },
    'social good': {
        'keywords': ['donate'],
        'mail_tag_line': 'Type {}: Strategic initiative'
    },
    'covid': {
        'keywords': ['covid'],
        'mail_tag_line': 'Type {}: Covid'
    },
}


def post_log(message, event='SUCCESS'):
    LOGGER.info(f"[{event}] | {str(datetime.now(timezone.utc))} || {message}")


# wordcloud function
def show_wordcloud(data, company_name, title=None):
    wordcloud = WordCloud(
        background_color='white',
        max_words=200,
        max_font_size=40,
        scale=3,
        random_state=42
    ).generate(str(data))

    fig = plt.figure(1, figsize=(20, 20))
    plt.axis('off')
    if title:
        fig.suptitle(title, fontsize=20)
        fig.subplots_adjust(top=2.3)

    plt.imshow(wordcloud)
    # plt.show()
    plt.savefig(f'{company_name}_wc_positive.png')
    return f'{company_name}_wc_positive.png'


def get_wordnet_pos(pos_tag):
    if pos_tag.startswith('J'):
        return wordnet.ADJ
    elif pos_tag.startswith('V'):
        return wordnet.VERB
    elif pos_tag.startswith('N'):
        return wordnet.NOUN
    elif pos_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def clean_text(text):
    # lower text
    if not text:
        text = ''
    elif not isinstance(text, str):
        return (text)
    text = text.lower()
    # tokenize text and remove puncutation
    text = [word.strip(string.punctuation) for word in text.split(" ")]
    # remove words that contain numbers
    text = [word for word in text if not any(c.isdigit() for c in word)]
    # remove stop words
    stop = stopwords.words('english')
    text = [x for x in text if x not in stop]
    # remove empty tokens
    text = [t for t in text if len(t) > 0]
    # pos tag text
    pos_tags = pos_tag(text)
    # lemmatize text
    text = [WordNetLemmatizer().lemmatize(t[0], get_wordnet_pos(t[1])) for t in pos_tags]
    # remove words with only one letter
    text = [t for t in text if len(t) > 1]
    # join all
    text = " ".join(text)
    return text


def get_tag(p_text):
    ret_value = []
    for key in tag_dict:
        for text in tag_dict[key]['keywords']:
            if text in p_text:
                ret_value.append(key)
    return ret_value


def get_first_tag_quotes(tag, final_data):
    for data in final_data:
        if tag in data['tags']:
            return data


def get_quotes_from_html_text(string_with_quotes):
    Find_double_quotes = re.compile('"([^"]*)"',
                                    re.DOTALL | re.MULTILINE | re.IGNORECASE)  # Ignore case not needed here, but can be useful.
    list_of_quotes = Find_double_quotes.findall(string_with_quotes)
    return list_of_quotes


def schedule_execute_interview_request():
    ir_object_list = InterviewRequest.objects.filter(is_visited_by_cron=False)
    for ir_object in ir_object_list:
        execute_interview_request(ir_object)
