import os
import json
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

ARQUIVO_REFERENCIAS = 'referencias_pesquisa.txt'


class SearchInput(BaseModel):
    query: str = Field(description="Termo de busca a ser pesquisado na web")


class SearchTool(BaseTool):
    name: str = "Search SerpAPI"
    description: str = "Busca na web e retorna apenas os resultados orgânicos filtrados."
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
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

            print(f"[DEBUG] Query: '{query}' → {len(filtered_results)} resultados")

            with open(ARQUIVO_REFERENCIAS, "a", encoding="utf-8") as f:
                f.write(f"\n[Termo: '{query}']\n")
                for res in filtered_results:
                    f.write(f"- {res['link']}\n")

            return json.dumps(filtered_results, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Erro na requisição: {e}")
            return json.dumps({"error": str(e)})


search_tool = SearchTool()