from crewai import Task
import yaml
import os

def load_tasks_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'tasks.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def create_task_from_config(task_config, agent, context):
    description = task_config['description'].format(context=context)
    return Task(
        description=description,
        agent=agent,
        expected_output=task_config['expected_output']
    )

def create_symptom_analysis_task(agent, context):
    tasks_config = load_tasks_config()
    return create_task_from_config(tasks_config['symptom_analysis'], agent, context)

def create_medical_research_task(agent, context):
    tasks_config = load_tasks_config()
    return create_task_from_config(tasks_config['medical_research'], agent, context)

def create_health_advice_task(agent, context):
    tasks_config = load_tasks_config()
    return create_task_from_config(tasks_config['health_advice'], agent, context)

def get_all_tasks(agents_dict, context):
    tasks_config = load_tasks_config()
    
    tasks = []
    for task_name, task_config in tasks_config.items():
        agent_name = task_config['agent']
        agent = agents_dict.get(agent_name)
        if agent:
            tasks.append(create_task_from_config(task_config, agent, context))
    
    return tasks
