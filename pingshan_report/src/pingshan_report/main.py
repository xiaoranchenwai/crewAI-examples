#!/usr/bin/env python
import asyncio
from typing import Dict, List
from datetime import datetime

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from pingshan_report.crews.data_analysis_crew.data_analysis_crew import (
    DataAnalysisCrew,
)
from pingshan_report.crews.visualization_crew.visualization_crew import (
    VisualizationCrew,
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
    district_chart: ChartData = None
    ev_violations_chart: ChartData = None
    garbage_stats_chart: ChartData = None
    garbage_sources_chart: ChartData = None
    
    # Report sections
    section_1: ReportSection = None
    section_2: ReportSection = None
    section_3: ReportSection = None
    section_4: ReportSection = None
    
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
            tasks=[viz_crew.create_district_chart],
            inputs={"district_data": self.state.district_stats}
        )
        # 从任务输出列表中提取结果
        if hasattr(district_chart_result, 'tasks_output') and len(district_chart_result.tasks_output) > 0:
            if hasattr(district_chart_result.tasks_output[0], 'pydantic'):
                self.state.district_chart = district_chart_result.tasks_output[0].pydantic
        
        # EV violations chart
        ev_chart_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_ev_violations_chart],
            inputs={"communities": self.state.ev_violations}
        )
        if hasattr(ev_chart_result, 'tasks_output') and len(ev_chart_result.tasks_output) > 0:
            if hasattr(ev_chart_result.tasks_output[0], 'pydantic'):
                self.state.ev_violations_chart = ev_chart_result.tasks_output[0].pydantic
        
        # Garbage stats chart
        garbage_chart_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_garbage_stats_chart],
            inputs={"community_data": self.state.garbage_stats}
        )
        if hasattr(garbage_chart_result, 'tasks_output') and len(garbage_chart_result.tasks_output) > 0:
            if hasattr(garbage_chart_result.tasks_output[0], 'pydantic'):
                self.state.garbage_stats_chart = garbage_chart_result.tasks_output[0].pydantic
        
        # Garbage sources chart
        sources_chart_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_garbage_sources_chart],
            inputs={"source_data": self.state.garbage_sources}
        )
        if hasattr(sources_chart_result, 'tasks_output') and len(sources_chart_result.tasks_output) > 0:
            if hasattr(sources_chart_result.tasks_output[0], 'pydantic'):
                self.state.garbage_sources_chart = sources_chart_result.tasks_output[0].pydantic
        
        print("Visualizations created")

    @listen(create_visualizations)
    async def write_report_sections(self):
        print("Writing Report Sections")
        
        viz_crew = VisualizationCrew()
        interpretation = self.state.data_interpretation
        
        # Write section 1
        section1_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_1],
            inputs={
                "district_data": self.state.district_stats,
                "chart_data": self.state.district_chart,
                "interpretation": interpretation
            }
        )
        if hasattr(section1_result, 'tasks_output') and len(section1_result.tasks_output) > 0:
            if hasattr(section1_result.tasks_output[0], 'pydantic'):
                self.state.section_1 = section1_result.tasks_output[0].pydantic
        
        # Write section 2
        section2_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_2],
            inputs={
                "communities": self.state.ev_violations,
                "chart_data": self.state.ev_violations_chart,
                "interpretation": interpretation
            }
        )
        if hasattr(section2_result, 'tasks_output') and len(section2_result.tasks_output) > 0:
            if hasattr(section2_result.tasks_output[0], 'pydantic'):
                self.state.section_2 = section2_result.tasks_output[0].pydantic
        
        # Write section 3
        section3_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_3],
            inputs={
                "community_data": self.state.garbage_stats,
                "chart_data": self.state.garbage_stats_chart,
                "interpretation": interpretation
            }
        )
        if hasattr(section3_result, 'tasks_output') and len(section3_result.tasks_output) > 0:
            if hasattr(section3_result.tasks_output[0], 'pydantic'):
                self.state.section_3 = section3_result.tasks_output[0].pydantic
        
        # Write section 4
        section4_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_4],
            inputs={
                "source_data": self.state.garbage_sources,
                "chart_data": self.state.garbage_sources_chart,
                "interpretation": interpretation
            }
        )
        if hasattr(section4_result, 'tasks_output') and len(section4_result.tasks_output) > 0:
            if hasattr(section4_result.tasks_output[0], 'pydantic'):
                self.state.section_4 = section4_result.tasks_output[0].pydantic
        
        print("Report sections completed")

    @listen(write_report_sections)
    async def compile_final_report(self):
        print("Compiling Final Report")
        
        viz_crew = VisualizationCrew()
        
        # Compile final report
        final_report_result = viz_crew.crew().kickoff(
            tasks=[viz_crew.compile_final_report],
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