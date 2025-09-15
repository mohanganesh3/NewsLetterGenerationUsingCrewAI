### 🚀 Live Demo: <a href="https://newslettergenerationusingcrewai-ocw9fz38zcsqr976xqg9h3.streamlit.app/">Open the Streamlit App</a>

# NewsletterGen: Your AI-Powered Newsletter Creation Suite 📰

An end-to-end tutorial to build a production-ready, AI newsletter generator that:
- researches the latest news for any topic,
- curates and edits the findings,
- compiles a polished, email-friendly HTML newsletter — automatically.

This guide explains the architecture, the CrewAI multi-agent orchestration, how the Exa-powered research tools work, and how the Streamlit UI ties everything together. By the end, you’ll be able to modify agents, prompts, tools, and the UI to ship your own bespoke newsletter engine.

---

## Table of Contents
- Motivation and Demo
- How It Works (Big Picture)
- Architecture Overview
- Deep Dive: Key Components with Code
  - Tools: Exa research with resilient retries
  - Crew Orchestration: Agents, Tasks, LLM, and logging
  - Prompts and Specs: agents.yaml and tasks.yaml
  - HTML Template: Email-safe design
  - Streamlit UI: Running the crew interactively
- Run Locally
- Customize and Extend
- Deploy to Streamlit Cloud
- Troubleshooting

---

## Motivation and Demo
If you routinely create weekly or themed newsletters, the tedious parts are always the same: find recent, trustworthy sources; summarize concisely; organize content; and format for email. NewsletterGen automates that workflow.

Live Demo (Streamlit): https://newslettergenerationusingcrewai-ocw9fz38zcsqr976xqg9h3.streamlit.app/

---

## How It Works (Big Picture)
On each run:
1) You provide a topic (and optional personal message)
2) Researcher fetches 1–2 high-signal items using Exa and summarizes them
3) Editor validates links, improves copy, orders items for impact
4) Designer fills a responsive HTML template and returns the final newsletter
5) Each step writes a timestamped artifact to logs/

---

## Architecture Overview
- Orchestrator (CrewAI): Sequential Process with 3 agents
  - Researcher → Editor → Designer
- LLM: Gemini 2.0 Flash-Lite (cost-effective, fast)
- Tools: Exa client with retry/backoff and 1s pacing
- Config: YAML-powered roles, goals, and task prompts
- UI: Streamlit app + command-line entry point

Key paths:
- src/newsletter_gen/crew.py — Crew, Agents, Tasks, LLM config, logging
- src/newsletter_gen/tools/research.py — Exa-powered tools with retries
- src/newsletter_gen/config/agents.yaml — Agent roles/goals/backstories
- src/newsletter_gen/config/tasks.yaml — Task prompts + expected outputs
- src/newsletter_gen/config/newsletter_template.html — Email template
- src/gui/app.py and streamlit_app.py — Streamlit UI
- src/newsletter_gen/main.py — CLI runner

---

## Deep Dive: Key Components with Code

### 1) Tools: Exa research with resilient retries
The Researcher and Editor can call three tools. Each tool uses tenacity for retry, respects Exa rate limits (with 1s sleep), and constrains returned text length.

```python
# src/newsletter_gen/tools/research.py
from langchain_core.tools import BaseTool
from exa_py import Exa
import os
from datetime import datetime, timedelta
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class SearchAndContents(BaseTool):
    name: str = "Search and Contents Tool"
    description: str = (
        "Searches the web for recent news (last week) using Exa API and returns content summaries."
    )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def _run(self, search_query: str) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        one_week_ago = datetime.now() - timedelta(days=7)
        date_cutoff = one_week_ago.strftime("%Y-%m-%d")
        try:
            results = exa.search_and_contents(
                query=search_query,
                use_autoprompt=True,
                start_published_date=date_cutoff,
                text={"include_html_tags": False, "max_characters": 300},
                num_results=2,
            )
            time.sleep(1)  # pacing
            return results
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise  # allow tenacity to retry
            raise Exception(f"Exa API error: {e}")
```

Why this matters:
- The 7-day cutoff keeps content fresh
- Tenacity handles bursty failures; a single 429 won’t kill the run
- Constraining characters forces the model to focus on signal

Similar classes FindSimilar and GetContents follow the same pattern.

---

### 2) Crew Orchestration: Agents, Tasks, LLM, and logging
The Crew is defined with three agents and three tasks. LLM is Gemini by default; every task writes a timestamped artifact to logs/.

```python
# src/newsletter_gen/crew.py (excerpt)
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from newsletter_gen.tools.research import SearchAndContents, FindSimilar, GetContents
from datetime import datetime
import streamlit as st
from typing import Union, List, Tuple, Dict
from langchain_core.agents import AgentFinish
import json
from langchain_google_genai import ChatGoogleGenerativeAI
import os

@CrewBase
class NewsletterGenCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def llm(self):
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7,
        )
        return llm

    def step_callback(self, agent_output: Union[str, List[Tuple[Dict, str]], AgentFinish], agent_name, *args):
        # Streams each tool call / finish into the Streamlit chat panel
        with st.chat_message("AI"):
            if isinstance(agent_output, str):
                try:
                    agent_output = json.loads(agent_output)
                except json.JSONDecodeError:
                    pass
            if isinstance(agent_output, List) and all(isinstance(item, tuple) for item in agent_output):
                for action, description in agent_output:
                    st.write(f"Agent Name: {agent_name}")
                    st.write(f"Tool used: {getattr(action, 'tool', 'Unknown')}")
                    st.write(f"Tool input: {getattr(action, 'tool_input', 'Unknown')}")
                    with st.expander("Show observation"):
                        st.markdown(f"Observation\n\n{description}")
            elif isinstance(agent_output, AgentFinish):
                st.write(f"Agent Name: {agent_name}")
                output = agent_output.return_values
                st.write(f"I finished my task:\n{output['output']}")

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SearchAndContents(), FindSimilar(), GetContents()],
            verbose=True,
            llm=self.llm(),
            step_callback=lambda step: self.step_callback(step, "Research Agent"),
        )

    # editor() and designer() are analogous; designer does not use tools

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.researcher(),
            output_file=f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_research_task.md",
        )
```

Why this matters:
- @CrewBase wires YAML config to Python seamlessly
- step_callback streams intermediate steps into Streamlit so users see progress
- output_file leaves a durable breadcrumb trail for debugging and audits

---

### 3) Prompts and Specs: YAML-driven agents and tasks
You get reproducible behavior and easy edits by keeping roles/goals and prompts in YAML.

```yaml
# src/newsletter_gen/config/agents.yaml (excerpt)
researcher:
  role: Senior Researcher
  goal: Conduct in-depth research to uncover reliable and cutting-edge news about {topic}.
  backstory: >
    You are an experienced journalist with exceptional research skills.
    You always include accurate and complete URLs for every source.
```

```yaml
# src/newsletter_gen/config/tasks.yaml (excerpt)
research_task:
  description: >
    Research the latest news on {topic}. Include only 1–2 relevant articles, summarize concisely (<500 chars), and provide URLs.

    IMPORTANT: When using tools, DO NOT ESCAPE the underscore character "_".
  expected_output: >
    Markdown with 1–2 stories: Title, Summary (<500 chars), URL
```

Designer’s newsletter_task appends your personal message and enforces “return only HTML” so the output is paste-ready for email.

---

### 4) HTML Template: Email-safe design
Responsive, conservative CSS keeps your newsletter legible in common clients.

```html
<!-- src/newsletter_gen/config/newsletter_template.html (excerpt) -->
<div class="personal-message">
  {personal_message}
</div>
<div class="news-item">
  <h2>{news_title}</h2>
  <p>{news_summary}</p>
  <a href="{news_url}" class="read-more">Read More</a>
</div>
```

---

### 5) Streamlit UI: Running the crew interactively
The UI wires text inputs to CrewAI, shows streaming steps, and returns downloadable HTML.

```python
# src/gui/app.py (excerpt)
from newsletter_gen.crew import NewsletterGenCrew

class NewsletterGenUI:
    def load_html_template(self):
        with open("src/newsletter_gen/config/newsletter_template.html", "r") as f:
            return f.read()

    def generate_newsletter(self, topic, personal_message):
        inputs = {
            "topic": topic,
            "personal_message": personal_message,
            "html_template": self.load_html_template(),
        }
        return NewsletterGenCrew().crew().kickoff(inputs=inputs)
```

---

## Run Locally

1) Install
```bash
# Poetry
poetry install
# or pip
pip install -r requirements.txt
```

2) Set env
```bash
export GOOGLE_API_KEY="<your-gemini-api-key>"
export EXA_API_KEY="<your-exa-api-key>"
```

3) Launch
```bash
# CLI
python src/newsletter_gen/main.py

# Streamlit
streamlit run streamlit_app.py
# or
streamlit run src/gui/app.py
```

---

## Customize and Extend
- Add tools: Create new BaseTool classes under src/newsletter_gen/tools and bind them to agents in crew.py
- Change LLM: Swap Gemini for another provider by initializing a different LangChain chat model in llm()
- Change the template: Edit src/newsletter_gen/config/newsletter_template.html to match your brand
- Add agents/tasks: Update YAML files and declare corresponding @agent/@task in crew.py

---

## Deploy to Streamlit Cloud
- Add GOOGLE_API_KEY and EXA_API_KEY to Streamlit Secrets
- The app includes a small sqlite compatibility shim to support Chroma on Debian-based images
- Main module: streamlit_app.py (or src/gui/app.py)

---

## Troubleshooting
- API keys missing: Set both environment variables (or Streamlit secrets)
- Exa rate limiting: Retries and backoff are built-in, but bursty queries can still hit limits
- Optional LLM imports: We default to Gemini; to use Anthropic/Groq, install their SDKs and update llm()
- Debug outputs: Inspect logs/ for timestamped artifacts from each task

---

## UI Screenshots

![image](https://github.com/user-attachments/assets/68121ef0-f41b-4745-ba9f-33bf896bfe69)

![7CE03ED0-3020-4C0B-8BC2-4F8D68CD2F46_1_105_c](https://github.com/user-attachments/assets/1ceb9d4b-60cb-44c6-8135-06d187b8020c)

### 1. User Input Panel
<img width="337" alt="Screenshot 2025-01-23 at 9 39 36 PM" src="https://github.com/user-attachments/assets/9e284f75-737c-4008-97c3-3d0b3ab5a4b1" />

### 2. Real-Time Updates
<img width="416" alt="Screenshot 2025-01-23 at 9 40 37 PM" src="https://github.com/user-attachments/assets/7a7e11c2-6eaa-404b-919a-cc377d0546b2" />

### 3. Newsletter Generation
<img width="1037" alt="Screenshot 2025-01-23 at 9 42 05 PM" src="https://github.com/user-attachments/assets/a2466007-2181-4f39-aa7d-d5964b81296c" />

### 4. Download Option
<img width="683" alt="Screenshot 2025-01-23 at 9 41 15 PM" src="https://github.com/user-attachments/assets/655878c9-5190-47ed-8c5c-f8c82e483553" />
