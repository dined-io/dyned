from __future__ import print_statement
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.CollectionsApi()
page = 789 # Long | Page number. Used for pagination with page_size (optional)
pageSize = 789 # Long | The number of results included on a page. Used for pagination with page (optional) (default to 10)
limit = 789 # Long | Number of results included on a page. Used for pagination with query (optional)
offset = 789 # Long | Where to start the listing(the offset of the first result). Used for pagination with limit (optional)
order = order_example # String | The field by which to order. Default varies by endpoint/resource. (optional) (default to published_date)
orderDirection = orderDirection_example # String |  (optional) (default to desc)
institution = 789 # Long | only return collections from this institution (optional)
publishedSince = publishedSince_example # String | Filter by collection publishing date. Will only return collections published after the date. date(ISO 8601) YYYY-MM-DD (optional)
modifiedSince = modifiedSince_example # String | Filter by collection modified date. Will only return collections published after the date. date(ISO 8601) YYYY-MM-DD (optional)
group = 789 # Long | only return collections from this group (optional)
resourceDoi = resourceDoi_example # String | only return collections with this resource_doi (optional)
doi = doi_example # String | only return collections with this doi (optional)
handle = handle_example # String | only return collections with this handle (optional)

try: 
    # Public Collections
    api_response = api_instance.collections_list(page=page, pageSize=pageSize, limit=limit, offset=offset, order=order, orderDirection=orderDirection, institution=institution, publishedSince=publishedSince, modifiedSince=modifiedSince, group=group, resourceDoi=resourceDoi, doi=doi, handle=handle)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling CollectionsApi->collectionsList: %s\n" % e)