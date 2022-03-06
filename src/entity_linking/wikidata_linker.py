from collections import defaultdict
import pandas as pd
import json

import spacy

# initialize language model
nlp = spacy.load("en_core_web_md")

# add pipeline (declared through entry_points in setup.py)
# nlp.add_pipe("sentencizer")
nlp.add_pipe("entityLinker", last=True)

# entities_dict = defaultdict(dict)


def entity_linking_text(text, entities_dict):
    """
    Input one text.
    :param text:
    :param entities_dict: dictionary of linked entities.
    :return:
    """

    doc = nlp(text)
    linked_entities = doc._.linkedEntities
    ids = []
    labels = []
    for entity in linked_entities:
        descriptions = entity.get_description()
        id = entity.get_id()
        label = entity.get_label()
        wikidata_url = entity.get_url()
        sub_entities = entity.get_sub_entities(limit=10)
        super_entities = entity.get_super_entities(limit=10)
        ids.append(id)
        labels.append(label)

        if id not in entities_dict:
            entities_dict[id] = {
                "description": descriptions,
                "label": label,
                "url": wikidata_url,
                # "sub_entities": sub_entities,
                # "super_entities": super_entities
            }
    return ids, labels


def entity_linking_events():
    df = pd.read_csv("data/events/events_20220224-20220304_sent.csv")
    entities_dict = defaultdict(dict)
    ids_list = []
    labels_list = []
    # sentences =[]
    for event_text in df["first_sentence"].tolist():
        ids, labels = entity_linking_text(event_text, entities_dict)
        # doc = nlp(event_text)
        ids_list.append(ids)
        labels_list.append(labels)

    # sentence = [sent.text.strip() for sent in doc.sents][0]
    # sentences.append(sentence)

    # df["first_sentence"]= sentences
    # df.to_csv("data/events/events_20220224-20220304_sent.csv")
    df["wikidata_ids"] = ids_list
    df["wikidata_labels"] = labels_list

    df.to_csv("data/wikidata/events_wikidata.csv", index=False)

    df_entities = pd.DataFrame.from_dict(entities_dict, orient="index")
    df_entities.to_csv("data/wikidata/entities.csv")


def entity_linking_tweets():
    df = pd.read_csv("data/output/preprocessed/final/all.csv")
    df["date"] = df["created_at"].str[:11]
    df["date"] = pd.to_datetime(df["date"])
    count = 0
    entities_dict = defaultdict(dict)
    for key, group_df in df.groupby(by=["date"]):
        date = group_df["date"].tolist()[0]
        tweets = group_df["preprocessed_text"].tolist()

        ids_list = []
        labels_list = []
        for tweet in tweets:
            ids, labels = entity_linking_text(tweet, entities_dict)
            ids_list.append(ids)
            labels_list.append(labels)
            print(f"{count} \r")
            count += 1

        group_df["wikidata_ids"] = ids_list
        group_df["wikidata_labels"] = labels_list
        print("finishing ....", len(group_df), date)

        group_df.to_csv(f"data/wikidata/tweets_wikidata_{date}.csv", index=False)

        df_entities = pd.DataFrame.from_dict(entities_dict, orient="index")
        df_entities.to_csv(f"data/wikidata/entities_tweets_{date}.csv")

def test_sample(text):
    entities_dict = defaultdict(dict)
    labels, ids = entity_linking_text(text, entities_dict)
    print(text)
    print(labels)
    print(ids)


if __name__ == '__main__':
    text ="This was reportedly filmed in #Chuhuiiv, #Kharkiv region, east #Ukraine: results of a missile strike by #Russias armed forces"
    text1 = "This was reportedly filmed in Chuhuiiv, Kharkiv region, east Ukraine: results of a missile strike by Russias armed forces"
    test_sample(text)
    print("*"*20)
    test_sample(text1)
