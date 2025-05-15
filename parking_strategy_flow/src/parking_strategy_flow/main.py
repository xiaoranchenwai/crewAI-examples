#!/usr/bin/env python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from parking_strategy_flow.crews.research_crew.research_crew import ResearchCrew
from parking_strategy_flow.crews.strategy_crew.strategy_crew import StrategyCrew
from parking_strategy_flow.types import ResearchData, PricingStrategy


class ParkingStrategyState(BaseModel):
    id: str = "1"
    question: str = "国家海洋博物馆停车场应如何制定动态调价策略？"
    research_data: ResearchData = None
    pricing_strategy: PricingStrategy = None


class ParkingStrategyFlow(Flow[ParkingStrategyState]):
    initial_state = ParkingStrategyState

    @start()
    def conduct_research(self):
        print("开始进行停车场动态调价策略研究")
        output = (
            ResearchCrew()
            .crew()
            .kickoff(inputs={"question": self.state.question, "goal": "为国家海洋博物馆停车场制定科学有效的动态调价策略"})
        )

        self.state.research_data = ResearchData(
            market_analysis=output["market_analysis"],
            user_behavior=output["user_behavior"],
            pricing_models=output["pricing_models"],
            case_studies=output["case_studies"]
        )
        
        print("研究完成，获得市场和用户行为分析结果")
        return self.state.research_data

    @listen(conduct_research)
    async def develop_strategy(self):
        print("开始制定停车场动态调价策略")
        
        output = (
            StrategyCrew()
            .crew()
            .kickoff(
                inputs={
                    "question": self.state.question,
                    "goal": "为国家海洋博物馆停车场制定科学有效的动态调价策略",
                    "market_analysis": self.state.research_data.market_analysis,
                    "user_behavior": self.state.research_data.user_behavior,
                    "pricing_models": self.state.research_data.pricing_models,
                    "case_studies": self.state.research_data.case_studies,
                }
            )
        )

        self.state.pricing_strategy = PricingStrategy(
            pricing_strategy=output["pricing_strategy"],
            justification=output["justification"],
            risk_control=output["risk_control"],
            implementation=output["implementation"],
            case_references=output["case_references"]
        )
        
        print("策略制定完成，生成最终报告")
        
        # 生成并保存最终报告
        report = self._generate_final_report()
        filename = "./停车场动态调价策略报告.md"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(report)
            
        print(f"报告已保存至 {filename}")
        return report
        
    def _generate_final_report(self):
        """生成最终报告"""
        if not self.state.pricing_strategy:
            return "策略尚未生成"
            
        report = f"""# 国家海洋博物馆停车场动态调价策略

## 一、调价策略与执行方案
{self.state.pricing_strategy.pricing_strategy}

## 二、判定理由与数据支撑
{self.state.pricing_strategy.justification}

## 三、风险控制措施
{self.state.pricing_strategy.risk_control}

## 四、实施步骤
{self.state.pricing_strategy.implementation}

## 五、同类案例参考
{self.state.pricing_strategy.case_references}

总结：国家海洋博物馆车场可通过"分时分区定价+用户分层权益+数据动态校准"实现收益与体验双优化，需配套风险熔断机制与用户沟通策略，确保商业目标与社会效益平衡。
"""
        return report


def kickoff():
    parking_strategy_flow = ParkingStrategyFlow()
    parking_strategy_flow.kickoff()


def plot():
    parking_strategy_flow = ParkingStrategyFlow()
    parking_strategy_flow.plot()


if __name__ == "__main__":
    kickoff()