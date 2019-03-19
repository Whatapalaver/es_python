# make sure ES is up and running
import requests, json
from flask import Flask, Blueprint, jsonify, request, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch, Match
from query.query import ESQuery

app = Flask(__name__)

client = Elasticsearch([{'host': 'localhost', 'port': 9100}])

search_term = ""

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
    resp = requests.get("http://localhost:9100/objects_150319/_analyze?%s&format=yaml" % whatToAnalyze, 
                        data=text)
    print(resp.text)


# this returns the results of a more complex query written as an external ESQuery function
@app.route('/', methods=['GET', 'POST'])
def dsl_search():
  if request.method=='GET':
    res ={
          'hits': {'total': 0, 'hits': []}
          }
    return render_template("index.html",res=res)
  elif request.method =='POST':
      print("-----------------Calling search Result from ESQuery ----------")
      search_term = request.form["input"]
      print("Search Term:", search_term)
      
      res = ESQuery(index='objects_150319',
                      searchfields=['_all', "metadata", "physicalDescription", "object"],
                      returnfields=['metadata', 'title', 'images', "physicalDescription", "object"],
                    #   nested_much=['categories', 'categories.id'],
                      query=search_term)
      
      print('*******Simple explain*********')
      print('')
      for hit in res['hits']['hits']:
        print('')
        if hit['_source']['title']:
          print(hit['_source']['title'][0]['title'], ' --> Score: ', hit._score)
        else: 
          print('Untitled', ' --> Score: ', hit._score)
        print('-----------------------------------')
        # print(res)
        print(simplerExplain(hit['_explanation']))
      # for tag in res.aggregations.per_tag.buckets:
      #   print(tag.key, tag.max_lines.value)
      
      return render_template('index.html', res=res)



if __name__ == "__main__":
    app.run(port=5000, debug=True)
