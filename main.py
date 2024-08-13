from workflows.workflow_graph import create_graph, compile_workflow
from IPython.display import Image, display

def main():
    
    graph = create_graph()
    workflow = compile_workflow(graph)
    # display(Image(workflow.get_graph().draw_png()))

    iterations = 10
    config = {"configurable": {"thread_id": "1"}}
    verbose = True
    user_request = "Bring me the content on this page: https://example.com/"
    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")


if __name__ == "__main__":
    main()
