from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from pingshan_hotline_report.types import ReportSection


@CrewBase
class ReportGenerationCrew:
    """Report Generation Crew for Pingshan Hotline System"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b", api_key="none", base_url="http://10.250.2.26:8004/v1")

    @agent
    def data_interpreter(self) -> Agent:
        """Create the data interpreter agent"""
        return Agent(
            config=self.agents_config["data_interpreter"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def report_writer(self) -> Agent:
        """Create the report writer agent"""
        return Agent(
            config=self.agents_config["report_writer"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def interpret_data(self) -> Task:
        """Task for interpreting analyzed data"""
        return Task(
            config=self.tasks_config["interpret_data"],
        )

    @task
    def write_report(self) -> Task:
        """Task for writing the monthly report"""
        return Task(
            config=self.tasks_config["write_report"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Report Generation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )