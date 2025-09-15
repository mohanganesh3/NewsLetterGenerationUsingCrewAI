import os
from pathlib import Path
import yaml

# Load environment variables
try:
    import streamlit as st
    # Try to get secrets from Streamlit
    try:
        exa_api_key = st.secrets["EXA_API_KEY"]
        google_api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["EXA_API_KEY"] = exa_api_key
        os.environ["GOOGLE_API_KEY"] = google_api_key
    except:
        # Fallback to environment variables
        pass
except ImportError:
    # Not in Streamlit environment
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except:
        pass  # Secrets not configured yet

# Import CrewAI components
from crewai import Agent, Crew, Process, Task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
from langchain_google_genai import ChatGoogleGenerativeAI


class NewsletterGenCrew:
    """Newsletter Generation Crew using CrewAI."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        self.llm = self._get_llm()
        
    def _load_config(self, filename):
        """Load configuration from YAML file."""
        config_path = self.config_dir / filename
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _get_llm(self):
        """Get the configured LLM."""
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=google_api_key,
            convert_system_message_to_human=True
        )
    
    def editor_agent(self):
        """Create the editor agent."""
        agent_config = self.agents_config["editor"]
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            llm=self.llm,
            max_iter=5,
            memory=True,
            verbose=True,
            allow_delegation=False
        )
    
    def news_researcher_agent(self):
        """Create the news researcher agent."""
        agent_config = self.agents_config["news_researcher"]
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            llm=self.llm,
            max_iter=5,
            memory=True,
            verbose=True,
            allow_delegation=False
        )
    
    def newsletter_compiler_agent(self):
        """Create the newsletter compiler agent."""
        agent_config = self.agents_config["newsletter_compiler"]
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            llm=self.llm,
            max_iter=5,
            memory=True,
            verbose=True,
            allow_delegation=False
        )
    
    def research_task(self):
        """Create the research task."""
        task_config = self.tasks_config["research_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.news_researcher_agent()
        )
    
    def edit_task(self):
        """Create the edit task."""
        task_config = self.tasks_config["edit_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.editor_agent()
        )
    
    def newsletter_task(self):
        """Create the newsletter task."""
        task_config = self.tasks_config["newsletter_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.newsletter_compiler_agent(),
            output_file='logs/newsletter.md'
        )
    
    def crew(self):
        """Create and return the crew."""
        return Crew(
            agents=[
                self.news_researcher_agent(),
                self.editor_agent(),
                self.newsletter_compiler_agent()
            ],
            tasks=[
                self.research_task(),
                self.edit_task(),
                self.newsletter_task()
            ],
            process=Process.sequential,
            verbose=True
        )
    
    def kickoff(self, inputs):
        """Execute the crew with given inputs."""
        return self.crew().kickoff(inputs=inputs)
    
    def validate_env_vars(self):
        """Validate that required environment variables are set."""
        required_vars = ["EXA_API_KEY", "GOOGLE_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
