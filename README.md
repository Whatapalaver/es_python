Python ElasticSearch Practice
===

This is a python / flask program setup in a virtualenvironment.
It will be used to connect with an ES instance currently running on localhost:9100 (run controlled by repo vam_es_reactivesearch_test)

Progress and Lack thereof
---
- [ ] I have incompletely implemented some python code to perform reindexing and bulk imports. These are currently in gitignore as they don't work
- [x] I've added the simpleexplain functionality that outputs the scoring explanation to the console
- [x] Notes on analysis and mapping changes are in VAM_ES_REACTIVESEARCH_TEST repo as `settingsLog.md`
- [x] I've implemented elaticssearch-dsl with a complex Query function that allows query on nested fields 

To Run
---

- To activate the virtualenv `source venv/bin/activate`
- If you are using .flaskenv you can start the server with `flask run`
- If you haven't set an environment variable you will need to run `export FLASK_APP=es_python.py` first.


Shout-outs
---

- Basic Flask interface with Elasticsearch. [Blog and repo by Dinesh Sonachalam](https://medium.com/devopslinks/building-a-real-time-elastic-search-engine-using-python-32e05bcb9140).
- I'm utilising a lot of the helper functions from the jupyter notebooks that accompany Relevant Search by Doug Turnbull and John Berryman
