from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

from parking_strategy_flow.types import ResearchData


@CrewBase
class ResearchCrew:
    """Parking Strategy Research Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b",api_key="none",base_url="http://10.250.2.26:8004/v1")

    @agent
    def market_researcher(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["market_researcher"],
            tools=[search_tool],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def user_analyst(self) -> Agent:
        search_tool = SerperDevTool()
        return Agent(
            config=self.agents_config["user_analyst"],
            tools=[search_tool],
            llm=self.llm,
            verbose=True,
        )

    @task
    def analyze_market(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_market"],
        )

    @task
    def analyze_user_behavior(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_user_behavior"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            output_pydantic=ResearchData,
        )