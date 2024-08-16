# utils/agent_utils.py
from config.config import app_config

def format_agents_description(agent_description: str = app_config.get_agents_description()):
    agents_list = []
    current_agent = None
    current_responsibilities = []

    try:
        for line in agent_description.splitlines():
            line = line.strip()

            if line.startswith("#### **") and "Agent**" in line:
                if current_agent:
                    agents_list.append(
                        {
                            "name": current_agent,
                            "role": current_role,
                            "responsibilities": current_responsibilities,
                        }
                    )
                current_agent = line.replace("#### **", "").replace("**", "").strip()
                current_responsibilities = []

            elif line.startswith("- **Role**:"):
                current_role = line.replace("- **Role**:", "").strip()

            elif line.startswith("- **Responsibilities**:"):
                continue

            elif line.startswith("- "):
                current_responsibilities.append(line.replace("- ", "").strip())

        if current_agent:
            agents_list.append(
                {
                    "name": current_agent,
                    "role": current_role,
                    "responsibilities": current_responsibilities,
                }
            )
    except Exception as e:
        raise ValueError(f"Error formatting agents: {str(e)}")

    return agents_list
