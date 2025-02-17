import requests
import pandas as pd
import urllib.parse
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import SKOS, RDF, DC, DCTERMS, RDFS

df = pd.read_csv("items.csv")
parentDf = pd.read_csv("parent.csv")
#print(df)

baseUri = "https://www.lassemempel.github.io/Terminologien/NAVISone"
thesaurus = URIRef(baseUri)
thesaurusAddendum = URIRef(baseUri + "/")

parentDfColumns = ["id","navisid","de","en","dk","nl","fr","it","es","pl","gr","he"]

dfColumns = ["id","navisid","fk_id_parent","de","en","es","it","nl","dk","gr","fr","pl","he","desc_en","desc_de","origindesc","gettyaat","gettyaatrelationtype","wikidata","wikidatarelationtype"]

g = Graph()
g.add((thesaurusAddendum, RDF.type, SKOS.ConceptScheme))
g.add((thesaurusAddendum, DC.title, Literal("NAVISone")))
g.add((thesaurusAddendum, DC.description, Literal("NAVISone ist ein Thesaurus über Schiffsbegriffe", lang="de")))
g.add((thesaurusAddendum, DC.creator, Literal("Florian Thiery")))

for index, row in parentDf.iterrows():
    concept = URIRef(baseUri + str(row["id"]))
    g.add((concept, RDF.type, SKOS.Concept))
    for language in parentDfColumns[2:]:
        if not pd.isnull(row[language]):
            g.add((concept, SKOS.prefLabel, Literal(row[language], lang=language)))
    g.add((concept, SKOS.inScheme, thesaurusAddendum))
    # top concept
    g.add((concept, SKOS.topConceptOf, thesaurusAddendum))
    g.add((thesaurusAddendum, SKOS.hasTopConcept, concept))
    # iterate over all rows in df where fk_id_parent == id
    for index2, row2 in df[df["fk_id_parent"] == row["id"]].iterrows():
        concept2 = URIRef(baseUri + str(row2["id"]))
        g.add((concept2, RDF.type, SKOS.Concept))
        for language in dfColumns[3:12]:
            if not pd.isnull(row2[language]):
                g.add((concept2, SKOS.prefLabel, Literal(row2[language], lang=language)))
        g.add((concept2, SKOS.inScheme, thesaurusAddendum))
        g.add((concept, SKOS.narrower, concept2))
        g.add((concept2, SKOS.broader, concept))
        # add relations
        if not pd.isnull(row2["gettyaat"]):
            g.add((concept2, SKOS.exactMatch, URIRef("http://vocab.getty.edu/aat/300263190")))
        if not pd.isnull(row2["wikidata"]):
            g.add((concept2, SKOS.exactMatch, URIRef("https://www.wikidata.org/wiki/Q582062")))
        # add descriptions
        if not pd.isnull(row2["desc_en"]):
            g.add((concept2, SKOS.definition, Literal(row2["desc_en"], lang="en")))
        if not pd.isnull(row2["desc_de"]):
            g.add((concept2, SKOS.definition, Literal(row2["desc_de"], lang="de")))
        if not pd.isnull(row2["origindesc"]):
            g.add((concept2, DC.source, Literal(row2["origindesc"])))

g.serialize(destination="navisOne.ttl", format="turtle")
# hardcoden
"""
id 20F045
gettyaat                                                      300263190.0
gettyaatrelationtype                                      skos:exactMatch
wikidata                                                          Q582062
wikidatarelationtype                                      skos:exactMatch
"""
