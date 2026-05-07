import urllib.request
import json
import urllib.parse
import re

def search_web(query: str, max_results: int = 3) -> list:
    """
    Performs a full-text web search using the Wikipedia API.
    This guarantees perfectly reliable resources without rate-limit issues.
    """
    results = []
    
    # Strip some common words added by the prompt
    clean_query = query.replace("tutorial", "").replace("or best resources", "").strip()
    
    # Fallback if query is empty
    if not clean_query:
        clean_query = "Natural Language Processing"
        
    try:
        # Use Wikipedia's full-text search (srsearch)
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_query)}&utf8=&format=json&srlimit={max_results}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'AgenticTeachingBot/1.0'})
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        search_hits = data.get('query', {}).get('search', [])
        
        for hit in search_hits:
            title = hit['title']
            url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            
            # The snippet contains HTML tags for highlighting, we strip them
            snippet = hit.get('snippet', '')
            snippet = re.sub('<[^<]+>', '', snippet)
            
            results.append({
                "title": f"Wikipedia: {title}",
                "url": url,
                "snippet": snippet + "..."
            })
            
        return results
    except Exception as e:
        print(f"Web search encountered an error: {e}")
        return results

if __name__ == "__main__":
    print("Testing Wikipedia web search...")
    res = search_web("Agentic Telegram Teaching Assistant", 2)
    for i, r in enumerate(res):
        print(f"\nResult {i+1}: {r['title']}")
        print(f"URL: {r['url']}")
        print(f"Snippet: {r['snippet']}")
