#!/usr/bin/env python
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pydantic import Field
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from pingshan_report.crews.data_analysis_crew.data_analysis_crew import (
    DataAnalysisCrew,
)
from pingshan_report.crews.visualization_crew.visualization_crew import (
    VisualizationCrew,
)
from pingshan_report.crews.report_writing_crew.report_writing_crew import (
    ReportWritingCrew,
)
from pingshan_report.crews.report_writing_final.report_writing_final import (
    ReportWritingFinalCrew,
)
from pingshan_report.types import (
    DistrictEventStats,
    ElectricVehicleViolations,
    GarbageExposureStats,
    GarbageSourceStats,
    ChartData,
    ReportSection,
    PingshanReport,
)


class ReportState(BaseModel):
    id: str = "pingshan_report"
    title: str = "坪山热线报告"
    
    # Analysis results
    district_stats: Dict = {}
    ev_violations: List = []
    garbage_stats: Dict = {}
    garbage_sources: Dict = {}
    data_interpretation: str = ""
    
    # Chart data
    #district_chart: ChartData = None
    district_chart: Dict[str, Any] = Field(default_factory=dict)
    ev_violations_chart: Dict[str, Any] = Field(default_factory=dict)
    garbage_stats_chart: Dict[str, Any] = Field(default_factory=dict)
    garbage_sources_chart: Dict[str, Any] = Field(default_factory=dict)
    
    # Report sections
    #section_1: ReportSection = None
    section_1: Dict[str, Any] = Field(default_factory=dict)
    section_2: Dict[str, Any] = Field(default_factory=dict)
    section_3: Dict[str, Any] = Field(default_factory=dict)
    section_4: Dict[str, Any] = Field(default_factory=dict)
    
    # Final report
    final_report: PingshanReport = None


