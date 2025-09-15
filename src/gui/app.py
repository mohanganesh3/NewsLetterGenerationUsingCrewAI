import streamlit as st
import sys
import os

# Add the src directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from newsletter_gen.crew import NewsletterGenCrew
except ImportError:
    # Fallback for different path structures
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    from newsletter_gen.crew import NewsletterGenCrew


class NewsletterGenUI:

    def load_html_template(self):
        # Handle different working directories in local vs cloud environments
        template_paths = [
            "src/newsletter_gen/config/newsletter_template.html",  # Local development
            "newsletter_gen/config/newsletter_template.html",      # Streamlit Cloud from src/
            "../newsletter_gen/config/newsletter_template.html",   # From gui directory
            os.path.join(os.path.dirname(__file__), "..", "newsletter_gen", "config", "newsletter_template.html")  # Absolute path
        ]
        
        for template_path in template_paths:
            try:
                with open(template_path, "r") as file:
                    html_template = file.read()
                return html_template
            except FileNotFoundError:
                continue
        
        # If no template found, return a basic template
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Newsletter</title></head>
        <body>
        <h1>Newsletter</h1>
        <div>{content}</div>
        </body>
        </html>
        """

    def generate_newsletter(self, topic, personal_message):
        inputs = {
            "topic": topic,
            "personal_message": personal_message,
            "html_template": self.load_html_template(),
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
