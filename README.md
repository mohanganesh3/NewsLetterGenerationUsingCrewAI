### 🚀 Live Demo: <a href="https://newslettergenerationusingcrewai-ocw9fz38zcsqr976xqg9h3.streamlit.app/">Open the Streamlit App</a>

# NewsletterGen: Your AI-Powered Newsletter Creation Suite 📰

Build a production-ready, AI-powered newsletter generator that researches the latest news on any topic, curates and edits it, and compiles a beautiful, email-friendly HTML newsletter — automatically.

This repository shows you how to orchestrate a multi-agent CrewAI workflow, wire it to real research tools (Exa), and ship a friendly Streamlit UI on top. Use it as a template, or follow this blog-style guide to understand and re-build it from scratch.

---

## Table of Contents
- Prerequisites
- Quickstart
  - Install dependencies (Poetry or pip)
  - Set environment variables
  - Run via CLI or Streamlit
- Architecture (Big Picture)
- End-to-End Flow (What happens on each run)
- Code Tour (Key files and snippets)
- GUI Walkthrough (Screenshots)
- Extending the System (LLMs, tools, and agents)
- Deployment (Streamlit Cloud)
- Troubleshooting

---

## Prerequisites
- Python 3.10 – 3.13
- API keys:
  - GOOGLE_API_KEY for Google Gemini (we use gemini-2.0-flash-lite by default)
  - EXA_API_KEY for Exa research

## Quickstart

### 1) Install dependencies
You can use either Poetry or pip.

Poetry (recommended):
```bash
poetry install
```

Or pip:
```bash
pip install -r requirements.txt
```

### 2) Set environment variables
```bash
export GOOGLE_API_KEY="<your-gemini-api-key>"
export EXA_API_KEY="<your-exa-api-key>"
```

### 3) Run
- CLI (generates a newsletter by prompting for inputs in the terminal):
```bash
python src/newsletter_gen/main.py
```

- Streamlit UI (interactive):
```bash
streamlit run streamlit_app.py
# or directly the module
streamlit run src/gui/app.py
```

---

## Architecture (Big Picture)
CrewAI coordinates a team of three specialized agents. They run in sequence, and each task writes timestamped outputs into logs/.

- Research Agent (researcher): Uses Exa to search recent news and summarize 1–2 highly relevant items for the topic
- Editor Agent (editor): Rewrites titles, validates URLs, improves summaries, and reorders items for impact
- Designer Agent (designer): Fills an email-safe HTML template with the curated content and optional personal message

Key files:
- Agents: src/newsletter_gen/config/agents.yaml
- Tasks (prompts + output specs): src/newsletter_gen/config/tasks.yaml
- Tools (Exa integration + retries): src/newsletter_gen/tools/research.py
- Crew wiring (LLM + agents + tasks + logging): src/newsletter_gen/crew.py
- HTML email template: src/newsletter_gen/config/newsletter_template.html
- CLI: src/newsletter_gen/main.py
- Streamlit UI: src/gui/app.py and streamlit_app.py

---

## End-to-End Flow (What happens on each run)
1) You provide a topic (and optional personal message)
2) Researcher executes research_task using Exa tools
3) Editor executes edit_task to refine, validate, and order stories
4) Designer executes newsletter_task to fill the HTML template
5) Output is returned (and saved in logs/) as HTML ready to send

---

## Code Tour (Key files and snippets)

1) Tools: Web research with Exa + retries
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
            search_results = exa.search_and_contents(
                query=search_query,
                use_autoprompt=True,
                start_published_date=date_cutoff,
                text={"include_html_tags": False, "max_characters": 300},
                num_results=2
            )
            time.sleep(1)  # Rate limit safety
            return search_results
        except Exception as e:
            if "413" in str(e) or "429" in str(e):
                raise  # Let tenacity retry
            raise Exception(f"Exa API error: {str(e)}")
```

2) LLM: Gemini 2.0 Flash-Lite by default
```python
# src/newsletter_gen/crew.py (excerpt)
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def llm(self):
    google_api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=google_api_key,
        temperature=0.7
    )
    return llm
```

3) Prompts and expected outputs (YAML)
```yaml
# src/newsletter_gen/config/tasks.yaml (excerpt)
research_task:
  description: >
    Research the latest news on {topic} from reliable sources. Include only 1-2 relevant articles, summarize concisely (<500 characters), and provide URLs.

    IMPORTANT INSTRUCTIONS ABOUT USING TOOLS: When using tools, DO NOT ESCAPE the underscore character "_", EVER.
  expected_output: >
    A markdown document with 1-2 news stories, each with title, summary, and URL.
```

4) Generating from the UI
```python
# src/gui/app.py (excerpt)
from newsletter_gen.crew import NewsletterGenCrew

