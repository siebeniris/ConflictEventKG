from collections import defaultdict
from itertools import chain

import pandas as pd
import spacy

# PIPELINE = "en_core_web_trf"
PIPELINE = "en_core_web_sm"
nlp = spacy.load(PIPELINE)

df = pd.read_csv("data/events/events_20220224-20220304.csv")
texts = df["event_text"].tolist()
print(texts[:10])
processed_docs = list(nlp.pipe(texts))


def detect_verbs_nouns(doc):
    """
    Get the verbs and nouns from doc
    :param doc:
    :return:
    """
    roots = []
    root_pos = []
    dobjs = []
    dobjs_pos = []
    for word in doc:
        if word.dep_ == "ROOT":
            roots.append(word.lemma_)
            root_pos.append(word.pos_)
            for subword in word.children:
                if subword.dep_ == "dobj":
                    dobjs.append(subword.lemma_)
                    dobjs_pos.append(subword.pos_)
    return roots, root_pos, dobjs, dobjs_pos


roots_list, root_pos_list, dobjs_list, dobjs_pos_list = [], [], [], []
for doc in processed_docs:
    roots, root_pos, dobjs, dobjs_pos = detect_verbs_nouns(doc)
    roots_list.append(roots)
    root_pos_list.append(root_pos)
    dobjs_list.append(dobjs)
    dobjs_pos_list.append(dobjs_pos)


df_root = pd.DataFrame.from_dict({
        "root": list(chain.from_iterable(roots_list)),
        "root_pos": list(chain.from_iterable(root_pos_list))
    })


df_dobj = pd.DataFrame.from_dict({
"dobj": list(chain.from_iterable(dobjs_list)),
        "dobj_pos": list(chain.from_iterable(dobjs_pos_list))

})

df_root.to_csv("data/extracted_roots.csv", index=False)
df_dobj.to_csv("data/extracted_dobjs.csv", index=False)
