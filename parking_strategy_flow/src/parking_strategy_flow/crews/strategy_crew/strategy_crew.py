from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI

from parking_strategy_flow.types import PricingStrategy


@CrewBase
class StrategyCrew:
    """Parking Strategy Development Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-32b",api_key="none",base_url="http://10.250.2.25:8004/v1")

    @agent
    def pricing_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["pricing_strategist"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def risk_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_analyst"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def implementation_expert(self) -> Agent:
        return Agent(
            config=self.agents_config["implementation_expert"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def design_pricing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config["design_pricing_strategy"],
        )

    @task
    def assess_risks(self) -> Task:
        return Task(
            config=self.tasks_config["assess_risks"],
        )

    @task
    def design_implementation(self) -> Task:
        return Task(
            config=self.tasks_config["design_implementation"],
            output_pydantic=PricingStrategy
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Strategy Development Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )