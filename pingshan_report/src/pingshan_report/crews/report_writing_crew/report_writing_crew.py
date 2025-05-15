from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from pingshan_report.types import (
    ReportSection,
    PingshanReport,
)


@CrewBase
class ReportWritingCrew:
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
    def write_report_section_1(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_section_1"],
            output_pydantic=ReportSection,
        )

    @task
    def write_report_section_2(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_section_2"],
            output_pydantic=ReportSection,
        )

    @task
    def write_report_section_3(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_section_3"],
            output_pydantic=ReportSection,
        )

    @task
    def write_report_section_4(self) -> Task:
        return Task(
            config=self.tasks_config["write_report_section_4"],
            output_pydantic=ReportSection,
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