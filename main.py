from workflows.workflow_graph import create_graph, compile_workflow
from utils.setup_utils import startup
from utils.helpers import get_file_content
from IPython.display import Image, display

def main():

    startup()
    
    graph = create_graph()
    workflow = compile_workflow(graph)
    # display(Image(workflow.get_graph().draw_png()))

    iterations = 10
    config = {"configurable": {"thread_id": "5"}}
    verbose = True

    tutorial_file="data/1_PREPARATION.md"
    tutorial = get_file_content(tutorial_file)

    user_request = f"Using the following tutorial, create a comprehensive migration plan for migrating virtual machines from VMware to OpenShift using the Migration Toolkit for Virtualization: \n\n {tutorial}"

    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")

if __name__ == "__main__":
    main()
