import os
import json
import requests
from crewai.tools import tool

ARQUIVO_REFERENCIAS = 'referencias_pesquisa.txt'


@tool("Search SerpAPI")
def search_tool(query: str) -> str:
    """Busca na web e retorna apenas os resultados orgânicos filtrados."""
    api_key = os.getenv("SERPAPI_API_KEY")
    params = {"q": query, "api_key": api_key}

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()

        filtered_results = []
        if "organic_results" in data:
            for result in data["organic_results"][:10]:
                filtered_results.append({
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet")
                })

        with open(ARQUIVO_REFERENCIAS, "a", encoding="utf-8") as f:
            f.write(f"\n[Termo: '{query}']\n")
            for res in filtered_results:
                f.write(f"- {res['link']}\n")

        return json.dumps(filtered_results, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})