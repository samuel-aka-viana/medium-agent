import os
import json
from datetime import datetime
from dotenv import load_dotenv
from crew import TechAnalysisCrew

load_dotenv()

ARQUIVO_SAIDA = 'guia_implementacao_pratico.md'
ARQUIVO_REFERENCIAS = 'referencias_pesquisa.txt'

def run():
    inputs = {
        'ferramentas_alvo': 'SeaweedFS e VersityGW',
        'ferramenta_legada': 'MinIO',
        'contexto': 'mudança de licença para AGPLv3 limitando uso comercial corporativo livre em 2025',
        'requisito_tecnico': 'paridade total com a API S3 da AWS e performance de IOPS para arquivos pequenos'
    }

    print(f"\nIniciando pipeline para: {inputs['ferramentas_alvo']}...")
    try:
        if os.path.exists(ARQUIVO_REFERENCIAS):
            os.remove(ARQUIVO_REFERENCIAS)

        crew_instance = TechAnalysisCrew().crew()
        result = crew_instance.kickoff(inputs=inputs)

        usage_metrics = {
            "timestamp": datetime.now().isoformat(),
            "topic": inputs['ferramentas_alvo'],
            "usage": result.token_usage.dict() if hasattr(result, 'token_usage') else "N/A"
        }

        with open('metrics_usage.json', 'a', encoding='utf-8') as f:
            json.dump(usage_metrics, f, indent=4, ensure_ascii=False)
            f.write("\n")

        if os.path.exists(ARQUIVO_SAIDA) and os.path.exists(ARQUIVO_REFERENCIAS):
            with open(ARQUIVO_SAIDA, "a", encoding="utf-8") as out_file:
                out_file.write("\n\n## Referências Consultadas\n")
                with open(ARQUIVO_REFERENCIAS, "r", encoding="utf-8") as ref_file:
                    out_file.write(ref_file.read())

        print("\nPipeline finalizada. Arquivos gerados.")

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] A pipeline falhou. Detalhes:\n{e}")

if __name__ == "__main__":
    run()