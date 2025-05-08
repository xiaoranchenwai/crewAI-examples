from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter

from pingshan_hotline_report.types import ChartData


@CrewBase
class DataAnalysisCrew:
    """Data Analysis Crew for Pingshan Hotline System"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = ChatOpenAI(model="openai/qwen3-235b", api_key="none", base_url="http://10.250.2.26:8004/v1")

    @agent
    def data_analyst(self) -> Agent:
        """Create the data analyst agent with MySQL query tool"""
        # Set up MySQL MCP server adapter
        #mysql_serverparams = {url="http://10.250.2.23:8030/sse"}
        mysql_serverparams = {"url": "http://10.250.2.23:8030/sse"}
        with MCPServerAdapter(mysql_serverparams) as tools:
            return Agent(
                config=self.agents_config["data_analyst"],
                tools=tools,
                llm=self.llm,
                verbose=True,
            )

    @agent
    def visualization_expert(self) -> Agent:
        """Create the visualization expert agent with QuickChart tool"""
        # Set up QuickChart MCP server adapter
        #quickchart_serverparams = StdioServerParameters(url="http://10.250.2.23:8005/quickchart-server")
        quickchart_serverparams = {"url": "http://10.250.2.23:8005/quickchart-server"}
        with MCPServerAdapter(quickchart_serverparams) as tools:
            return Agent(
                config=self.agents_config["visualization_expert"],
                tools=tools,
                llm=self.llm,
                verbose=True,
            )

    @task
    def query_hotline_data(self) -> Task:
        """Task for querying hotline data using SQL"""
        return Task(
            config=self.tasks_config["query_hotline_data"],
        )

    @task
    def create_visualizations(self) -> Task:
        """Task for creating visualizations from SQL query results"""
        return Task(
            config=self.tasks_config["create_visualizations"],
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