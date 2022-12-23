from http import HTTPStatus
from typing import Dict
from fastapi import FastAPI, Request, Form
from elasticsearch import Elasticsearch
from fastapi.staticfiles import StaticFiles
import datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import uvicorn


app = FastAPI(title="Tweets Project")
client = Elasticsearch(hosts="http://localhost:9200")
index_name = "tweets_test"
filename = "C:\\Users\\User\\boulder_flood_geolocated_tweets.json"
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# This function constructs a query with the given parameters for text, distance, coordinates, and date range
def make_query(text: str, distance: int= 22078, corrs: list[float]=[-180,-90], start_date: str = "", end_date: str = ""):
    '''
    The body of the query consists of a bool query with three "must" clauses:
    1. A fuzzy search for the given text
    2. A geo distance filter for the given distance and coordinates
    3. A range filter for the given date range
    '''
    body = {
        "query": {
            "bool": {
                "must":
                [
                    {
                        "fuzzy":{
                            "text": text
                        }
                    },
                    {
                      "geo_distance": {
                        "distance": distance+"km",
                        "coordinates": corrs
                           
                      }
                    },
                    {
                        "range":{
                            "created_at":{
                                "gte": start_date,
                                "lte": end_date
                            }
                        }
                    }
                ]
            }
        }
    }
    return body 

# This function searches an Elasticsearch index using the given query and returns the search results
def search_res(query):
    
    search = client.search(index="tweets_test", body=query)
    # Perform the search using the Elasticsearch client and the specified index. 
    
    data = []
    tweets = []

    for i in range(len(search["hits"]["hits"])):
        doc = {
            "lng": search["hits"]["hits"][i]["_source"]["coordinates"]["coordinates"][0],
            "lat": search["hits"]["hits"][i]["_source"]["coordinates"]["coordinates"][1],
            "count": int(search["hits"]["hits"][i]["_score"])
        }
        # Extract the longitude, latitude, and score (count) from the search result and store it in the `doc` dictionary
        
        tweet = {
            "text": search["hits"]["hits"][i]["_source"]["text"]
        }
        # Extract the text from the search result and store it in the `tweet` dictionary
        
        data.append(doc)
        tweets.append(tweet)
        # Append the `doc` and `tweet` dictionaries to the `data` and `tweets` lists, respectively
    
    return data, tweets
    

# def top_ten_terms():
#     # The query: an Elasticsearch aggregation to get the top 10 terms used in the "text" field
#     tst = {
#         "size": 0,
#         "aggs": {
#             "most_used_terms": {
#             "terms": {
#                 "field": "text",
#                 "size": 10,
#                 "order": {
#                 "_count": "desc"
#                 }
#             }
#             }
#         }
#     }

#     # Perform a search using the client and the defined aggregation
#     keys_list = client.search(index=index_name, body=tst)["aggregations"]["most_used_terms"]["buckets"]
#     top_terms = []
    
#     # Iterate over the list of aggregated terms
#     for key in range(len(keys_list)): 
#         top_terms.append(keys_list[key]["key"])
    
#     return top_terms


#Health check 
@app.get("/", response_class=HTMLResponse)
def _index(request: Request):
    return templates.TemplateResponse('items.html', {'request': request})


# This is a GET request handler that accepts query parameters from the request and returns search results
@app.get("/items")
async def create_item(request: Request):

    # Extract the query parameters from the request and store them in a dictionary
    params = dict(request.query_params.items()) 
    
    # Initialize default values
    text = params["text"]
    distance = params["distance"]
    long, lat, start_date, end_date  =  -180, -90, None, None
    
    #type casting from strings to float/date. 
    if params["long"] != "":
        long = float(params["long"])
    if params["lat"] != "":
        lat = float(params["lat"])
    if params["Sdate"] != "" and params["Edate"] != "":
        start_date = params["Sdate"]
        end_date = params["Edate"]

    # If any of the query parameters are provided, construct the search query using them
    if (start_date, end_date, long, lat, distance) != ("", "", None, None, None):
        search_query = make_query(text, distance, [long, lat], start_date=start_date, end_date=end_date)
    elif start_date and end_date:
        search_query = make_query(text, start_date=start_date, end_date=end_date)
    elif long and lat:
        search_query = make_query(text, coordinates=[long, lat])
    elif distance:
        search_query = make_query(text, distance=distance)
    else:
        search_query = make_query(text)
    # If none of the query parameters are provided, construct the search query using only the text parameter
    
    print(search_query, "\n")
    
    # search = client.search(index="tweets_test", body=search_query)
    # print(search, "\n")
    
    # Perform the search using the Elasticsearch client and the `search_query` constructed above
    # Store the search results in the `test_data` variable
    test_data = search_res(search_query)
    
    print(test_data, "\n")
    
    # top_terms = top_ten_terms()
    # print(top_terms, "\n") 
    
    return{
            "test": params, 
            # "top_terms" : top_terms,
            "data" : test_data[0],
            "tweets": test_data[1]
        }
   

if __name__ == "__main__":
    uvicorn.run("api:app", host= "127.0.0.1", port=8000, reload= True)



# http://localhost:8000/?text=+


