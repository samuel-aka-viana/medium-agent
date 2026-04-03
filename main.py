from flows import TechAnalysisFlow


def run():
    try:
        fluxo = TechAnalysisFlow()
        fluxo.kickoff()
        print("\nPipeline finalizada com sucesso.")
    except Exception as e:
        print(f"\n[ERRO CRÍTICO] A pipeline falhou. Detalhes:\n{e}")


if __name__ == "__main__":
    run()
