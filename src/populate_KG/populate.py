import json
from datetime import datetime
from ast import literal_eval

import rdflib
import pandas as pd
import numpy as np
import uuid

from rdflib.namespace import Namespace
from rdflib.namespace import DC, DCTERMS, OWL, RDF, RDFS, XMLNS, XSD, TIME
from rdflib import URIRef, Literal

g = rdflib.Graph()
# g.parse("data/schema/schema_CEKG.owl", format="application/rdf+xml")
g.parse("data/schema/schema_CEKG.owl", format="ttl")

sem = Namespace("http://semanticweb.cs.vu.nl/2009/11/sem/")
sioc = Namespace('http://rdfs.org/sioc/ns#')
sioc_t = Namespace('http://rdfs.org/sioc/types#')
nee = Namespace('http://www.ics.forth.gr/isl/oae/core#')
schema = Namespace('http://schema.org/')
cidoc_crm = Namespace("https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html#")
eventKG_s = Namespace("http://eventKG.l3s.uni-hannover.de/schema/")
CEKG = Namespace("https://siebeniris.github.io/ConflictEventKG/")
cekg = Namespace(CEKG)

# binding
g.bind("dc", DC)
g.bind("nee", nee)
g.bind("owl", OWL)
g.bind('rdf', RDF)
g.bind("sem", sem)
g.bind("xml", XMLNS)
g.bind("xsd", XSD)
g.bind("cekg", cekg)
g.bind("rdfs", RDFS)
g.bind("sioc", sioc)
g.bind("time", TIME)
g.bind("schema", schema)
g.bind("sioc_t", sioc_t)
g.bind("dcterms", DCTERMS)
g.bind("cidoc-crm", cidoc_crm)
g.bind("eventKG-s", eventKG_s)


# final/ entities.csv/events.csv/tweets.csv
# entities

def define_entity_resources():
    """
    Define entity resources
    :return:
    """
    filepath = "data/final/entities.csv"
    df_entities = pd.read_csv(filepath, index_col=0)
    entities_dict = df_entities.to_dict(orient="index")
    # entity_id,description,label,url
    for entity_id, entity_dict in entities_dict.items():
        description = entity_dict["description"]
        label_ = entity_dict["label"]
        url = entity_dict["url"]
        ent_instance = URIRef(url)
        g.add((ent_instance, RDF.type, RDFS.Resource))
        g.add((ent_instance, RDFS.label, Literal(label_)))
        g.add((ent_instance, DCTERMS.description, Literal(description)))


def define_event_resources():
    filepath = "data/final/events.csv"
    df_event = pd.read_csv(filepath, index_col=0)
    main_events = list(set(df_event["main_event"].tolist()))
    actors = list(set(df_event["first_actor"].tolist()))
    actors_dict = {actor: idx for idx, actor in enumerate(actors)}

    roles = list(set(df_event["category"].tolist()))
    roles_dict = {role: idx for idx, role in enumerate(roles)}

    events_dict = df_event.to_dict(orient="index")
    wikidata = "https://www.wikidata.org/wiki/Q"
    # id,category,date,event_text,main_event,first_sentence,first_actor,
    # wikidata_labels,wikidata_ids,event_id,extractedFrom
    #actors
    for idx, actor in enumerate(actors):
        actor_instance = URIRef(CEKG+f"actor_{idx}")
        g.add((actor_instance, RDF.type, sem.Actor))
        g.add((actor_instance, RDFS.label, Literal(actor)))
    # roles
    for idx, role in enumerate(roles):
        role_instance = URIRef(CEKG + f"roke_type_{idx}")
        g.add((role_instance, RDF.type, sem.RoleType))
        g.add((role_instance, RDFS.label, Literal(role)))


    main_event_dict = {main_event: idx for idx, main_event in enumerate(main_events)}
    print(main_event_dict)
    for idx, main_event in enumerate(main_events):
        main_event_instance = URIRef(CEKG+f"main_event_{idx}")
        # description only
        g.add((main_event_instance, RDF.type, sem.Event))
        g.add((main_event_instance, DCTERMS.description, Literal(main_event)))
    for idx, event_dict in events_dict.items():
        category = event_dict["category"]
        date = event_dict["date"]
        event_text = event_dict["first_sentence"]
        actor = event_dict["first_actor"]
        main_event = event_dict["main_event"]
        wikidata_ids = literal_eval(event_dict["wikidata_ids"])
        event_id = event_dict["event_id"]
        extractedFrom = event_dict["extractedFrom"]
        # event
        event_instance = URIRef(CEKG+f"event_{event_id}")
        g.add((event_instance, DCTERMS.description, Literal(event_text)))
        g.add((event_instance, eventKG_s.extractedFrom, URIRef(extractedFrom)))
        g.add((event_instance, sem.hasBeginTimeStamp, Literal(date)))
        g.add((event_instance, sem.hasEndTimeStamp, Literal(date)))
        g.add((event_instance, eventKG_s.startUnitType, TIME.unitDay))
        main_event_id = main_event_dict[main_event]
        main_event_instance = URIRef(CEKG + f"main_event_{main_event_id}")
        g.add((main_event_instance, sem.hasSubEvent, event_instance))

        for wikidata_id in wikidata_ids:
            ent_instance = URIRef(wikidata+f"{wikidata_id}")
            ent_mention_instance = URIRef(CEKG+f"ent_mention_{event_id}_{wikidata_id}")
            g.add((ent_mention_instance, RDF.type, nee.Entity))
            g.add((event_instance, schema.mentions, ent_mention_instance))
            g.add((ent_mention_instance, schema.mentions, ent_instance))

        # actor
        actor_id = actors_dict[actor]
        actor_instance = URIRef(CEKG + f"actor_{actor_id}")

        # relation
        role_id = roles_dict[category]
        role_type_instance = URIRef(CEKG + f"roke_type_{role_id}")
        relation_instance = URIRef(CEKG+f"relation_{idx}")
        g.add((relation_instance, RDF.type, eventKG_s.Relation))
        g.add((relation_instance, RDF.object, event_instance))
        g.add((relation_instance, RDF.subject, actor_instance))
        g.add((relation_instance, sem.roleType, role_type_instance))
        g.add((relation_instance, sem.hasBeginTimeStamp, Literal(date)))
        g.add((relation_instance, sem.hasEndTimeStamp, Literal(date)))
        g.add((relation_instance, eventKG_s.startUnitType, TIME.unitDay))








if __name__ == '__main__':
    # define_entity_resources()
    define_event_resources()

    g.serialize(destination=f"data/final/CEKG.nt", format="nt")

