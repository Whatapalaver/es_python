# make sure ES is up and running
import requests, json
from flask import Flask, Blueprint, jsonify, request, render_template
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import MultiMatch, Match
from query.query import ESQuery, ObjectGetQuery

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
    resp = requests.get("http://localhost:9100/objects_200319/_analyze?%s&format=yaml" % whatToAnalyze, 
                        data=text)
    print(resp.text)


# this returns the results of a more complex query written as an external ESQuery function
@app.route('/', methods=['GET', 'POST'])
def global_search():

  advanced_search = []
  advanced_should = []
  nested_should_search = []
  nested_must_search = []
  nested_search = []
  nested_range = []
  sort_order = []
  inc_explain = False

  if request.method=='GET':
    res ={
          'hits': {'total': 0, 'hits': []}
          }
    return render_template("index.html",res=res)
  elif request.method =='POST':
      print("-----------------Calling search Result from ESQuery ----------")
      search_term = request.form["input"]
      print("Search Term:", search_term)

    #   nested_search.append(('title', 'title.title', search_term))
    #   nested_should_search.append(('artistMakerPerson.name', 'artistMakerPerson.name__text',  search_term))
    #   nested_should_search.append(('artistMakerPeople.name', 'artistMakerPeople.name__text',  search_term))
    #   nested_should_search.append(('artistMakerOrganisation.name', 'artistMakerOrganisation.name__text',  search_term))
    #   nested_should_search.append(('categories', 'categories.raw',  search_term))
    #   nested_should_search.append(('techniques', 'techniques.text__raw',  search_term))
      
      res = ESQuery(index='objects_200319',
                      searchfields=["physicalDescription", "uniqueId", "object", "materialsTechniques", "objectNumber", "museumNumber", "gs_artistMakerOrganisation", \
                                    "gs_artistMakerPeople", "gs_artistMakerPerson", "gs_associatedEvent", "gs_associatedOrganisation", \
                                    "gs_associatedPeople", "gs_associatedPerson", "gs_associatedPlace", "gs_categories", "gs_collectionCode_id", \
                                    "gs_collectionCode_text", "gs_contentConcept", "gs_contentEvent", "gs_contentOrganisation", "gs_contentOther", \
                                    "gs_contentPeople", "gs_contentPerson", "gs_contentPlace", "gs_galleryLocation", "gs_labelsAndDate", \
                                    "gs_marksAndInscriptions", "gs_materials", "gs_productionType", "gs_style", "gs_techniques", "gs_title"],
                    #   returnfields=['metadata', 'title', 'images', "physicalDescription", "object", ],
                      aggregations=[['by_collection_code', 'gs_collectionCode_id']],
                      explain=inc_explain,
                      nested=nested_search,
                      nested_range=nested_range,
                      nested_should=nested_should_search,
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
        if inc_explain is True:
            print(simplerExplain(hit['_explanation']))
    #   for tag in res.aggregations.per_tag.buckets:
        # print(tag.key, tag.max_lines.value)
      for item in res.aggregations.by_collection_code.buckets:
        # item.key will the house number
        print(item.key, item.doc_count)
      return render_template('index.html', res=res)


@app.route('/museumObject/<url_uniqueID>/', methods=['GET', 'POST'])
def get_object(url_uniqueID=None):
    results_format = request.args.get('format', '')

    uniqueID = url_uniqueID
    print('Iniqued ID ', uniqueID)

    result = ObjectGetQuery(index='objects_200319', searchfields=["uniqueID"], query=uniqueID)
    for hit in result['hits']['hits']:
        print(hit)

    return render_template('object.html', res=result)

    # json_data = json.dumps([{ "pk": 10000,
	# 		"model": "collection.museumobject",
	# 		"fields": make_legacy_object_api(obj, None) }])

    # return Response(json_data,  mimetype='application/javascript')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
