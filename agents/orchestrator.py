import sys
import os

# Ensure we can import from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_backend import generate
from tools.web_search import search_web
from tools.slides import extract_text_from_pdf
from tools.email_sender import send_email

class TeachingAgentOrchestrator:
    def __init__(self):
        # A simple state machine to hold the session data for the user
        self.state = {
            "slide_text": "",
            "topic": "",
            "lesson_plan": "",
            "research_links": [],
            "final_report": "",
            "pdf_path": ""
        }

    def ingest_slides(self, pdf_path: str):
        """Extracts text from the uploaded PDF and stores it in state."""
        self.state["pdf_path"] = pdf_path
        self.state["slide_text"] = extract_text_from_pdf(pdf_path)
        return self.state["slide_text"]

    def generate_lesson_plan(self, context_info: str = "60 minutes, general audience"):
        """Calls the local LLM to generate a lesson plan based on slide text."""
        if not self.state["slide_text"] or self.state["slide_text"].startswith("No extractable"):
            return "Error: No valid slide text found. Please upload a valid PDF first."

        messages = [
            {"role": "system", "content": f"You are an expert teaching assistant. Create a lesson plan based on the slides. Context: {context_info}. Include objectives, a timed outline, and one practical exercise."},
            {"role": "user", "content": f"Here is the text from the slides:\n{self.state['slide_text'][:3000]}\n\nPlease generate the lesson plan."}
        ]
        
        print("Agent: Calling local Llama-3 model for lesson plan...")
        plan = generate(messages, temperature=0.7, max_tokens=800)
        self.state["lesson_plan"] = plan
        
        # Extract a short topic for web research
        topic_messages = [
            {"role": "system", "content": "You are a precise keyword extractor. Extract a 1 to 3 word topic summary from the text. Return ONLY the 1-3 words, no introductory text, no quotes, no explanations."},
            {"role": "user", "content": f"Text: {plan[:1000]}\n\nKeywords only:"}
        ]
        raw_topic = generate(topic_messages, temperature=0.1, max_tokens=10).strip()
        # Clean up in case the LLM still chatters
        raw_topic = raw_topic.replace('"', '').replace("Here is", "").split('\n')[0][:50]
        self.state["topic"] = raw_topic
        print(f"Agent: Extracted topic for research -> {self.state['topic']}")
        
        return plan

    def perform_web_research(self):
        """Performs a web search based on the lesson plan topic."""
        if not self.state["topic"]:
            return "Error: Please generate a lesson plan first so I know what to research."

        query = f"{self.state['topic']} tutorial or best resources"
        print(f"Agent: Searching web for '{query}'...")
        results = search_web(query, max_results=3)
        self.state["research_links"] = results
        
        if not results:
            return "Could not find any research links online."
            
        formatted_links = "\n".join([f"- [{r['title']}]({r['url']})" for r in results])
        return formatted_links

    def prepare_final_report(self):
        """Combines the plan and research into a final string."""
        if not self.state["lesson_plan"]:
            return "Error: Lesson plan is missing."
            
        report = f"📚 **Lesson Plan:**\n\n{self.state['lesson_plan']}\n\n"
        report += f"🌐 **Supporting Resources:**\n\n"
        
        for r in self.state["research_links"]:
            report += f"- {r['title']}: {r['url']}\n"
            
        self.state["final_report"] = report
        return report

    def email_report(self, recipient_email: str):
        """Sends the final report via email."""
        if not self.state["final_report"]:
            return False, "Error: Final report is not ready yet. Please run /plan and /research first."
            
        subject = f"Your Teaching Package: {self.state['topic']}"
        success = send_email(recipient_email, subject, self.state["final_report"])
        
        if success:
            return True, f"Email sent successfully to {recipient_email}!"
        else:
            return False, "Failed to send email. Please check your console logs or .env credentials."
