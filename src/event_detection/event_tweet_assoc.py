import json
from ast import literal_eval
from glob import glob
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


def get_event_df():
    df_event = pd.read_csv("data/events/event_indexed.csv")
    wiki2data_ids = df_event["wikidata_ids"].tolist()
    wiki2data_ids_ = [literal_eval(x) for x in wiki2data_ids]
    wiki2data_ids_ = [[int(x) for x in y] for y in wiki2data_ids_]
    df_event["wikidata_ids"] = wiki2data_ids_
    # df_event["event_id"] = df_event.index
    print(df_event["wikidata_ids"].tolist()[:10])
    return df_event


def get_tweet_df(file):
    df_tweet = pd.read_csv(file)
    wikidata_ids = df_tweet["wikidata_ids"].tolist()
    wikidata_ids_ = [literal_eval(x) for x in wikidata_ids]
    wikidata_ids_ = [[int(x) for x in y] for y in wikidata_ids_]
    df_tweet["wikidata_ids"] = wikidata_ids_
    print(df_tweet["wikidata_ids"].tolist()[:10])
    return df_tweet


def get_tweet_event_score(tweet2event_dict):
    tweet2event_score = defaultdict(dict)

    for tweet_id, event_score in tweet2event_dict.items():
        event_score_sorted = sorted(event_score.items(), key=lambda item: item[1], reverse=True)
        event_id, score = event_score_sorted[0]
        event_score_dict = {k: v for k, v in event_score.items() if v > 0.3}
        tweet2event_score[tweet_id] = {"event_id": event_id, "score": score, "score_dict": event_score_dict}

    # convert dictionary to dataframe
    tweet2event_df = pd.DataFrame.from_dict(tweet2event_score, orient="index")
    tweet2event_df["id"] = tweet2event_df.index
    return tweet2event_df


def matching_tweets_event(df_event, df_tweets):
    """
    Matching tweets with events
    :param df_event: event dataframe
    :param df_tweets: one tweet dataframe
    :return:
    """
    tweet_date = df_tweets["date"].tolist()[0]
    df_event = df_event[df_event["date"] <= tweet_date]  # tweet should be after event date.
    print(df_event.date.value_counts())
    event2wikidata = dict(zip(df_event["event_id"], df_event["wikidata_ids"]))
    tweet2wikidata = dict(zip(df_tweets["id"], df_tweets["wikidata_ids"]))

    tweet2event_dict = defaultdict(dict)

    for tweet_id, tweet_ents in tweet2wikidata.items():
        for event_id, event_ents in event2wikidata.items():
            event_labels_len = len(event_ents)
            inters = list(set(event_ents).intersection(set(tweet_ents)))
            if len(inters) > 0:
                if event_labels_len > 0:
                    score = len(inters) / event_labels_len
                    if score > 0:
                        if tweet_id not in tweet2event_dict:
                            tweet2event_dict[tweet_id] = dict()
                            tweet2event_dict[tweet_id][event_id] = score
                        else:
                            tweet2event_dict[tweet_id][event_id] = score

    tweet2event_df = get_tweet_event_score(tweet2event_dict)
    print(f"tweet df original {len(df_tweets)}, event detected {len(tweet2event_df)}")

    df_merged = pd.merge(df_tweets, tweet2event_df, on="id")
    print(f"score >0.3: {len(df_merged[df_merged['score'] > 0.3])}")

    df_merged.to_csv(f"data/events/event_detected_tweets/tweets_{tweet_date}.csv", index=False)


def main():
    df_event = get_event_df()
    for file in glob("data/wikidata/tweets_wikidata_*.csv"):
        df_tweet = get_tweet_df(file)
        matching_tweets_event(df_event, df_tweet)


#
# def sample_run():
#     df_event =

if __name__ == '__main__':
    # df_event = get_event_df()
    # df_event.to_csv("data/events/event_indexed.csv", index=False)
    main()
