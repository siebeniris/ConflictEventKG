import json
import os
from typing import Any, List, Tuple
import string

import pandas as pd
import unicodedata
from src.preprocessor.defines import *

# tt = TweetTokenizer()

SPECIAL_CHARS = ['&nbsp;', '&lt;', '&gt;', '&amp;', '&quot;', '&apos;', '&cent;', '&pound;', '&yen;', '&euro;',
                 '&copy;', '&reg;']


# https://gist.github.com/slowkow/7a7f61f495e3dbb7e3d767f97bd7304b

def get_entities_positions(entities: Any, entity_name: str) -> List[Tuple]:
    """
    Get the positions of the entities
    :param entities: including hashtags, mentions, urls
    :param entity_name: either hashtags, mentions, or urls
    :return: positions of the entities , a list of Tuples.
    """
    positions = []
    if str(entities) != 'nan':
        if entity_name in entities:
            for x in entities[entity_name]:
                positions.append((x['start'], x['end']))
    return positions


def entities_in_text(text, entities, entity_name=""):
    """
    Get the hashtags, urls, or mentions
    :param text:
    :param entities:
    :param entity_name:
    :return:
    """
    positions = get_entities_positions(entities, entity_name)
    return [text[pos[0]:pos[1]] for pos in positions]


def preprocessing_one_tweet(tweet, crawled=True, tp=False, lid=False):
    """
    Preprocessing one tweet
    :param tweet: it is text if crawled is False.
    :param lang: language.
    :param crawled:
    :param tp: if for topic modeling, extra: remove stopwords, remove numbers, remove punctuations.
    :param lid: language identification
    :param remove_emoticons:
    :param unidecoded:
    :return:
    """
    # for ID, pure text without removing anything
    if crawled:
        text = tweet['text']
    else:
        text = tweet
    # print(text)

    # remove urls, mentions, or hashtags from crawled tweets.
    if crawled:
        # if it is crawled tweets, "entities" information is crawled.
        if "entities" in tweet:
            entities = tweet['entities']
            # print(entities)
            hashtags = None
            user_mentions = None
            urls = None
            if "hashtags" in entities:
                hashtags = entities_in_text(text, entities, "hashtags")
            if "mentions" in entities:
                user_mentions = entities_in_text(text, entities, "mentions")
            if "urls" in entities:
                urls = entities_in_text(text, entities, "urls")

            # if hashtags is not None:
            #     for hashtag in hashtags:
            #         if lid:
            #             # language identification, hashtags can be transferable between languages.
            #             text = text.replace(hashtag, "")
            #     text = text.replace("#", '')
            #
            # if user_mentions is not None:
            #     for x in user_mentions:
            #         text = text.replace(x, "")

            if urls is not None:
                for url in urls:
                    text = text.replace(url, "")
    else:
        # remove urls
        text = Patterns.URL_PATTERN.sub(r'', text)
        # remove user mentions
        text = Patterns.MENTION_PATTERN.sub(r'', text)
        if lid:
            # remove hashtags:
            text = Patterns.HASHTAG_PATTERN.sub(r'', text)
        # remove "#"
        text = text.replace("#", '')

    # remove special chars, starting with &.
    for CHAR in SPECIAL_CHARS:
        text = text.replace(CHAR, '')
    # remove reserved words
    text = Patterns.RESERVED_WORDS_PATTERN.sub(r'', text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

    if tp or lid:
        # remove emojis
        text = Patterns.EMOJIS_PATTERN.sub(r'', text)
        # remove smileys
        text = Patterns.SMILEYS_PATTERN.sub(r'', text)
        # remove accented characters

    # special for topic modeling:
    if tp:
        # remove numbers
        text = Patterns.NUMBERS_PATTERN.sub(r'', text)
        # remove punctuations
        text = text.translate(str.maketrans('', '', string.punctuation))

        # lower-cased, tokenized and lemmatized
        # text = text_lemmatizer(text.lower(), langdata=langdata)
        # # remove stopwords
        # inter = set(text).intersection(stopwords)
        # for i in inter:
        #     text.remove(i)

        if len(text) > 1:
            return ' '.join(text)

    else:
        # tokenized = tt.tokenize(text)
        # if len(tokenized) > 2:
        #     # remove unnecessary characters.
        #     return ' '.join(text.split())
        # else:
        text = " ".join(text.split())
        return text


def preprocessing_files_by_lang(idx, output_dir, crawled, tp, lid):
    """
    if lang_code is "und", will use langid mode to preprocess tweets
    :param idx: index code
    :param output_dir:
    :return:
    """
    df = pd.DataFrame()
    count = 0
    preprocessed_texts = []
    dates = []
    ids = []
    test_file = f'data/output/preprocessed/restructured/{idx}.json'

    with open(test_file) as f:
        data = json.load(f)["conflict"]['data']
        # for tweet_id, tweet in dict(itertools.islice(data.items(), example_nr)).items():
    for tweet_id, tweet in data.items():
        # preprocessed_text_for_langid = preprocessing_one_tweet(tweet, True)
        # preprocessed_text_cl = preprocessing_one_tweet(tweet, crawled=crawled, tp=False, lid=False)
        preprocessed_text = preprocessing_one_tweet(tweet, crawled=crawled, tp=False, lid=False)
        if preprocessed_text is not None:

            dates.append(tweet['created_at'])
            preprocessed_texts.append(preprocessed_text)
            ids.append(tweet_id)
            print('*' * 40)
        count += 1
    df['id'] = ids
    df['created_at'] = dates
    # df['text'] = original_texts
    df['preprocessed_text'] = preprocessed_texts
    df.to_csv(os.path.join(output_dir, f'{idx}.csv'), index=False)
    print(count)
    print(len(preprocessed_texts))


if __name__ == '__main__':
    lang_code = "en"
    example_nr = 10
    output_dir = "data/output/preprocessed/final"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    tp = False  # for topic modeling
    crawled = True  # for crawled tweets
    lid = False  # for language identification

    # lemmatizer
    # if tp:
    #     langdata = simplemma.load_data(lang_code)
    #     stopwords = stopwordsiso.stopwords(lang_code)
    for idx in [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16]:
        preprocessing_files_by_lang(idx, output_dir=output_dir, crawled=crawled, tp=tp, lid=lid)
