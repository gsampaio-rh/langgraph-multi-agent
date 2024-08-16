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
    # url = "https://raw.githubusercontent.com/rhpds/virt-migration-day2-demo/ba8c21ab4875ff8d2a74266c695dcee75b32396e/content/modules/ROOT/pages/01-mtv-migration.adoc"
    # user_request = (
    #     "Researcher Agent: Please crawl this page https://rhpds.github.io/virt-migration-demo/modules/01-mtv-migration.html "
    #     "and extract all the content. "
    #     "Architect Agent: Once the content is extracted, please list all the requirements, steps, and tools needed to complete the tutorial."
    # )
    url = "https://example.com/"
    user_request = f"Just crawl this page: {url}. Just crawl the page and do nothing else! Don't do something else!"
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
