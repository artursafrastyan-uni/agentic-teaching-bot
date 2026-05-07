import urllib.request
import json
import urllib.parse
import re

def search_web(query: str, max_results: int=3) -> list:
    results = []
    clean_query = query.replace('tutorial', '').replace('or best resources', '').strip()
    if not clean_query:
        clean_query = 'Natural Language Processing'
    try:
        search_url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_query)}&utf8=&format=json&srlimit={max_results}'
        req = urllib.request.Request(search_url, headers={'User-Agent': 'AgenticTeachingBot/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
        search_hits = data.get('query', {}).get('search', [])
        for hit in search_hits:
            title = hit['title']
            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            snippet = hit.get('snippet', '')
            snippet = re.sub('<[^<]+>', '', snippet)
            results.append({'title': f'Wikipedia: {title}', 'url': url, 'snippet': snippet + '...'})
        return results
    except Exception as e:
        print(f'Web search encountered an error: {e}')
        return results
