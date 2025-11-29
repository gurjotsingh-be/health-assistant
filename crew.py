from crewai import Crew
from agents import get_all_agents
from tasks import get_all_tasks
from config import DISCLAIMER
import re

class HealthAssistantCrew:
    def __init__(self):
        self.agents = get_all_agents()
    
    def format_output(self, raw_output):
        output = str(raw_output)
        
        output = re.sub(r'\*\*([^\*]+)\*\*', r'\1', output)
        output = re.sub(r'\*([^\*]+)\*', r'\1', output)
        output = re.sub(r'_([^_]+)_', r'\1', output)
        output = re.sub(r'\*+', '', output)
        output = re.sub(r'\n{3,}', '\n\n', output)
        
        sections = output.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            lines = section.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith(':') and len(line) < 100:
                    formatted_lines.append('\n' + line.upper())
                elif line[0:2].replace('.', '').replace(')', '').isdigit():
                    formatted_lines.append('  ' + line)
                else:
                    formatted_lines.append(line)
            
            if formatted_lines:
                formatted_sections.append('\n'.join(formatted_lines))
        
        output = '\n\n'.join(formatted_sections)
        output = re.sub(r'\n{3,}', '\n\n', output)
        
        return output.strip()
    
    def run(self, symptoms, age, medical_history):
        context = f"""
        Patient Information:
        - Age: {age}
        - Symptoms: {symptoms}
        - Medical History: {medical_history if medical_history else 'None provided'}
        """
        
        tasks = get_all_tasks(self.agents, context)
        
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        formatted_result = self.format_output(result)
        
        return formatted_result + "\n\n" + DISCLAIMER
