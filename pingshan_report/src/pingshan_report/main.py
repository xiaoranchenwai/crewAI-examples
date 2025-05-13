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
        
        # Extract the district event statistics
        district_stats = output.get("district_event_stats", {})
        if district_stats and hasattr(district_stats, "district_data"):
            self.state.district_stats = district_stats.district_data
        
        # Extract electric vehicle violations
        ev_violations = output.get("electric_vehicle_violations", {})
        if ev_violations and hasattr(ev_violations, "communities"):
            self.state.ev_violations = ev_violations.communities
        
        # Extract garbage exposure statistics
        garbage_stats = output.get("garbage_exposure_stats", {})
        if garbage_stats and hasattr(garbage_stats, "community_data"):
            self.state.garbage_stats = garbage_stats.community_data
        
        # Extract garbage sources
        garbage_sources = output.get("garbage_sources", {})
        if garbage_sources and hasattr(garbage_sources, "source_data"):
            self.state.garbage_sources = garbage_sources.source_data
        
        # Extract interpretation
        self.state.data_interpretation = output.get("interpret_results", "")
        
        print("Data Analysis completed")
        return output

    @listen(run_data_analysis)
    async def create_visualizations(self):
        print("Creating Visualizations")
        
        # Create charts for all analysis results
        viz_crew = VisualizationCrew()
        
        # District events chart
        district_chart = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_district_chart],
            inputs={"district_data": self.state.district_stats}
        )
        self.state.district_chart = district_chart.get("create_district_chart")
        
        # EV violations chart
        ev_chart = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_ev_violations_chart],
            inputs={"communities": self.state.ev_violations}
        )
        self.state.ev_violations_chart = ev_chart.get("create_ev_violations_chart")
        
        # Garbage stats chart
        garbage_chart = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_garbage_stats_chart],
            inputs={"community_data": self.state.garbage_stats}
        )
        self.state.garbage_stats_chart = garbage_chart.get("create_garbage_stats_chart")
        
        # Garbage sources chart
        sources_chart = viz_crew.crew().kickoff(
            tasks=[viz_crew.create_garbage_sources_chart],
            inputs={"source_data": self.state.garbage_sources}
        )
        self.state.garbage_sources_chart = sources_chart.get("create_garbage_sources_chart")
        
        print("Visualizations created")

    @listen(create_visualizations)
    async def write_report_sections(self):
        print("Writing Report Sections")
        
        viz_crew = VisualizationCrew()
        interpretation = self.state.data_interpretation
        
        # Write section 1
        section1 = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_1],
            inputs={
                "district_data": self.state.district_stats,
                "chart_data": self.state.district_chart,
                "interpretation": interpretation
            }
        )
        self.state.section_1 = section1.get("write_report_section_1")
        
        # Write section 2
        section2 = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_2],
            inputs={
                "communities": self.state.ev_violations,
                "chart_data": self.state.ev_violations_chart,
                "interpretation": interpretation
            }
        )
        self.state.section_2 = section2.get("write_report_section_2")
        
        # Write section 3
        section3 = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_3],
            inputs={
                "community_data": self.state.garbage_stats,
                "chart_data": self.state.garbage_stats_chart,
                "interpretation": interpretation
            }
        )
        self.state.section_3 = section3.get("write_report_section_3")
        
        # Write section 4
        section4 = viz_crew.crew().kickoff(
            tasks=[viz_crew.write_report_section_4],
            inputs={
                "source_data": self.state.garbage_sources,
                "chart_data": self.state.garbage_sources_chart,
                "interpretation": interpretation
            }
        )
        self.state.section_4 = section4.get("write_report_section_4")
        
        print("Report sections completed")

    @listen(write_report_sections)
    async def compile_final_report(self):
        print("Compiling Final Report")
        
        viz_crew = VisualizationCrew()
        
        # Compile final report
        final_report = viz_crew.crew().kickoff(
            tasks=[viz_crew.compile_final_report],
            inputs={
                "section_1": self.state.section_1,
                "section_2": self.state.section_2,
                "section_3": self.state.section_3,
                "section_4": self.state.section_4,
            }
        )
        self.state.final_report = final_report.get("compile_final_report")
        
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