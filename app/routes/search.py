# make sure ES is up and running
import requests, json
from flask import Flask, Blueprint, jsonify, request, render_template
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9100}])

# creating a Blueprint class
search_blueprint = Blueprint('search',__name__,template_folder="templates")
search_term = "building"

# helper functions

# Some utilities for flattening the explain into something a bit more
# readable. Pass Explain JSON, get something readable (ironically this is what Solr's default output is :-p)
def flatten(l):
    [item for sublist in l for item in sublist]

def simplerExplain(explainJson, depth=0):
    result = " " * (depth * 2) + "%s, %s\n" % (explainJson['value'], explainJson['description'])
    #print json.dumps(explainJson, indent=True)
    if 'details' in explainJson:
        for detail in explainJson['details']:
            result += simplerExplain(detail, depth=depth+2)
    return result
    
def analyze(text, field=None, analyzer=None):
    whatToAnalyze = ''
    if field is not None:
        whatToAnalyze = "field=%s" % field
    elif analyzer is not None:
        whatToAnalyze = "analyzer=%s" % analyzer
    resp = requests.get("http://localhost:9100/objects_010319/_analyze?%s&format=yaml" % whatToAnalyze, 
                        data=text)
    print(resp.text)


@search_blueprint.route('/', methods=['GET', 'POST'], endpoint='index')
def index():
  # results = es.get(index='sw', doc_type='people', id=5)
  # return jsonify(results['_source'])
  if request.method=='GET':
    res ={
          'hits': {'total': 0, 'hits': []}
          }
    return render_template("index.html",res=res)
  elif request.method =='POST':
    if request.method == 'POST':
      print("-----------------Calling search Result----------")
      search_term = request.form["input"]
      print("Search Term:", search_term)
      payload = {
        "query": {
          "multi_match": {
              "query": str(search_term),
              "fields": ["physicalDescription", "object", "metadata^3"],
              "type": "most_fields"
          }
        },
        "size": 50,
        "sort": [

        ]
      }
      res = es.search(index="objects_010319", body=payload, explain=True)

      # print(json.dumps(res['hits']['hits'][0]['_explanation'], indent=2))

      print('*******Simple explain*********')
      print('')
      for hit in res['hits']['hits']:
        print(simplerExplain(hit['_explanation']))
      
      return render_template('index.html', res=res)

