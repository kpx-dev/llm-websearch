import googleapiclient.discovery

def google_search(query, service):
    # Perform the search using the Google CSE API
    res = service.cse().list(q=query, cx='YOUR_CSE_ID', num=10).execute()

    # Extract and format the search results
    search_results = []
    if 'items' in res:
        for item in res['items']:
            search_results.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item['snippet']}\n")

    return "\n".join(search_results)
