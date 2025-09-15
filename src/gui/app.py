import os
import sys
import json
import streamlit as st

# Ensure 'src' (the parent of this file's directory) is on sys.path so `newsletter_gen` is importable
# when Streamlit runs this module directly (as configured on Streamlit Cloud)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# If running on Streamlit Cloud, expose secrets as environment variables for downstream libs
if st.secrets.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
if st.secrets.get("EXA_API_KEY"):
    os.environ["EXA_API_KEY"] = st.secrets["EXA_API_KEY"]

# Ensure ChromaDB works on environments with older system sqlite3
# If pysqlite3 is present, alias it to sqlite3 before importing CrewAI/Chroma
try:
    import pysqlite3 as _pysqlite3  # type: ignore
    import sys as _sys
    _sys.modules["sqlite3"] = _sys.modules.pop("pysqlite3")
except Exception:
    # Safe to ignore; Chroma will raise a helpful error if sqlite is too old
    pass

from newsletter_gen.crew import NewsletterGenCrew
from newsletter_gen.tools.research import fetch_recent_news


class NewsletterGenUI:

    def load_html_template(self):
        with open("src/newsletter_gen/config/newsletter_template.html", "r") as file:
            html_template = file.read()

        return html_template

    def generate_newsletter(self, topic, personal_message):
        # Fetch recent news programmatically (avoids CrewAI tool validation issues)
        try:
            recent = fetch_recent_news(topic)
        except Exception as e:
            recent = []  # Fallback to empty if Exa fails; the researcher will rely on general knowledge
        inputs = {
            "topic": topic,
            "personal_message": personal_message,
            "html_template": self.load_html_template(),
            # Provide pre-fetched results to the crew; referenced in tasks.yaml
            "pre_fetched_news": json.dumps(recent, default=str),
        }
        return NewsletterGenCrew().crew().kickoff(inputs=inputs)

    def newsletter_generation(self):

        if st.session_state.generating:
            st.session_state.newsletter = self.generate_newsletter(
                st.session_state.topic, st.session_state.personal_message
            )

        if st.session_state.newsletter and st.session_state.newsletter != "":
            with st.container():
                st.write("Newsletter generated successfully!")
                st.download_button(
                    label="Download HTML file",
                    data=st.session_state.newsletter,
                    file_name="newsletter.html",
                    mime="text/html",
                )
            st.session_state.generating = False

    def sidebar(self):
        with st.sidebar:
            st.title("Newsletter Generator")

            st.write(
                """
                To generate a newsletter, enter a topic and a personal message. \n
                Your team of AI agents will generate a newsletter for you!
                """
            )

            st.text_input("Topic", key="topic", placeholder="USA Stock Market")

            st.text_area(
                "Your personal message (to include at the top of the newsletter)",
                key="personal_message",
                placeholder="Dear readers, welcome to the newsletter!",
            )

            if st.button("Generate Newsletter"):
                st.session_state.generating = True

    def render(self):
        st.set_page_config(page_title="Newsletter Generation", page_icon="📧")

        if "topic" not in st.session_state:
            st.session_state.topic = ""

        if "personal_message" not in st.session_state:
            st.session_state.personal_message = ""

        if "newsletter" not in st.session_state:
            st.session_state.newsletter = ""

        if "generating" not in st.session_state:
            st.session_state.generating = False

        self.sidebar()

        self.newsletter_generation()


if __name__ == "__main__":
    NewsletterGenUI().render()
