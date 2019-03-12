# make sure ES is up and running
import requests, json
from flask import Flask, Blueprint, jsonify, request, render_template
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9100}])

# creating a Blueprint class
search_blueprint = Blueprint('search',__name__,template_folder="templates")
search_term = ""


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
          "query_string": {
              "analyze_wildcard": True,
              "query": str(search_term),
              "fields": ["physicalDescription", "object"]
          }
        },
        "size": 50,
        "sort": [

        ]
      }
      res = es.search(index="objects_010319", body=payload)
      return render_template('index.html', res=res)
      # return jsonify(res['hits']['hits'])
