from config.config import app_config
from custom_tools import tools_description
from workflows.workflow_graph import create_graph, compile_workflow
from utils.log_utils import log_startup
from IPython.display import Image, display

def main():

    log_startup(app_config.get_agents_description(), tools_description)

    graph = create_graph()
    workflow = compile_workflow(graph)
    # display(Image(workflow.get_graph().draw_png()))

    iterations = 10
    config = {"configurable": {"thread_id": "1"}}
    verbose = True
    
    url = "https://example.com/"
    user_request = f"Just crawl this page: {url}. Just crawl the page and do nothing else! Don't do something else!"
    
    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")


if __name__ == "__main__":
    main()
