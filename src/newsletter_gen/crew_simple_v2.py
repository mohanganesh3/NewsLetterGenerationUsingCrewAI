from crewai import Agent, Crew, Process, Task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
import streamlit as st
from typing import Union, List, Tuple, Dict
from langchain_core.agents import AgentFinish
import json
import os
import yaml


class NewsletterGenCrew:
    """NewsletterGen crew"""

    def __init__(self):
        # Load configurations
        self.agents_config = self._load_config("src/newsletter_gen/config/agents.yaml")
        self.tasks_config = self._load_config("src/newsletter_gen/config/tasks.yaml")

    def _load_config(self, file_path):
        """Load YAML configuration file"""
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def llm(self):
        """Initialize the Language Model"""
        os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
            max_tokens=4096
        )
        return llm

    def step_callback(self, agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name, *args):
        """Callback function for agent steps in Streamlit"""
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

    def researcher(self) -> Agent:
        """Create the researcher agent"""
        return Agent(
            role=self.agents_config["researcher"]["role"],
            goal=self.agents_config["researcher"]["goal"],
            backstory=self.agents_config["researcher"]["backstory"],
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Research Agent"),
        )

    def editor(self) -> Agent:
        """Create the editor agent"""
        return Agent(
            role=self.agents_config["editor"]["role"],
            goal=self.agents_config["editor"]["goal"],
            backstory=self.agents_config["editor"]["backstory"],
            verbose=True,
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Chief Editor"),
        )

    def designer(self) -> Agent:
        """Create the designer agent"""
        return Agent(
            role=self.agents_config["designer"]["role"],
            goal=self.agents_config["designer"]["goal"],
            backstory=self.agents_config["designer"]["backstory"],
            verbose=True,
            allow_delegation=False,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "HTML Writer"),
        )

    def research_task(self) -> Task:
        """Create the research task"""
        return Task(
            description=self.tasks_config["research_task"]["description"],
            expected_output=self.tasks_config["research_task"]["expected_output"],
            agent=self.researcher(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_research_task.md",
        )

    def edit_task(self) -> Task:
        """Create the edit task"""
        return Task(
            description=self.tasks_config["edit_task"]["description"],
            expected_output=self.tasks_config["edit_task"]["expected_output"],
            agent=self.editor(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_edit_task.md",
        )

    def newsletter_task(self) -> Task:
        """Create the newsletter task"""
        return Task(
            description=self.tasks_config["newsletter_task"]["description"],
            expected_output=self.tasks_config["newsletter_task"]["expected_output"],
            agent=self.designer(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_newsletter_task.html",
        )

    def crew(self) -> Crew:
        """Creates the NewsletterGen crew"""
        return Crew(
            agents=[self.researcher(), self.editor(), self.designer()],
            tasks=[self.research_task(), self.edit_task(), self.newsletter_task()],
            process=Process.sequential,
            verbose=2,
        )
