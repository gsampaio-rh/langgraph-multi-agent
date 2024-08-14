from workflows.workflow_graph import create_graph, compile_workflow
from IPython.display import Image, display
from config.config import app_config
from custom_tools import tools_description
from termcolor import colored

def main():

    # Print the available tools and agents
    print(colored("Available Agents:", "light_blue"))
    print(colored(f"{app_config.get_agents_description()}", "light_blue"))
    print(colored("\nAvailable Tools:", "light_blue"))
    print(colored(f"{tools_description}", "light_blue"))
    print(colored("\nStarting the workflow...\n", "light_blue"))

    graph = create_graph()
    workflow = compile_workflow(graph)
    # display(Image(workflow.get_graph().draw_png()))

    iterations = 10
    config = {"configurable": {"thread_id": "1"}}
    verbose = True
    user_request = "Just crawl this page: https://example.com/. Just crawl the page and do nothing else! Don't do something else!"
    # user_request = "Simply crawl this page: https://example.com/"
    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")


if __name__ == "__main__":
    main()
