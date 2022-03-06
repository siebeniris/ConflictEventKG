# Conflict Event Knowledge Graph


## wikipedia current events
can download directly
https://github.com/kiwicopple/current-events



## Usage
1. install requirements
`pip install -r requirements.txt`
2. install spacy 

```
pip install -U pip setuptools wheel
pip install -U 'spacy[apple]'
python -m spacy download en_core_web_sm

```
3. set up spacy entity linker
To install the package run: `pip install spacy-entity-linker`

Afterwards, the knowledge base (Wikidata) must be downloaded. This can be done by calling

`python -m spacy_entity_linker "download_knowledge_base"`

This will download and extract a ~500mb file that contains a preprocessed version of Wikidata



## Steps
### Wikipedia
1. Crawling Wikipedia Pages
2. Notebooks, extract events. 

### Crawling Tweets
`python -m src.crawler.twitter_crawler`

### Preprocessing Tweets
1. structure crawled tweets into json files, save to the folder `data/output/preprocessed/restructured`

`python -m src.preprocessor.restructure_data`


2. Convert json into dataframes, save to the folder `data/output/preprocessed/dataframes` => for populating KB

`python -m src.preprocessor.dict2df`

3. Preprocessing tweets, save to the folder `data/output/preprocessed/final` 

`python -m src.preprocessor.preprocessing`

4. merge all the preprocessed dataframes `data/output/preprocessed/final/all.csv` =>  for entity linking.

` python -m src.preprocessor.merge_dataframes`

### Entity linking

1. entity linking for event text
`python -m src.entity_linking.wikidata_linker`


### Event Twitter Connection

`python src/event_detection/event_tweet_assoc.py`

## Resources
https://andrewhalterman.com/post/event-data-in-30-lines-of-python/
