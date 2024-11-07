import re
from typing import Dict, List, Optional
from langfuse import Langfuse

def get_prompt_variables(langfuse: Langfuse, label: Optional[str] = None, tag: Optional[str] = None) -> Dict[str, Dict[str, any]]:
    """
    Retrieves all Langfuse prompts and extracts their variables.
    
    Args:
        langfuse (Langfuse): Langfuse client instance
        label (str, optional): Filter prompts by label
        tag (str, optional): Filter prompts by tag
        
    Returns:
        dict: Dictionary mapping prompt names to their variables and chat status
    """
    lf_api_wrapper = langfuse.client
    
    # Get prompts with optional filtering
    prompts = lf_api_wrapper.prompts.list(label=label, tag=tag)
    
    prompt_info = {}
    
    # Process each prompt
    for prompt in prompts.data:
        variables = set()
        
        # Get prompt details
        prompt_detail = langfuse.get_prompt(prompt.name)
        is_chat = isinstance(prompt_detail.prompt, list)

        # Handle chat vs non-chat prompts differently
        if is_chat:
            prompt_content = prompt_detail.prompt
            for msg in prompt_content:
                if isinstance(msg.get("content"), str):
                    vars_found = re.findall(r'\{\{(.*?)\}\}', msg["content"])
                    variables.update(vars_found)
        else:
            # For non-chat prompts, process single prompt string
            if isinstance(prompt_detail.prompt, str):
                vars_found = re.findall(r'\{\{(.*?)\}\}', prompt_detail.prompt)
                variables.update(vars_found)
        
        prompt_info[prompt.name] = {
            "variables": list(variables),
            "is_chat": is_chat
        }
    
    return prompt_info

def get_project_name(langfuse):
    projects = langfuse.client.projects.get().data
    if len(projects)>1:
        print("Warning! More then one project found!")
    return projects[0].name
    