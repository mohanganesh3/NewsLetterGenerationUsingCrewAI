<h1 align="center">🚀 Live Demo: <a href="https://newslettergenerationusingcrewai-ocw9fz38zcsqr976xqg9h3.streamlit.app/">Open the Streamlit App</a></h1>

# NewsletterGen: Your AI-Powered Newsletter Creation Suite 📰

Whether you’re a business owner or a content creator, NewsletterGen revolutionizes newsletter creation by combining advanced AI with a seamless user experience.

**Try the live website here:** <a href="https://newslettergenerationusingcrewai.onrender.com">Visit NewsletterGen</a>

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