def generate_newsletter(self, topic, personal_message):
    inputs = {
        "topic": topic,
        "personal_message": personal_message,
        "html_template": self.load_html_template(),
    }
    return NewsletterGenCrew().crew().kickoff(inputs=inputs)
```

5) CLI entrypoint
```python
# src/newsletter_gen/main.py (excerpt)
from newsletter_gen.crew import NewsletterGenCrew

def run():
    inputs = {
        'topic': input('Enter the topic for yout newsletter: '),
        'personal_message': input('Enter a personal message for your newsletter: '),
        'html_template': load_html_template()
    }
    NewsletterGenCrew().crew().kickoff(inputs=inputs)
```

---

## GUI Walkthrough (Screenshots)
Below are the key screens from the Streamlit UI (kept from the original tutorial):

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

---

## Extending the System
- Add more research tools: Implement new BaseTool classes in src/newsletter_gen/tools and bind them to agents
- Change the LLM: You can switch to other LLMs (e.g., Anthropic or Groq). Install their SDKs, then modify llm() accordingly
  - Example (optional):
    - pip install langchain-anthropic langchain-groq
    - Update llm() to initialize ChatAnthropic or ChatGroq
- Customize the HTML template: Edit src/newsletter_gen/config/newsletter_template.html
- Add agents or tasks: Expand agents.yaml and tasks.yaml; wire them in src/newsletter_gen/crew.py

## Deployment (Streamlit Cloud)
- Set GOOGLE_API_KEY and EXA_API_KEY in Streamlit Secrets
- The app uses a small compatibility shim so Chroma works on Debian-based images
- Main entrypoints: streamlit_app.py or src/gui/app.py

## Troubleshooting
- API keys: Make sure both env vars are set
- Exa rate limits: Tools implement retries + backoff; heavy use may still rate-limit
- ImportError for optional LLMs: Either install the relevant SDKs or use the default Gemini config
- Logs: Check logs/ for timestamped outputs of each task

---

Whether you’re a business owner or a content creator, NewsletterGen revolutionizes newsletter creation by combining advanced AI with a seamless user experience.


# What We Will Build
we use Exa and CrewAI to build a team of AI research agents who, given any topic, can perform the following tasks for us:

- Research and summarize the latest news on the given topic.
- Verify that the sources are correct and that the articles are relevant to the selected topic.
- Compile the top stories into a newsletter using an HTML template.

To enhance usability, we built a user-friendly GUI using Streamlit, allowing users to input topics and personal messages, generate newsletters seamlessly, and download the final HTML output directly.

![image](https://github.com/user-attachments/assets/68121ef0-f41b-4745-ba9f-33bf896bfe69)



# Step 1: Create the Crew
The first thing to do is to create the crew that will perform the tasks for us. We can build it ourselves using the core components of CrewAI (agents, tools, and tasks) or we can use the CrewAI CLI to create the crew for us. Let’s use the CLI to create the crew:

    $ pip install crewai
    $ crewai new newsletter-crew
    
This will create a new folder called **newsletter-crew**. You will find here all the components that you will need to create and orchestrate your agents. In it, you can also find the **src/config** folder, which contains the configuration files for your crew: **agents.yaml** and **tasks.yaml**. These will be automatically loaded to the CrewAI system if you are using the CLI.

Consider that this command initializes a Poetry project, so if you want to add any dependencies, you should do it using Poetry:

    $ poetry add my-dependency

# Step 2: Create the Tasks

![7CE03ED0-3020-4C0B-8BC2-4F8D68CD2F46_1_105_c](https://github.com/user-attachments/assets/1ceb9d4b-60cb-44c6-8135-06d187b8020c)



## Input and Output
Before we start building our crew, we need to define the tasks that our agents will need to complete. This is the backbone of your crew. Once you have the tasks that your agents will perform, you can start creating your agents. But in order to define your tasks, you need to know what your input and expected output are. In our case:

- **Input**: the topic of the newsletter
- **Output**: the HTML code of the newsletter.
Once you have that, you can start listing the tasks that your agents will need to complete to get from input to expected output. Think of it as a to-do list for your agents.

## How to Define Tasks
This is usually where things can get tricky. But don’t worry! With some practice, you will be able to create a set of tasks for any automation within a few minutes!

My advice is to make a list of the to-do items that you would need to complete the task yourself. Then, break down these items into specific and granular tasks that your agents can perform.

Here are some tips for creating your crew:

- **Avoid tasks that are too complex**: If you try to perform too many actions in a single task, it can confuse the agent. For example, asking it to research a topic, summarize it, expand it, and reorder the results might be too much. Instead, break down the task into smaller, simpler tasks.
- **Perform thorough testing until you get reliable results**: You will need to run your crew several times, varying your input to make sure that your agents are working correctly.
- **Have a monitoring setup**: We will not cover monitoring and observability in this tutorial, but consider that you should be able to trace what your agents are thinking and doing. This is crucial for improving your prompts.
  
## For this Project, our tasks will be:

1. Research task. To complete this task, the agent will need to:

    - Search for the latest news on the given topic.
    - Select the most relevant articles.
    - Summarize the articles.
2. Edit task. To complete this task, the agent will need to verify that the sources are correct and that the articles are relevant to the selected topic. The agent in charge of this task will also need to improve the summary, add a title, and a comment to the article.

3. HTML task. To complete this task, the agent will need to replace the selected stories in an HTML template to generate the final newsletter file.

   As I mentioned above, this is a trial and error process. I started off with 4 tasks (I had an extra summary task), but I found that the researcher can do the summary as well without any issues. So I removed the summary task, and now I have 3 tasks. :)

## Fill the tasks.yaml File
Now that we have our tasks, we can fill the tasks.yaml file with the tasks that our agents will need to complete. Think of it as writing the prompt for your agents. A task in CrewAI contains the following properties:

- **Description**: A detailed prompt outlining what the task is supposed to do.
- **Expected Output**: The expected output of the task. This is what the agent should return when the task is completed. You can use Few-Shot Learning (include a few examples of the expected output) here.
- **Tools**: The tools that the agent can use to complete the task. You can also bind the tools to the agent instead of the task.

# Step 3: Create the agents
Now that we have our tasks, we can start creating the agents that will perform the tasks. An agent in CrewAI is a LangChain Runnable that can use tools to perform tasks. The agent can use the tools to perform the tasks that we defined in the **tasks.yaml** file.

To initialize an **Agent** object, you can specify many parameters. But the most important ones are:

- **Role**: This can be researcher, editor, html_generator, etc.
- **Goal**: This is a brief description of what your agent’s overal goal is. Try to be precise and give your agent a good idea of what its importance is within the entire project.
- **Backstory**: This is a brief description of the agent’s background. This is useful to give your agent a personality and a particular expertise. For example, you can say that the agent is a senior journalist known for its wit and humor. This will influence the writing style of the agent.

# Step 4: Create the tools
The tools are the functions that the agents will use to perform the tasks (that is why it is so important to use an LLM that supports function calling). We will then bind these tools to the agents when initializing them.

In this example, we will be giving the research tools to the researcher and editor agents. The tools that we will be using will use the following methods from the Exa client:

- **search_and_contents**: This tool will search a given query and return the full text contents each article.
- **find_similar**: This tool will find similar articles to the ones that we pass in.
-**get_contents**: This tool will get the contents of a given URL.

# Step 5: Put everything together
Once that everything is put together, you can put everything together in your **crew.py** file. This file will initialize the agents and tasks, bind the tools to the agents and create the crew.

# Step 6: Run the crew
Once everything is set up, you can run the crew using the CrewAI CLI. Remember that we are using poetry to manage the dependencies, so you should make sure that all your dependencies are installed in the virtual environment that you are using.

## To run the crew, you can use the following command:

    $ poetry lock
    $ poetry install
    $ poetry run <YOUR_CREW_NAME>
    
# Building GUI using Streamlit

The project features an interactive GUI built with Streamlit for seamless newsletter generation. It allows users to input a topic and a personal message, which are processed by a team of AI agents to create a professional HTML newsletter. The GUI provides a simple and user-friendly interface with options to download the generated newsletter directly.

## Features
### 1.User Input Panel

<img width="337" alt="Screenshot 2025-01-23 at 9 39 36 PM" src="https://github.com/user-attachments/assets/9e284f75-737c-4008-97c3-3d0b3ab5a4b1" />

• The sidebar allows users to input a topic and add a personal message, which will appear prominently in the generated newsletter

### 2.Real-Time Updates

<img width="416" alt="Screenshot 2025-01-23 at 9 40 37 PM" src="https://github.com/user-attachments/assets/7a7e11c2-6eaa-404b-919a-cc377d0546b2" />

• The interface dynamically displays the generation progress.

• Users are notified upon successful generation.

### 3.Newsletter Generation

<img width="1037" alt="Screenshot 2025-01-23 at 9 42 05 PM" src="https://github.com/user-attachments/assets/a2466007-2181-4f39-aa7d-d5964b81296c" />

• Using a team of specialized AI agents, the app transforms user inputs into a polished, professional newsletter, ensuring high-quality results every time.

• The output is a downloadable HTML file ready for use.

### 4.Download Option

<img width="683" alt="Screenshot 2025-01-23 at 9 41 15 PM" src="https://github.com/user-attachments/assets/655878c9-5190-47ed-8c5c-f8c82e483553" />

• The generated newsletter can be downloaded as an HTML file directly from the app.
