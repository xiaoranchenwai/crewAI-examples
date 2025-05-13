from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

from pingshan_report.types import (
    DistrictEventStats,
    ElectricVehicleViolations,
    GarbageExposureStats,
    GarbageSourceStats,
)


@CrewBase
class DataAnalysisCrew:
    """Data Analysis Crew for Pingshan Hotline Report"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b", api_key="none", base_url="http://10.250.2.25:8004/v1")

    @agent
    def sql_analyst(self) -> Agent:
        mysql_serverparams = {"url": "http://10.250.2.23:8030/sse"}
        with MCPServerAdapter(mysql_serverparams) as tools:
            return Agent(
                config=self.agents_config["sql_analyst"],
                tools=[tools[0]],
                llm=self.llm,
                verbose=True,
            )

    @agent
    def data_interpreter(self) -> Agent:
        return Agent(
            config=self.agents_config["data_interpreter"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def district_event_stats(self) -> Task:
        return Task(
            config=self.tasks_config["district_event_stats"],
            output_pydantic=DistrictEventStats,
        )

    @task
    def electric_vehicle_violations(self) -> Task:
        return Task(
            config=self.tasks_config["electric_vehicle_violations"],
            output_pydantic=ElectricVehicleViolations,
        )

    @task
    def garbage_exposure_stats(self) -> Task:
        return Task(
            config=self.tasks_config["garbage_exposure_stats"],
            output_pydantic=GarbageExposureStats,
        )

    @task
    def garbage_sources(self) -> Task:
        return Task(
            config=self.tasks_config["garbage_sources"],
            output_pydantic=GarbageSourceStats,
        )

    @task
    def interpret_results(self) -> Task:
        return Task(
            config=self.tasks_config["interpret_results"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Data Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )