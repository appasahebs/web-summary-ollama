
# Some websites need you to use proper headers when fetching them:
import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
import ollama
from dotenv import load_dotenv
import os
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, title=None, text=None):
        # Initialize the OpenAI API        
        load_dotenv(override=True)
        self.ollama_api = os.getenv('OLLAMA_API')
        print("Initializing website summary assistant...")
        self.title = title
        self.text = text
        
    def fetch(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        soap = BeautifulSoup(response.text, "html.parser")
        self.title = soap.title.string if soap.title else "No title found"
        for irrelevant in soap(["script", "style", "img", "svg", "input", "button"]):
            irrelevant.decompose()
        self.text = soap.get_text(separator="\n", strip=True)
    
    def user_prompt_for(self):
        user_prompt = f"You are looking at a website titled {self.title}"
        user_prompt += "\nThe contents of this website is as follows; \
    please provide a short summary of this website in markdown. \
    If it includes news or announcements, then summarize these too.\n\n"
        user_prompt += self.text
        return user_prompt

    def input(self):
        system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."
        return [
            {"role": "user", "content": self.user_prompt_for()}
        ]
    
    def summary(self, url):
        "This is a summary of the website"
        self.fetch(url)
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": 'llama3.2',
            "messages": self.input(),
            "stream": False
        }
        response = requests.post(self.ollama_api, json=payload, headers=headers)
        print(response.json()['message']['content'])
        print("Above is result")
        return response.json()['message']['content']
    
    def display_summary(self, url):
        summary = self.summary(url)
        print(summary)
        display(Markdown(summary))