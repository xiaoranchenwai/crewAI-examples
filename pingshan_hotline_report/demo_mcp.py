from crewai import Agent, Task, Crew, LLM
from crewai_tools import MCPServerAdapter

llm = LLM(model="openai/qwen3-235b",api_base="http://10.250.2.25:8004/v1")

params = {"url": "http://10.250.2.23:8030/sse" }

with MCPServerAdapter(params) as mcptools:

    webagent = Agent(
        role="坪山热线数据分析师",
        goal = '''分析坪山热线系统在2025年4月的数据，提取关键洞察和趋势，
    为月度报告提供数据支持。''',
        backstory = """你是一位专业的数据分析师，擅长从大量数据中提取有价值的信息。
    你的专长是分析热线系统数据，识别模式和趋势，并将复杂数据转化为可理解的见解。
    你将使用SQL查询工具Generate and Execute SQL Query来获取坪山热线系统的数据，并分析这些数据以获得有价值的洞察。""",
        memory = True,
        tools = [mcptools[0]],
        allow_delegation = True,
        llm = llm,
        verbose = True
    )

    webtask = Task(
        description = """
        使用SQL查询工具Generate and Execute SQL Query获取坪山热线系统在 2025年期间的数据，
    并对获取的数据进行初步分析和统计。需要执行的关键查询包括：
    
    1. 按街道名称统计事件数量，并按数量降序排序？
    
    请确保每个查询都有明确的目的，并关注数据的质量和完整性。
        """,
        expected_output='''包含各类SQL查询结果的结构化数据集，以便后续进行可视化和报告生成。''',
        agent = webagent
    )

    crew = Crew(
        agents = [webagent],
        tasks = [webtask],
        verbose = True
    )

    result = crew.kickoff()
    print(result)