class PingshanHotlineReportFlow(Flow[ReportState]):
    initial_state = ReportState

    @start()
    def run_data_analysis(self):
        print("Starting Data Analysis Crew")
        
        # Run the data analysis crew to get all query results
        output = DataAnalysisCrew().crew().kickoff()
        
        # 检查任务输出结果存在
        if hasattr(output, 'tasks_output') and output.tasks_output:
            # 任务输出是一个列表，每个任务的结果按索引访问
            
            # 提取第1个任务：district_event_stats的结果
            if len(output.tasks_output) > 0 and hasattr(output.tasks_output[0], 'pydantic'):
                district_stats = output.tasks_output[0].pydantic
                if hasattr(district_stats, "district_data"):
                    self.state.district_stats = district_stats.district_data
            
            # 提取第2个任务：electric_vehicle_violations的结果
            if len(output.tasks_output) > 1 and hasattr(output.tasks_output[1], 'pydantic'):
                ev_violations = output.tasks_output[1].pydantic
                if hasattr(ev_violations, "communities"):
                    self.state.ev_violations = ev_violations.communities
            
            # 提取第3个任务：garbage_exposure_stats的结果
            if len(output.tasks_output) > 2 and hasattr(output.tasks_output[2], 'pydantic'):
                garbage_stats = output.tasks_output[2].pydantic
                if hasattr(garbage_stats, "community_data"):
                    self.state.garbage_stats = garbage_stats.community_data
            
            # 提取第4个任务：garbage_sources的结果
            if len(output.tasks_output) > 3 and hasattr(output.tasks_output[3], 'pydantic'):
                garbage_sources = output.tasks_output[3].pydantic
                if hasattr(garbage_sources, "source_data"):
                    self.state.garbage_sources = garbage_sources.source_data
            
            # 提取第5个任务：interpret_results的结果（可能没有pydantic模型）
            if len(output.tasks_output) > 4:
                # 对于没有pydantic模型的任务，使用raw或其他可用字段
                if hasattr(output.tasks_output[4], 'raw'):
                    self.state.data_interpretation = output.tasks_output[4].raw
                else:
                    self.state.data_interpretation = str(output.tasks_output[4])
        
        print("Data Analysis completed")
        return output

    @listen(run_data_analysis)
    async def create_visualizations(self):
        print("Creating Visualizations")
        
        # Create charts for all analysis results
        viz_crew = VisualizationCrew()
        
        # District events chart
        district_chart_result = viz_crew.crew().kickoff(
            inputs={"district_data": self.state.district_stats,
                    "communities": self.state.ev_violations,
                    "community_data": self.state.garbage_stats,
                    "source_data": self.state.garbage_sources}
        )
        # 从任务输出列表中提取结果
        if hasattr(district_chart_result, 'tasks_output') and len(district_chart_result.tasks_output) > 0:
            if hasattr(district_chart_result.tasks_output[0], 'pydantic'):
                self.state.district_chart['chart_url'] = district_chart_result.tasks_output[0].pydantic.chart_url
                self.state.district_chart['title'] = district_chart_result.tasks_output[0].pydantic.title
                self.state.district_chart['description'] = district_chart_result.tasks_output[0].pydantic.description
        
        # EV violations chart
        # ev_chart_result = viz_crew.crew().kickoff(
        #     inputs={"communities": self.state.ev_violations}
        # )
        if hasattr(district_chart_result, 'tasks_output') and len(district_chart_result.tasks_output) > 0:
            if hasattr(district_chart_result.tasks_output[1], 'pydantic'):
                self.state.ev_violations_chart['chart_url']  = district_chart_result.tasks_output[1].pydantic.chart_url
                self.state.ev_violations_chart['title'] = district_chart_result.tasks_output[1].pydantic.title
                self.state.ev_violations_chart['description'] = district_chart_result.tasks_output[1].pydantic.description
        
        # Garbage stats chart
        # garbage_chart_result = viz_crew.crew().kickoff(
        #     inputs={"community_data": self.state.garbage_stats}
        # )
        if hasattr(district_chart_result, 'tasks_output') and len(district_chart_result.tasks_output) > 0:
            if hasattr(district_chart_result.tasks_output[2], 'pydantic'):
                self.state.garbage_stats_chart['chart_url']  = district_chart_result.tasks_output[2].pydantic.chart_url
                self.state.garbage_stats_chart['title'] = district_chart_result.tasks_output[2].pydantic.title
                self.state.garbage_stats_chart['description'] = district_chart_result.tasks_output[2].pydantic.description
        
        # Garbage sources chart
        # sources_chart_result = viz_crew.crew().kickoff(
        #     inputs={"source_data": self.state.garbage_sources}
        # )
        if hasattr(district_chart_result, 'tasks_output') and len(district_chart_result.tasks_output) > 0:
            if hasattr(district_chart_result.tasks_output[3], 'pydantic'):
                self.state.garbage_sources_chart['chart_url']  = district_chart_result.tasks_output[3].pydantic.chart_url
                self.state.garbage_sources_chart['title'] = district_chart_result.tasks_output[3].pydantic.title
                self.state.garbage_sources_chart['description'] = district_chart_result.tasks_output[3].pydantic.description
        
        print("Visualizations created")


    @listen(create_visualizations)
    async def write_report_sections(self):
        print("Writing Report Sections")
        
        report_crew = ReportWritingCrew()
        interpretation = self.state.data_interpretation
        
        # Write section 1
        section1_result = report_crew.crew().kickoff(
            inputs={
                "district_data": self.state.district_stats,
                "district_data_chart_data": self.state.district_chart,
                "interpretation": interpretation,
                 "communities": self.state.ev_violations,
                "communities_chart_data": self.state.ev_violations_chart,
                 "community_data": self.state.garbage_stats,
                "community_data_chart_data": self.state.garbage_stats_chart,
                 "source_data": self.state.garbage_sources,
                "source_data_chart_data": self.state.garbage_sources_chart
            }
        )
        if hasattr(section1_result, 'tasks_output') and len(section1_result.tasks_output) > 0:
            if hasattr(section1_result.tasks_output[0], 'pydantic'):
                self.state.section_1['title'] = section1_result.tasks_output[0].pydantic.title
                self.state.section_1['content'] = section1_result.tasks_output[0].pydantic.content
                self.state.section_1['chart_data']=self.state.district_chart
        
        if hasattr(section1_result, 'tasks_output') and len(section1_result.tasks_output) > 0:
            if hasattr(section1_result.tasks_output[1], 'pydantic'):
                self.state.section_2['title'] = section1_result.tasks_output[1].pydantic.title
                self.state.section_2['content'] = section1_result.tasks_output[1].pydantic.content
                self.state.section_2['chart_data'] = self.state.ev_violations_chart
        
    
        if hasattr(section1_result, 'tasks_output') and len(section1_result.tasks_output) > 0:
            if hasattr(section1_result.tasks_output[2], 'pydantic'):
                self.state.section_3['title'] = section1_result.tasks_output[2].pydantic.title
                self.state.section_3['content'] = section1_result.tasks_output[2].pydantic.content
                self.state.section_3['chart_data'] = self.state.garbage_stats_chart
        
        if hasattr(section1_result, 'tasks_output') and len(section1_result.tasks_output) > 0:
            if hasattr(section1_result.tasks_output[3], 'pydantic'):
                self.state.section_4['title'] = section1_result.tasks_output[3].pydantic.title
                self.state.section_4['content'] = section1_result.tasks_output[3].pydantic.content
                self.state.section_4['chart_data'] = self.state.garbage_sources_chart
        
        print("Report sections completed")

    @listen(write_report_sections)
    async def compile_final_report(self):
        print("Compiling Final Report")
        
        report_crew = ReportWritingFinalCrew()
        
        # Compile final report
        final_report_result = report_crew.crew().kickoff(
            inputs={
                "section_1": self.state.section_1,
                "section_2": self.state.section_2,
                "section_3": self.state.section_3,
                "section_4": self.state.section_4,
            }
        )
        if hasattr(final_report_result, 'tasks_output') and len(final_report_result.tasks_output) > 0:
            if hasattr(final_report_result.tasks_output[0], 'pydantic'):
                self.state.final_report = final_report_result.tasks_output[0].pydantic
        
        # Save the report to a file
        report_date = datetime.now().strftime("%Y%m%d")
        filename = f"坪山热线报告_{report_date}.md"
        
        with open(filename, "w", encoding="utf-8") as file:
            # Write sections
            if self.state.final_report and hasattr(self.state.final_report, "sections"):
                for section in self.state.final_report.sections:
                    file.write(f"# {section.title}\n\n")
                    file.write(f"{section.content}\n\n")
                    if section.chart_data:
                        file.write(f"![{section.chart_data.title}]({section.chart_data.chart_url})\n\n")
                        file.write(f"*{section.chart_data.description}*\n\n")
        
        print(f"Final report saved as {filename}")
        return self.state.final_report


def kickoff():
    report_flow = PingshanHotlineReportFlow()
    report_flow.kickoff()


def plot():
    report_flow = PingshanHotlineReportFlow()
    report_flow.plot()


if __name__ == "__main__":
    kickoff()