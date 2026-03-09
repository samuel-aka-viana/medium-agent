from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from custom_tools import search_tool

# Modelos otimizados para 12GB VRAM
llm_lite = LLM(model='ollama/gemma3', base_url='http://localhost:11434', temperature=0.0)
llm_validator = LLM(model='ollama/gemma3', base_url='http://localhost:11434', temperature=0.0)
llm_writer = LLM(model='ollama/glm-4.7-flash', base_url='http://localhost:11434', temperature=0.2)

@CrewBase
class TechAnalysisCrew():
    """TechAnalysis crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[search_tool],
            llm=llm_lite,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def sre_auditor(self) -> Agent:
        return Agent(
            config=self.agents_config['sre_auditor'],
            llm=llm_lite,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'],
            llm=llm_writer,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['fact_checker'],
            llm=llm_validator,
            allow_delegation=False,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config['research_task'])

    @task
    def audit_task(self) -> Task:
        return Task(
            config=self.tasks_config['audit_task'],
            context=[self.research_task()]
        )

    @task
    def write_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_task'],
            context=[self.research_task(), self.audit_task()]
        )

    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['validation_task'],
            context=[self.research_task(), self.write_task()],
            output_file='guia_implementacao_pratico.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )