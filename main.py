import argparse
from workflows.workflow_graph import create_graph, compile_workflow
from utils.setup_utils import startup
from utils.helpers import get_file_content
from IPython.display import Image, display


def main(
    user_request=None,
    iterations=10,
    verbose=True,
    config={"configurable": {"thread_id": "5"}},
):
    # Default behavior if no user_request is provided
    if not user_request:
        tutorial_file = "data/1_PREPARATION.md"
        tutorial = get_file_content(tutorial_file)
        user_request = f"Using the following tutorial, create a comprehensive migration plan for migrating virtual machines from VMware to OpenShift using the Migration Toolkit for Virtualization: \n\n {tutorial}"

    # Setup and initialization
    startup()

    # Create and compile the workflow
    graph = create_graph()
    workflow = compile_workflow(graph)

    # Load tutorial content if specified in user request
    dict_inputs = {"user_request": user_request}
    limit = {"recursion_limit": iterations}

    # Stream the workflow and process the output
    for event in workflow.stream(dict_inputs, config=config):
        if verbose:
            print(event)
        else:
            print("\n")


if __name__ == "__main__":
    # Parse arguments from the command line
    parser = argparse.ArgumentParser(
        description="Process a migration plan for VMware to OpenShift migration."
    )

    # Add a command-line argument for the user request, optional with default
    parser.add_argument(
        "--user_request",
        type=str,
        nargs="?",
        default=None,
        help="The user request string for creating a migration plan.",
    )

    # Optional arguments
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations for the workflow.",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")

    # Parse the arguments
    args = parser.parse_args()

    # Call main with parsed arguments, using defaults if arguments are not provided
    main(
        user_request=args.user_request, iterations=args.iterations, verbose=args.verbose
    )
