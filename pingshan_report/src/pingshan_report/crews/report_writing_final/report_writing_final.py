from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from pingshan_report.types import (
    ReportSection,
    PingshanReport,
)


@CrewBase
class ReportWritingFinalCrew:
    """Report Writing Crew for Pingshan Hotline Report"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b", api_key="none", base_url="http://10.250.2.25:8004/v1")

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["report_writer"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def compile_final_report(self) -> Task:
        return Task(
            config=self.tasks_config["compile_final_report"],
            output_pydantic=PingshanReport,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Report Writing Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )