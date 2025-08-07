import httpx

def get_search_fuzzy(query):
    # Baca subscription key dari file
    with open("api.txt", "r") as f:
        subscription_key = f.read().strip()

    url = "https://atlas.microsoft.com/search/fuzzy/json"
    params = {
        'subscription-key': subscription_key,
        'api-version': '1.0',
        'query': query
    }

    response = httpx.get(url, params=params)
    return response.json()

query = "Takengon, Aceh Tengah, Aceh"
response_json = get_search_fuzzy(query)

for item in response_json['results']:
    print('Result Type:', item.get('type'))
    if 'poi' in item:
        print('Name:', item['poi'].get('name', 'N/A'))
    print('Address:', item['address'].get('freeformAddress', 'N/A'))
    print('Lat Long:', item.get('position'))
    print('---------------------------')
