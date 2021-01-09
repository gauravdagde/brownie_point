import logging
# from pygooglenews import GoogleNews
import re
# libraries to be imported
import smtplib
import string
import traceback
from datetime import datetime, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import matplotlib.pyplot as plt
import nltk
import pandas as pd
import plotly.express as px
import requests
import seaborn as sns
from IPython.display import HTML
from bs4 import BeautifulSoup
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from google_play_scraper import Sort, reviews_all
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

from brownie.interview_request.models import InterviewRequest

# from IPython import get_ipython
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('vader_lexicon')

color = sns.color_palette()

# get_ipython().run_line_magic('matplotlib', 'inline')

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


def execute_interview_request():
    ir_object_list = InterviewRequest.objects.filter(is_visited_by_cron=False)
    for ir_object in ir_object_list:
        user_name = ir_object.user.first_name
        company_name = ir_object.company.name
        try:
            post_log("Getting news from google", 'STARTED')
            attachment_file_list = []
            user_tag_list = []
            from pygooglenews import GoogleNews
            gn = GoogleNews()
            s = gn.search(company_name.lower())
            final_data = []
            for news in s['entries']:
                new_dict = {
                    'title': news['title'],
                    'link': news['link'],
                    'published': news['published']
                }
                # print(s['entries'])
                # break
                summary_texts = []
                tags = []
                try:
                    soup = BeautifulSoup(requests.get(news['link'], timeout=300).content, "html.parser")
                    for p in soup.findAll('p'):
                        # print(p.text)
                        dummy_text = p.text
                        tags.extend(get_tag(dummy_text))
                        if "“" in dummy_text:
                            # print(dummy_text)
                            # get_quotes_from_html_text(p.text.replace("“",'"').replace("”",'"'))
                            summary_texts.append(dummy_text)
                            # break
                    if summary_texts:
                        new_dict['summary'] = summary_texts
                        new_dict['tags'] = list(set(tags))
                        user_tag_list.extend(new_dict['tags'])
                        final_data.append(new_dict)
                except Exception as e:
                    print(f"{e} : {news}")
            user_email = ir_object.user.email
            post_log(f"Getting news from google for {user_email}", 'COMPLETED')
            # creating a Dataframe object
            news_df = pd.DataFrame(final_data)
            news_df['Date'] = pd.to_datetime(news_df['published'], errors='coerce')
            news_df.sort_values(by=['Date'], inplace=True, ascending=False)
            del news_df['Date']
            file_name = f'{company_name}_Scrapped News.csv'
            news_df.to_csv(file_name)
            post_log(f"File creation for the scrapped news for {user_email}", 'COMPLETED')
            attachment_file_list.append(file_name)
            google_play_app_id = ir_object.company.google_play_app_id
            if google_play_app_id:
                post_log(f"Srapping reviews for the app for {user_email}", 'STARTED')
                result = reviews_all(
                    google_play_app_id,
                    sleep_milliseconds=0,  # defaults to 0
                    lang='en',  # defaults to 'en'
                    country='us',  # defaults to 'us'
                    sort=Sort.NEWEST  # defaults to Sort.MOST_RELEVANT
                    # filter_score_with=5 # defaults to None(means all score)
                )
                post_log(f"Srapping reviews for the app for {user_email}", 'COMPLETED')

                df = pd.DataFrame(result)
                # df = pd.read_csv('/content/Netflix_all_reviews.csv')
                # print(df.head())
                # Product Scores
                post_log(f"Histogram creation for the app reviews for {user_email}", 'STARTED')
                fig = px.histogram(df, x="score")
                fig.update_traces(marker_color="turquoise", marker_line_color='rgb(8,48,107)',
                                  marker_line_width=1.5)
                fig.update_layout(title_text='Product Score')
                HTML(fig.to_html())
                fig.write_image(f"{company_name}_playstore_ratings.png")
                attachment_file_list.append(f"{company_name}_playstore_ratings.png")
                post_log(f"Histogram creation for the app reviews for {user_email}", 'COMPLETED')
                reviews_df = df
                # reviews_df["review"] = reviews_df["content"].apply(lambda x: x.replace("No Negative", "").replace("No Positive", ""))
                reviews_df["is_bad_review"] = reviews_df["score"].apply(lambda x: 1 if x < 3 else 0)
                # select only relevant columnss
                reviews_df = reviews_df[["content", "reviewCreatedVersion", "at", "is_bad_review"]]
                # reviews_df.head()
                reviews_df["review"] = reviews_df["content"]
                # reviews_df
                post_log(f"Sentiment analysis for {user_email}", 'STARTED')
                # return the wordnet object value corresponding to the POS tag

                # clean text data
                reviews_df["review_clean"] = reviews_df["review"].apply(lambda x: clean_text(x))
                # add sentiment anaylsis columns

                sid = SentimentIntensityAnalyzer()
                reviews_df["sentiments"] = reviews_df["review"].apply(lambda x: sid.polarity_scores(str(x)))
                reviews_df = pd.concat(
                    [reviews_df.drop(['sentiments'], axis=1), reviews_df['sentiments'].apply(pd.Series)], axis=1)
                # add number of characters column
                reviews_df["nb_chars"] = reviews_df["review"].apply(lambda x: len(str(x)))

                # add number of words column
                reviews_df["nb_words"] = reviews_df["review"].apply(lambda x: len(str(x).split(" ")))
                # create doc2vec vector columns

                documents = [TaggedDocument(doc, [i]) for i, doc in
                             enumerate(reviews_df["review_clean"].apply(lambda x: str(x).split(" ")))]

                # train a Doc2Vec model with our text data
                model = Doc2Vec(documents, vector_size=5, window=2, min_count=1, workers=4)

                # transform each document into a vector data
                doc2vec_df = reviews_df["review_clean"].apply(lambda x: model.infer_vector(str(x).split(" "))).apply(
                    pd.Series)
                doc2vec_df.columns = ["doc2vec_vector_" + str(x) for x in doc2vec_df.columns]
                reviews_df = pd.concat([reviews_df, doc2vec_df], axis=1)
                # add tf-idfs columns
                tfidf = TfidfVectorizer(min_df=10)
                tfidf_result = tfidf.fit_transform(reviews_df["review_clean"]).toarray()
                tfidf_df = pd.DataFrame(tfidf_result, columns=tfidf.get_feature_names())
                tfidf_df.columns = ["word_" + str(x) for x in tfidf_df.columns]
                tfidf_df.index = reviews_df.index
                reviews_df = pd.concat([reviews_df, tfidf_df], axis=1)
                # show is_bad_review distribution
                # reviews_df["sentiment"].value_counts(normalize = True)
                post_log(f"Sentiment analysis for {user_name}", 'COMPLETED')

                # print wordcloud
                post_log(f"Creating word cloud for {user_name}", 'STARTED')
                wc_name = show_wordcloud(reviews_df["review"], company_name)
                attachment_file_list.append(wc_name)
                post_log(f"Creating word cloud for {user_name}", 'COMPLETED')
                # highest positive sentiment reviews (with more than 5 words)
                reviews_df[reviews_df["nb_words"] >= 5].sort_values("pos", ascending=False)[["review", "pos"]].head(10)

                # show is_bad_review distribution
                reviews_df["is_bad_review"].value_counts(normalize=True)

                # lowest negative sentiment reviews (with more than 5 words)
                post_log(f"Creating negative reviews csv for {user_name}", 'STARTED')
                negative_df = reviews_df[reviews_df["nb_words"] >= 5].sort_values("neg", ascending=False)[
                    ["content", "neg"]].head(50)
                negative_df.to_csv(f'{company_name}_negative_reviews.csv', columns=["content"])
                attachment_file_list.append(f'{company_name}_negative_reviews.csv')
                post_log(f"Creating negative reviews csv for {user_name}", 'COMPLETED')
            else:
                attachment_file_list.extend(['app_playstore.png', 'app_word_cloud.png'])
            # gbrowniepoint
            post_log(f"Creation of email body for {user_name}", 'STARTED')

            # Set Global Variables
            gmail_user = 'gbrowniepoint@gmail.com'
            gmail_password = 'gagan@123'

            fromaddr = "gbrowniepoint@gmail.com"
            toaddr = "gagan.gehani@gmail.com"

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = fromaddr

            # storing the receivers email address
            msg['To'] = toaddr

            # storing the subject
            msg['Subject'] = f"Interview Brownie : {user_name}'s report"

            # string to store the body of the mail
            body = f'''
            <p>Hi {user_name},</p>
            <div dir="ltr"><br />Here is your report<br /><br /><strong><u>1. PR synthesis</u></strong>&nbsp;<br /><br />
          '''
            # print(f'body before adding tags : {body}')
            # print(user_tag_list)
            for index, tag in enumerate(list(set(user_tag_list))):
                tag_data = get_first_tag_quotes(tag, final_data)
                type_str = tag_dict[tag]['mail_tag_line'].format(alphabet_list[index])
                summary = '<br />'.join(map(str, tag_data["summary"]))
                body = body + f'<u>{type_str}</u><br /><br />Quote:<br />&nbsp;&ldquo;{summary}<br />Source: <a href="{tag_data["link"]}" target="_blank">{tag_data["title"]}</a><br /><br />'

            # print(f'body after adding tags : {body}')

            body = body + f'''
          <p><strong><u><em>How do you use these insights in your interview?<br /></em></u></strong><br />
          Interviewer - Do you have any questions for us?<br />{user_name} - Yes, I read about the launch of ASAP - how do people get assigned to such projects internally?<br /><br />
          From Type A.<br /><br />Another one,<br />{user_name} - I also read about the platform for data collaboration for covid - amazing to see the pace of execution on that one, how is that going?<br /><br />
          From type B<br /><br />{user_name} - There were 40 million raised for the clinical analysis, do we raise money for specific projects / verticals or was this a covid specific development?<br /><br />
          From type C.<br /><br />Now remember, these are just examples and you should be able to come up with genuine talking points, questions, things that you can relate to now with minimal effort of going through the links <br /><br />You can also find a consolidated list of all public mentions of {company_name} in the past year attached.<br /><u></u></p><div dir="ltr">&nbsp;</div>
          '''
            if google_play_app_id:
                body = body + f'''<div dir="ltr"><strong><u>2. End user understanding</u></strong></div>
              <div>This is the split of the playstore ratings, suggest you to bring up this in your talking points in the interview<br /><br /><br />This is a wordcloud of all the negative reviews, the takeaway for you is that<br />
              <br><img src="cid:0"><br>
              <ul>
              <li>A significant chunk of the bad ratings of the app are generic bad reviews, investing in talking to these consumers might uncover issues yet unknown</li>
              <li>1 peculiar thing was the mention of cbse in a cluster of reviews, the CBSE learning experience might have some issues in particular</li>
              </ul>
              &nbsp;</div>
              <div>This is a word cloud from all the positive reviews,<br />
              <br><img src="cid:1"><br>
              <ul>
              <li>The trend of generic reviews continues here as well, 1 suggestion could be to request reviewers to write a few lines describing what they loved about their experience</li>
              </ul>
              <div>Thanks for trying out the beta, please feel free to revert with any questions, suggestions/ feedback etc and it will be super helpful to us if you can share this in your network - a linkedin post talking about your experience will help us reach more people<br /><br />If you don't have anything to ask or say, please revert with your rating on 5 on how useful did you find this tool, it will help us gauge it's efficacy&nbsp;<br /><br />Cheers,</div>
              </div>
              <p>--</p>
              <div dir="ltr" data-smartmail="gmail_signature">
              <div dir="ltr">
              <div>
              <div dir="ltr">
              <div dir="ltr">
              <div dir="ltr">
              <div>Gaurav Dagde and Gagan Gehani</div>
              </div>
              </div>
              </div>
              </div>
              </div>
              </div>'''
            else:
                body = body + f'''
            <div><strong><u>2. End user understanding<br /></u></strong></div>
            <div><br />Playstore reviews - Our system couldn't find {company_name} app on the playstore.
             Nonetheless, I am attaching screenshots of the output of another beta tester to give you a taste of what you can expect from this section</div>
            <br><img src="cid:0"><br>
            <br><img src="cid:1"><br>
            <p>If you don't have anything to ask or say, please revert with your rating on 5 on how useful did you find this tool, it will help us gauge it's efficacy
            <br /><br />All the best for your interview!</p>
            <div>Thanks for trying out the beta, please feel free to revert with any questions, suggestions/ feedback etc and it will be super helpful to us if you can share this in your network - a linkedin post talking about your experience will help us reach more people<br /><br />If you don't have anything to ask or say, please revert with your rating on 5 on how useful did you find this tool, it will help us gauge it's efficacy&nbsp;<br /><br />Cheers,</div>
            </div>
            <p>--</p>
            <div dir="ltr" data-smartmail="gmail_signature">
            <div dir="ltr">
            <div>
            <div dir="ltr">
            <div dir="ltr">
            <div dir="ltr">
            <div>Gaurav Dagde and Gagan Gehani</div>
            </div>
            </div>
            </div>
            </div>
            </div>
            </div
            '''

            # attach the body with the msg instance
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            # file_list = ['ps_image.png',file_name]
            img_count = 0
            for attach_file in attachment_file_list:
                # open the file to be sent
                # filename = file_name
                attachment = open(f'/content/{attach_file}', "rb")
                # to add an attachment is just add a MIMEBase object to read a picture locally.
                post_log(f"filename : {attach_file}", "IN_PROGRESS")
                if '.png' in attach_file:
                    # post_log(f"In PNG block", "IN_PROGRESS")
                    # with open(f'/content/{attach_file}', 'rb') as attachment:
                    # set attachment mime and file name, the image type is png
                    mime = MIMEBase('image', 'png', filename=attach_file)
                    # add required header data:
                    mime.add_header('Content-Disposition', 'attachment', filename=attach_file)
                    mime.add_header('X-Attachment-Id', '{}'.format(img_count))
                    mime.add_header('Content-ID', '<{}>'.format(img_count))
                    # read attachment file content into the MIMEBase object
                    mime.set_payload(attachment.read())
                    # encode with base64
                    encoders.encode_base64(mime)
                    # add MIMEBase object to MIMEMultipart object
                    msg.attach(mime)
                    img_count += 1
                else:
                    # post_log(f"In else block", "IN_PROGRESS")
                    # instance of MIMEBase and named as p
                    p = MIMEBase('application', 'octet-stream')

                    # To change the payload into encoded form
                    p.set_payload(attachment.read())

                    # encode into base64
                    encoders.encode_base64(p)

                    p.add_header('Content-Disposition', "attachment; filename= %s" % attach_file)

                    # attach the instance 'p' to instance 'msg'
                    msg.attach(p)

                    # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            s.starttls()

            # Authentication
            s.login(fromaddr, gmail_password)

            # Converts the Multipart msg into a string
            text = msg.as_string()
            post_log(f"Creation of email body for {user_name}", 'COMPLETED')
            # sending the mail
            s.sendmail(fromaddr, toaddr, text)
            post_log(f"Email sending for the user : {user_name}", 'COMPLETED')
            # terminating the session
            s.quit()
        except Exception as e:
            df.to_csv(f'{company_name}_all_reviews.csv')
            traceback.print_exc()
            post_log(f"{e} : for user : {user_name}", "ERROR")
            continue
