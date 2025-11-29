from crewai import Agent
from llm_config import get_llm
import yaml
import os

def load_agents_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'agents.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def create_agent_from_config(agent_name, config):
    return Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        llm=get_llm(),
        verbose=config.get('verbose', True),
        allow_delegation=config.get('allow_delegation', False)
    )

def create_symptom_analyzer():
    agents_config = load_agents_config()
    return create_agent_from_config('symptom_analyzer', agents_config['symptom_analyzer'])

def create_medical_researcher():
    agents_config = load_agents_config()
    return create_agent_from_config('medical_researcher', agents_config['medical_researcher'])

def create_health_advisor():
    agents_config = load_agents_config()
    return create_agent_from_config('health_advisor', agents_config['health_advisor'])

def get_all_agents():
    agents_config = load_agents_config()
    return {
        'symptom_analyzer': create_agent_from_config('symptom_analyzer', agents_config['symptom_analyzer']),
        'medical_researcher': create_agent_from_config('medical_researcher', agents_config['medical_researcher']),
        'health_advisor': create_agent_from_config('health_advisor', agents_config['health_advisor'])
    }
