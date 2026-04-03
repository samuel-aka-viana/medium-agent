import json
import os
from datetime import datetime as dt
from crewai.flow.flow import Flow, start, listen, router
from dotenv import load_dotenv

from crews.search_audit_crew.search_audit_crew import PesquisaAuditoriaCrew
from crews.write_validate_crew.write_validate_crew import EscritaValidacaoCrew

load_dotenv()

ARQUIVO_SAIDA = 'guia_implementacao_pratico.md'
ARQUIVO_REFERENCIAS = 'output/referencias_pesquisa.txt'


class TechAnalysisFlow(Flow):
    def __init__(self):
        super().__init__()
        self.inputs = {
            'ferramentas_alvo': 'Snowflake e BigQuery',
            'contexto': 'Armazenamento e processamento analítico',
            'requisito_tecnico': 'Modelo de pricing, otimização de custos, separação compute/storage, custos ocultos de rede',
        }

    @start()
    def executar_pesquisa(self):
        print(f"\n[1/2] Iniciando Pesquisa e Auditoria para: {self.inputs['ferramentas_alvo']}...")

        if os.path.exists(ARQUIVO_REFERENCIAS): os.remove(ARQUIVO_REFERENCIAS)
        if os.path.exists(ARQUIVO_SAIDA): os.remove(ARQUIVO_SAIDA)

        self.state['dados_auditoria'] = "Nenhum dado extraído."

        try:
            crew_pesquisa = PesquisaAuditoriaCrew().crew()
            resultado_pesquisa = crew_pesquisa.kickoff(inputs=self.inputs)

            self._salvar_metricas(resultado_pesquisa, "Pesquisa")

            if hasattr(resultado_pesquisa, 'tasks_output') and len(resultado_pesquisa.tasks_output) >= 2:
                fatos_estruturados = resultado_pesquisa.tasks_output[-2].raw
                auditoria_final = resultado_pesquisa.tasks_output[-1].raw
                self.state[
                    'dados_auditoria'] = f"=== DADOS TÉCNICOS EXTRAÍDOS ===\n{fatos_estruturados}\n\n=== AUDITORIA SRE ===\n{auditoria_final}"
            else:
                self.state['dados_auditoria'] = resultado_pesquisa.raw

        except Exception as e:
            print(f"\n[AVISO] A auditoria falhou ou o Guardrail abortou: {e}")
            print("→ Resgatando dados parciais da extração e forçando a escrita do artigo...")

            fatos_recuperados = "Dados estruturados não disponíveis."
            if os.path.exists('output/debug_json_extracao.txt'):
                with open('output/debug_json_extracao.txt', 'r', encoding='utf-8') as f:
                    fatos_recuperados = f.read()

            self.state[
                'dados_auditoria'] = f"=== DADOS TÉCNICOS EXTRAÍDOS (RECUPERADOS) ===\n{fatos_recuperados}\n\n=== AUDITORIA SRE ===\n[PREENCHER MANUALMENTE: A auditoria SRE falhou na formatação e foi ignorada]"

        return self.state['dados_auditoria']

    @listen(executar_pesquisa)
    def executar_escrita(self, dados_auditoria):
        print("\n[2/2] Iniciando Escrita e Validação...")

        inputs_escrita = self.inputs.copy()
        inputs_escrita['dados_auditoria'] = dados_auditoria

        crew_escrita = EscritaValidacaoCrew().crew()
        resultado_final = crew_escrita.kickoff(inputs=inputs_escrita)

        self._salvar_metricas(resultado_final, "Escrita")

        self.state['status'] = 'concluido'
        self._anexar_referencias()

        self.state['resultado_final'] = resultado_final.raw
        return self.state['resultado_final']

    @router(executar_escrita)
    def avaliar_ciclo(self):
        return 'finalizar'

    @listen('finalizar')
    def finalizar_fluxo(self):
        print("\nFluxo encerrado. Artigo gerado (com placeholders, se necessário).")
        return self.state['resultado_final']

    def _salvar_metricas(self, resultado, etapa):
        try:
            usage_metrics = {
                "timestamp": dt.now().isoformat(),
                "topic": self.inputs['ferramentas_alvo'],
                "etapa": etapa,
                "usage": resultado.token_usage.dict() if hasattr(resultado, 'token_usage') else "N/A"
            }
            with open('output/metrics_usage.json', 'a', encoding='utf-8') as f:
                json.dump(usage_metrics, f, indent=4, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"Erro ao salvar métricas da etapa {etapa}: {e}")

    def _anexar_referencias(self):
        if os.path.exists(ARQUIVO_SAIDA) and os.path.exists(ARQUIVO_REFERENCIAS):
            with open(ARQUIVO_SAIDA, "a", encoding="utf-8") as out_file:
                out_file.write("\n\n## Referências Consultadas\n")
                with open(ARQUIVO_REFERENCIAS, "r", encoding="utf-8") as ref_file:
                    out_file.write(ref_file.read())