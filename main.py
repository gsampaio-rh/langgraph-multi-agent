from workflows.workflow_graph import create_graph, compile_workflow
from IPython.display import Image, display
from custom_tools import tools_description
from termcolor import colored

def main():

    # Print the available tools and agents
    print(colored("Available Tools:", "light_blue"))
    print(colored(f"{tools_description}", "light_blue"))
    print(colored("\nStarting the workflow...\n", "light_blue"))

    graph = create_graph()
    workflow = compile_workflow(graph)
    # display(Image(workflow.get_graph().draw_png()))

    iterations = 10
    config = {"configurable": {"thread_id": "1"}}
    verbose = True
    user_request = "1. Crawl this page: https://example.com/ 2. Extract the body content. Do it, step-by-step."
    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")


if __name__ == "__main__":
    main()
