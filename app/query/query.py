from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A
from elasticsearch_dsl.query import Q, MultiMatch, Match
import json

client = Elasticsearch([{'host': 'localhost', 'port': 9100}])

def ESQuery(index=None, 
            searchfields=None, 
            returnfields=None,
            query=None, # search_term
            source_fields=None, 
            aggregations=None,
            advanced=None, # used to add additional 'must' advanced search fields to search
            advanced_should=None, # used to add additional 'must' advanced search fields to search
            sort_order=[],
            nested=None,
            nested_must=None,
            nested_should=None,
            nested_range=None,
            preference="_primary_first",  
            explain=None,
            offset=0, 
            limit=15, 
            fuzziness=1):
    s = None
    s = Search(using=client, index=index).source(returnfields)
    s = s.params(preference=preference)
    q = None
    queries = []

    if nested is not None:
        print("Adding nested search")
        for nest in nested:
            queries.append(Q("nested", path=nest[0],
                             query=Q("match", **{nest[1]: nest[2]})))

    if nested_must is not None:
        for nest in nested_must:
            queries.append(Q("nested", path=nest[0],
                             query=Q("match", **{nest[1]: nest[2]})))

        s = s.query(Q('bool', must=queries))[offset:limit]
        queries = []

    if nested_should is not None:
        for nest in nested_should:
            queries.append(Q("nested", path=nest[0],
                             query=Q("match", **{nest[1]: nest[2]})))

        s = s.query(Q('bool', should=queries))[offset:limit]

        if len(nested_should) > 1:
          s.query.minimum_should_match = 1

        queries = []

    if nested_range is not None:
        for nest in nested_range:
            queries.append(Q("nested", path=nest[0],
                             filter=Q("range", **{nest[1]: {nest[2]: nest[3]}})))
        s = s.query(Q('bool', must=queries))
        queries = []

    if advanced is not None:
        raw_queries = []
        for advance in advanced:
          print("Adding match search on %s" % advance[0])
          raw_queries.append(Q("match", **{ advance[0]: advance[1]}))

          s = s.query(Q('bool', must=raw_queries))

    if advanced_should is not None:
        for advance in advanced_should:
            queries.append(Q("match", **{ advance[0]: advance[1]}))
        s = s.query(Q('bool', should=queries))[offset:limit]
        queries = []

    if searchfields is not None:
      if query is not None and query != '':
        queries.append(Q("simple_query_string", query=query, default_operator="and", flags="PREFIX|PHRASE|NOT|AND|OR", fields=searchfields))


    if len(queries) > 1:
        s = s.query(Q('bool', should=queries))[offset:limit]
    elif len(queries) > 0:
        s = s.query(Q('bool', must=queries[0]))[offset:limit]

    if source_fields is not None:
        s = s.extra(_source={'include': source_fields})

    if len(sort_order) > 0:
        s = s.sort(sort_order[0])



    if aggregations is not None:
        for agg in aggregations:
            a = A('terms', field=agg[1], size=10)
            s.aggs.bucket(agg[0], a)

    s = s.extra(explain=explain)
   
    results = s.execute()
    print("Query: ", json.dumps(s.to_dict()))

    print("Results: ", json.dumps(results.to_dict()))
    return results


def ObjectGetQuery(index=None, 
                  searchfields=None, 
                  returnfields=None,
                  query=None, # search_term
                  source_fields=None, 
                  offset=0, 
                  limit=15, 
                  explain=False,
                  fuzziness=1):
    s = None
    s = Search(using=client, index=index).source(returnfields)
 
    q = None
    queries = []

    if searchfields is not None:
      if query is not None and query != '':
        queries.append(Q("simple_query_string", query=query, default_operator="and", flags="PREFIX|PHRASE|NOT|AND|OR", fields=searchfields))
        s = s.query(Q('bool', must=queries[0]))[offset:limit]

    if source_fields is not None:
        s = s.extra(_source={'include': source_fields})

    s = s.extra(explain=explain)
   
    results = s.execute()
    print("ObjectGetQuery: ", json.dumps(s.to_dict()))

    # print("Results: ", json.dumps(results.to_dict()))
    return results