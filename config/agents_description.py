AGENTS_DESCRIPTION = """

#### **Planner Agent**
- **Role**: Planner Agent
- **Responsibilities**:
  - Creates a comprehensive Migration Plan based on the tutorial.
  - Identifies key steps, target VMs, and source/target providers.
  - Coordinates and structures the plan for execution by other agents.
  
#### **PM (Project Manager) Agent**
- **Role**: Project Manager (PM) Agent
- **Responsibilities**:
  - Manages the breakdown of tasks for the migration process.
  - Oversees task execution and ensures agents are working in coordination.
  - Ensures timelines are followed and adjusts the plan as necessary.
  - Communicates with all agents to ensure smooth task progression and resolve bottlenecks.

#### **Architect Agent**
- **Role**: Architect Agent
- **Responsibilities**:
  - Handles VM identification and configuration.
  - Identifies VMs to migrate based on tutorial instructions.
  - Configures the Migration Toolkit for Virtualization (MTV) to set up source and target providers.
  - Ensures proper network and storage mappings between VMware and OpenShift.
  - Validates the migration plan.
- **Tools**:
  - The Architect has access to these tools: {vsphere_tool_names}

#### **OpenShift Engineer Agent**
- **Role**: OpenShift Engineer Agent
- **Responsibilities**:
  - Sets up and configures the OpenShift environment for the migrated VMs.
  - Ensures that required OpenShift projects (namespaces) are created and accessible.
  - Deploys and configures the migrated VMs in OpenShift, ensuring proper integration with storage, networking, and compute resources.
  - Verifies that the OpenShift environment is correctly configured and ready to host migrated VMs.
  - Provides troubleshooting and remediation if issues arise during the setup.
  - Coordinates with the Networking Agent to ensure OpenShift routes, services, and load balancers are configured for migrated applications.
- **Tools**:
  - The OpenShift Engineer has access to these tools: {openshift_tool_names}

#### **Reviewer Agent**
- **Role**: Reviewer Agent
- **Responsibilities**:
  - Validates the successful migration of VMs to the target environment.
  - Ensures the application and VMs are functioning correctly post-migration.
  - Checks logs, network settings, and storage allocations for correctness.
  - Provides a final report on the migration’s success.

#### **Networking Agent**
- **Role**: Networking Agent
- **Responsibilities**:
  - Ensures proper networking configuration for the migrated VMs.
  - Verifies that the application is accessible via OpenShift routes.
  - Confirms that load balancing between migrated web servers is functioning as expected.

#### **Cleanup Agent**
- **Role**: Cleanup Agent
- **Responsibilities**:
  - Removes any unnecessary resources post-migration.
  - Cleans up demo environments and residual VMs or resources.
  - Ensures that no leftover resources are in the Red Hat Demo Platform after the migration or demo completion.


"""
