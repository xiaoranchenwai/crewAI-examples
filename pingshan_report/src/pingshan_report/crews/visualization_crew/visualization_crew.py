from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from crewai_tools import MCPServerAdapter

from pingshan_report.types import (
    ChartData,
)


@CrewBase
class VisualizationCrew:
    """Visualization Crew for Pingshan Hotline Report"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b", api_key="none", base_url="http://10.250.2.25:8004/v1")

    @agent
    def chart_designer(self) -> Agent:
        quickchart_serverparams = {"url": "http://10.250.2.23:8005/quickchart-server"}
        with MCPServerAdapter(quickchart_serverparams) as tools:
            return Agent(
                config=self.agents_config["chart_designer"],
                tools=tools,
                llm=self.llm,
                verbose=True,
            )

    @task
    def create_district_chart(self) -> Task:
        return Task(
            config=self.tasks_config["create_district_chart"],
            output_pydantic=ChartData,
        )

    @task
    def create_ev_violations_chart(self) -> Task:
        return Task(
            config=self.tasks_config["create_ev_violations_chart"],
            output_pydantic=ChartData,
        )

    @task
    def create_garbage_stats_chart(self) -> Task:
        return Task(
            config=self.tasks_config["create_garbage_stats_chart"],
            output_pydantic=ChartData,
        )

    @task
    def create_garbage_sources_chart(self) -> Task:
        return Task(
            config=self.tasks_config["create_garbage_sources_chart"],
            output_pydantic=ChartData,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Visualization Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )