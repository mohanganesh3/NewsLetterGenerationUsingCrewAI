from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from newsletter_gen.tools.research import get_tools
from datetime import datetime
import streamlit as st
from typing import Union, List, Tuple, Dict
from langchain_core.agents import AgentFinish
import json
from langchain_google_genai import ChatGoogleGenerativeAI
import os


@CrewBase
class NewsletterGenCrew:
    """NewsletterGen crew"""


    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def llm(self):
        #llm = ChatAnthropic(model_name="claude-3-sonnet-20240229", max_tokens=4096)
        #groq_api_key=os.getenv('GROQ_API_KEY')
        #llm=ChatGroq(groq_api_key=groq_api_key,
        #     model_name="Llama3-8b-8192")
        # llm = ChatGroq(model="mixtral-8x7b-32768")
        
        # Using Google Gemini API - Free tier with Gemini 2.0 Flash-Lite (most cost-effective)
        google_api_key = os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=google_api_key,
            temperature=0.7
        )

        return llm

    def step_callback(
        self,
        agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish],
        agent_name,
        *args,
    ):
        with st.chat_message("AI"):
            # Try to parse the output if it is a JSON string
            if isinstance(agent_output, str):
                try:
                    agent_output = json.loads(agent_output)
                except json.JSONDecodeError:
                    pass

            if isinstance(agent_output, list) and all(
                isinstance(item, tuple) for item in agent_output
            ):

                for action, description in agent_output:
                    # Print attributes based on assumed structure
                    st.write(f"Agent Name: {agent_name}")
                    st.write(f"Tool used: {getattr(action, 'tool', 'Unknown')}")
                    st.write(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}")
                    st.write(f"{getattr(action, 'log', 'Unknown')}")
                    with st.expander("Show observation"):
                        st.markdown(f"Observation\n\n{description}")

            # Check if the output is a dictionary as in the second case
            elif isinstance(agent_output, AgentFinish):
                st.write(f"Agent Name: {agent_name}")
                output = agent_output.return_values
                st.write(f"I finished my task:\n{output['output']}")

            # Handle unexpected formats
            else:
                st.write(type(agent_output))
                st.write(agent_output)

    @agent
    def researcher(self) -> Agent:
        cfg = self.agents_config["researcher"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=get_tools(),
            verbose=True,
            llm=self.llm(),
        )

    @agent
    def editor(self) -> Agent:
        cfg = self.agents_config["editor"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            verbose=True,
            tools=get_tools(),
            llm=self.llm(),
        )

    @agent
    def designer(self) -> Agent:
        cfg = self.agents_config["designer"]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            verbose=True,
            allow_delegation=False,
            llm=self.llm(),
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_research_task.md",
        )

    @task
    def edit_task(self) -> Task:
        return Task(
            config=self.tasks_config["edit_task"],
            agent=self.editor(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_edit_task.md",
        )

    @task
    def newsletter_task(self) -> Task:
        return Task(
            config=self.tasks_config["newsletter_task"],
            agent=self.designer(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_newsletter_task.html",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NewsletterGen crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=2,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
