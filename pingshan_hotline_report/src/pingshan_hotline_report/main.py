#!/usr/bin/env python
from typing import List, Optional
from datetime import datetime, timedelta

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from pingshan_hotline_report.crews.data_analysis_crew.data_analysis_crew import DataAnalysisCrew
from pingshan_hotline_report.crews.report_generation_crew.report_generation_crew import ReportGenerationCrew
from pingshan_hotline_report.types import MonthlyReport, ReportSection, ChartData


class ReportState(BaseModel):
    """State management for the report generation flow"""
    id: str = "pingshan_hotline_report"
    title: str = "坪山热线系统月度分析报告"
    month: str = ""
    year: str = ""
    report_date: str = ""
    report_sections: List[ReportSection] = []
    sql_results: dict = {}
    chart_data: List[ChartData] = []
    start_date: str = ""
    end_date: str = ""
    report: Optional[MonthlyReport] = None


class PingshanHotlineReportFlow(Flow[ReportState]):
    """Flow for generating monthly reports for the Pingshan Hotline System"""
    initial_state = ReportState

    @start()
    def analyze_hotline_data(self):
        """Start the data analysis crew to analyze the hotline data"""
        print(f"开始进行热线数据分析 - {self.state.month}月 {self.state.year}年")
        
        # 直接执行同步代码，不使用异步
        output = DataAnalysisCrew().crew().kickoff(inputs={
            "month": self.state.month,
            "year": self.state.year,
            "start_date": self.state.start_date,
            "end_date": self.state.end_date,
        })

        # Store SQL query results and chart data for use in report generation
        # self.state.sql_results = output.get("sql_results", {})
        # self.state.chart_data = output.get("chart_data", [])
        
        self.state.sql_results = output.tasks_output[0].raw
        self.state.chart_data = output.tasks_output[1].raw
        
        #print(f"数据分析完成，获取到 {len(self.state.chart_data)} 个图表")
        return self.state.sql_results

    @listen(analyze_hotline_data)
    def generate_report(self):
        """Generate the monthly report based on the analyzed data"""
        print("正在生成月度报告...")
        
        # 直接执行同步代码，不使用异步
        output = ReportGenerationCrew().crew().kickoff(inputs={
            "month": self.state.month,
            "year": self.state.year,
            "report_date": self.state.report_date,
            "sql_results": self.state.sql_results,
            "chart_data": self.state.chart_data,
        })
        
        # 解析输出结果
        interpret_data_output = output.tasks_output[0].raw
        report_output = output.tasks_output[1].raw
        
        # 创建报告章节
        # 假设 report_output 包含了一个结构化的报告数据
        # 需要将其转换为 ReportSection 对象列表
        self.state.report_sections = []
        
        # 这里需要根据实际输出格式解析报告内容
        # 示例：假设 report_output 是一个包含各章节的字典
        if isinstance(report_output, dict) and "sections" in report_output:
            for section in report_output["sections"]:
                # 确保每个章节都有标题和内容
                if "title" in section and "content" in section:
                    charts = []
                    if "charts" in section and section["charts"]:
                        for chart_data in section["charts"]:
                            charts.append(ChartData(**chart_data))
                    
                    self.state.report_sections.append(
                        ReportSection(
                            title=section["title"],
                            content=section["content"],
                            charts=charts
                        )
                    )
        
        # 如果输出不是预期的格式，创建一个默认章节
        if not self.state.report_sections:
            self.state.report_sections = [
                ReportSection(
                    title="报告内容",
                    content=str(report_output),
                    charts=[]
                )
            ]
        
        # 获取报告摘要
        summary = ""
        if isinstance(interpret_data_output, dict) and "summary" in interpret_data_output:
            summary = interpret_data_output["summary"]
        else:
            # 如果没有找到摘要，使用默认文本
            summary = "这是一份坪山热线系统的月度分析报告，包含了系统运行情况的关键指标和分析。"
        
        # 创建完整报告
        self.state.report = MonthlyReport(
            title=f"{self.state.year}年{self.state.month}月坪山热线系统分析报告",
            month=self.state.month,
            year=self.state.year,
            summary=summary,
            sections=self.state.report_sections,
            creation_date=datetime.now()
        )
        
        print(f"报告生成完成: {self.state.report.title}")
        return self.state.report

    @listen(generate_report)
    def save_report(self):
        """Save the generated report to a markdown file"""
        print("正在保存月度报告...")
        
        # Combine all sections into a single markdown string
        report_content = f"# {self.state.report.title}\n\n"
        report_content += f"生成日期: {self.state.report.creation_date.strftime('%Y-%m-%d')}\n\n"
        report_content += f"## 摘要\n\n{self.state.report.summary}\n\n"
        
        # Add each section with its charts
        for section in self.state.report.sections:
            report_content += f"## {section.title}\n\n"
            report_content += f"{section.content}\n\n"
            
            # Add charts if available
            if section.charts:
                for chart in section.charts:
                    report_content += f"### {chart.title}\n\n"
                    if chart.chart_url:
                        report_content += f"![{chart.title}]({chart.chart_url})\n\n"
        
        # Create the filename
        filename = f"./坪山热线系统分析报告_{self.state.year}年{self.state.month}月.md"
        
        # Save the report to a file
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report_content)
            
        print(f"报告已保存为: {filename}")
        return filename


def kickoff(month=None, year=None):
    """Start the report generation flow with the given month and year"""
    if not month:
        # Default to previous month if not specified
        current_date = datetime.now()
        if current_date.month == 1:
            month = "12"
            year = str(current_date.year - 1)
        else:
            month = str(current_date.month - 1)
            year = str(current_date.year)
    
    if not year:
        year = str(datetime.now().year)
    
    # Calculate the start and end dates for the selected month
    month_int = int(month)
    year_int = int(year)
    
    # First day of the month
    start_date = datetime(year_int, month_int, 1).strftime('%Y-%m-%d')
    
    # Last day of the month
    if month_int == 12:
        end_date = datetime(year_int + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year_int, month_int + 1, 1) - timedelta(days=1)
    end_date = end_date.strftime('%Y-%m-%d')
    
    # Current date for the report
    report_date = datetime.now().strftime('%Y-%m-%d')
    
    # Initialize the flow
    flow = PingshanHotlineReportFlow()
    
    # Update the state with our calculated values
    flow.state.month = month
    flow.state.year = year
    flow.state.report_date = report_date
    flow.state.start_date = start_date
    flow.state.end_date = end_date
    
    # Start the flow synchronously
    flow.kickoff()


def plot():
    """Generate and plot the flow diagram"""
    flow = PingshanHotlineReportFlow()
    flow.plot()


if __name__ == "__main__":
    # You can specify month and year as command-line arguments
    # For now, we'll use the default (previous month)
    kickoff()