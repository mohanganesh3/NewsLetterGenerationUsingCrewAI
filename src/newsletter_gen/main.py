#!/usr/bin/env python
from newsletter_gen.crew import NewsletterGenCrew

def load_html_template(): 
    with open('src/newsletter_gen/config/newsletter_template.html', 'r') as file:
        html_template = file.read()
        
    return html_template


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': input('Enter the topic for yout newsletter: '),
        'personal_message': input('Enter a personal message for your newsletter: '),
        'html_template': load_html_template()
    }
    try:
        NewsletterGenCrew().crew().kickoff(inputs=inputs)
    except ValueError as e:
        if "GOOGLE_API_KEY" in str(e):
            print(f"❌ Configuration Error: {e}")
            print("Please set the GOOGLE_API_KEY environment variable with a valid Google API key.")
        else:
            print(f"❌ An error occurred: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")