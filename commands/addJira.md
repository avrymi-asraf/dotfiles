Generate or update a Jira ticket using the `jira_create_issue` or `jira_update_issue` MCP tool.

**Configuration:**
- **Project:** Always set to `REMCLOUD`.
- **Labels:** Always add the current repository name as a label.

**Process:**
1.  **Analyze:** Read the prompt to understand the request and scan the codebase to grasp the underlying context or problem.
2.  **Structure:** The Jira ticket description MUST be highly concise and follow this structure:

    1.  **Current State:** Briefly describe the existing code problem or situation.
    2.  **Desired Change (What & Why):** State precisely what needs to be altered and the fundamental rationale for the change.
    3.  **High-Level Plan (How):** Outline the necessary architectural or big-picture steps. If there is more than one way to do it, you can list several directions.

**Crucial Constraint:**
Keep all sections extremely short and purposeful. Avoid low-level technical implementation details or fine-grained how-to instructions. Focus exclusively on *what* must change and *why*. Pseudo-code or simple diagrams/graphs are permitted for illustration.
