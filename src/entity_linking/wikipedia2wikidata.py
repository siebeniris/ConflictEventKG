from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from src.utils.utils import chunks
import time
import json


def get_query(wiki_labels):
    # "Ministry of Defence (Russia)"@en
    # "Wikidata"@en
    QUERY_ = "\n".join(['\"' + label + '\"@en' for label in wiki_labels])
    print(QUERY_)
    QUERY_BEF = """
    SELECT ?lemma ?item WHERE {
      VALUES ?lemma {
      
      """

    QUERY_AFTER = """
      }
      ?sitelink schema:about ?item;
        schema:isPartOf <https://en.wikipedia.org/>;
        schema:name ?lemma.
    }
    """
    return QUERY_BEF + QUERY_ + QUERY_AFTER


df = pd.read_csv("data/entities_wiki_dedup.csv")
wiki_labels = df["entity_name"].tolist()
chuks = list(chunks(wiki_labels, 10))
print(chuks)


WIKI_LABELS = ["NATO summit", "Secretary General of NATO"]
for idx, chuk in enumerate(chuks[37:]):
    idx += 37
    print(chuk)
    entities_dict = dict()

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    QUERY = get_query(chuk)
    print(QUERY)

    sparql.setQuery(QUERY)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        label = result["lemma"]["value"]
        uri = result["item"]["value"]
        entities_dict[label] = uri


    with open(f"data/wikidata/event_wiki2data_entities_{idx}.json", "w") as f:
        json.dump(entities_dict, f)
    time.sleep(10)
