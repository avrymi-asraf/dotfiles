---
name: jira-workflow
description: Jira workflow — read, search, create, and update issues, commit with ticket references, and plan implementation. Use when the user asks to read/fetch/search Jira issues, create or update tickets, file bugs, create stories, plan work from a Jira ticket, or mentions /addJira.
---

# Jira Workflow

This skill covers the Jira lifecycle: **reading** issues, **searching** with JQL, **creating** and **updating** tickets, and **planning implementation** from Jira requirements.

---

## ⚠️ Quick Reference — Critical Rules (Read Before Doing Anything)

| Action | Mandatory pre-steps |
|--------|---------------------|
| **Create** a ticket | Run git context (Step 1) → resolve `components` (Step 3) → then call `jira_create_issue` |
| **Update** a ticket | Fetch the issue first with `jira_get_issue`, then call `jira_update_issue` |
| **Read/Search** | Jump straight to Part A |

### REMCLOUD project — `components` is REQUIRED

Skipping `components` when creating a `REMCLOUD` issue causes the API to return:
> `Component/s should be modified during this transition.`

**Always pass `components`** before calling `jira_create_issue`. Known values:

| Work area               | `components` value |
|-------------------------|--------------------|
| Lambda@Edge / CDN       | `CDN`              |
| Infrastructure as Code  | `terraform`        |
| CI/CD pipelines         | `CI/CD`            |

If unsure, call `jira_get_field_options` (see Step 3 in Part C).

---

## Part A — Read & Search Jira Issues

Use this section when the user provides an issue key, a Jira URL, or asks to find/search issues.

### A1. Get a Single Issue

Call `jira_get_issue` on the `user-jira` MCP server.

**Required parameter:**

| Parameter   | Type   | Description                          |
|-------------|--------|--------------------------------------|
| `issue_key` | string | Jira issue key, e.g. `REMCLOUD-123` |

**Useful optional parameters:**

| Parameter       | Type    | Default                                                                      | Notes                                                   |
|-----------------|---------|------------------------------------------------------------------------------|---------------------------------------------------------|
| `fields`        | string  | `summary,priority,updated,assignee,labels,status,reporter,issuetype,description,created` | Comma-separated, or `*all` for everything               |
| `expand`        | string  | —                                                                            | `renderedFields`, `transitions`, `changelog`            |
| `comment_limit` | integer | 10                                                                           | 0 to skip comments, up to 100                           |

**Example — fetch an issue with its comments:**

```
CallMcpTool: server="user-jira", toolName="jira_get_issue"
arguments: { "issue_key": "REMCLOUD-8994", "comment_limit": 20 }
```

**Example — fetch only status and assignee:**

```
CallMcpTool: server="user-jira", toolName="jira_get_issue"
arguments: { "issue_key": "REMCLOUD-8994", "fields": "summary,status,assignee" }
```

> **Tip — Jira URLs:** If the user gives a URL like `https://jira.example.com/browse/REMCLOUD-8994`, extract the issue key (`REMCLOUD-8994`) and call `jira_get_issue`.

### A2. Search Issues with JQL

Call `jira_search` on the `user-jira` MCP server.

**Required parameter:**

| Parameter | Type   | Description       |
|-----------|--------|-------------------|
| `jql`     | string | JQL query string  |

**Optional parameters:**

| Parameter         | Type    | Default | Notes                          |
|-------------------|---------|---------|--------------------------------|
| `fields`          | string  | essentials | Comma-separated or `*all`   |
| `limit`           | integer | 10      | 1–50                           |
| `start_at`        | integer | 0       | For pagination                 |
| `projects_filter` | string  | —       | Comma-separated project keys   |

**Common JQL patterns:**

```
project = REMCLOUD ORDER BY created DESC
assignee = currentUser() AND status != Done
labels = "prems" AND project = REMCLOUD
updated >= -7d AND project = REMCLOUD
issuetype = Bug AND status = "In Progress" AND project = REMCLOUD
text ~ "lambda edge" AND project = REMCLOUD
```

**Example — find my open issues:**

```
CallMcpTool: server="user-jira", toolName="jira_search"
arguments: { "jql": "assignee = currentUser() AND status != Done", "limit": 20 }
```

### A3. Browse All Issues in a Project

Call `jira_get_project_issues` for a quick listing (no JQL needed).

```
CallMcpTool: server="user-jira", toolName="jira_get_project_issues"
arguments: { "project_key": "REMCLOUD", "limit": 25 }
```

### A4. Get Development Info (PRs, Branches, Commits)

Call `jira_get_issue_development_info` to see linked source-control activity.

```
CallMcpTool: server="user-jira", toolName="jira_get_issue_development_info"
arguments: { "issue_key": "REMCLOUD-8994" }
```

### A5. Get Issue Dates & Status History

Call `jira_get_issue_dates` for timeline and workflow tracking.

```
CallMcpTool: server="user-jira", toolName="jira_get_issue_dates"
arguments: { "issue_key": "REMCLOUD-8994", "include_status_changes": true, "include_status_summary": true }
```

---

## Part B — Plan Before You Implement

When a Jira issue describes work to be done (feature, bug fix, refactor)

### B1. Read the Issue Thoroughly

1. Fetch the full issue with `jira_get_issue` (use `fields: "*all"` and `comment_limit: 50` to capture discussion).
2. Read linked issues, epics, or subtasks if referenced.
3. Check development info (`jira_get_issue_development_info`) for related PRs or prior attempts.

### B2. Understand the Codebase Context

1. Identify which files/modules the issue affects by reading the description, acceptance criteria, and comments.
2. Use code exploration tools (Read, Grep, SemanticSearch) to examine the relevant areas.
3. Note any dependencies, shared state, or downstream consumers.

### B3. Create an Implementation Plan

Before making any code changes:

1. **Switch to Plan mode** if the task is non-trivial (multiple files, architectural decisions, trade-offs).
2. Outline the steps: what changes, in which files, in what order.
3. Call out risks, edge cases, and testing approach.
4. Present the plan to the user for confirmation before proceeding.

> **Rule of thumb:** If the Jira issue touches more than 2 files or requires a design decision, plan first. For single-file, obvious fixes, skip straight to implementation but still mention what you are about to do.

### B4. Track Progress

- Use the TodoWrite tool to create a task list from the Jira requirements.
- Mark tasks as you complete them so the user can see progress.
- After completing all work, consider adding a comment to the Jira issue summarizing what was done (use `jira_add_comment`).

---

## Part C — Create / Update Jira Tickets

### Step 0. Decide: Create or Update?

- **Update** — the user provides an existing issue key (e.g., `REMCLOUD-1234`) or a Jira URL. Fetch the issue first with `jira_get_issue`, then jump to **Step 4b**.
- **Create** — no existing issue key. Follow the full workflow below.

---

### Step-by-Step Create/Update Workflow

### 1. Gather Git Context

Run these shell commands together to collect the assignee and labels:

```bash
git config user.email                       # → assignee email
basename $(git rev-parse --show-toplevel)    # → repo-name label
git rev-parse --abbrev-ref HEAD             # → branch-name label
```

This produces three values used in the create/update call:

| Value            | Source                     | Used as                              |
|------------------|----------------------------|--------------------------------------|
| **Email**        | `git config user.email`    | `assignee` parameter                 |
| **Repo name**    | `basename …`               | Jira label in `additional_fields`    |
| **Branch name**  | `git rev-parse …`          | Jira label in `additional_fields`    |

If a command fails (e.g., not a git repo), skip that label.

### 2. Analyze the Request

- Read the user's prompt to understand what the ticket is about.
- Scan relevant code files, make sure you understand the code, where and how it is used, if the ticket relates to a code change.
- Keep analysis brief; the goal is context for the ticket description.

### 3. Resolve Required Fields (Components)

Some Jira projects (e.g., `REMCLOUD`) **require** a component on issue creation.
If you skip it, the API returns: `Component/s should be modified during this transition.`

**Before creating the issue**, call `jira_get_field_options` to fetch valid components:

```
CallMcpTool: server="user-jira", toolName="jira_get_field_options"
arguments: { "field_id": "components", "project_key": "<PROJECT_KEY>", "issue_type": "Task" }
```

Pick the component that best matches the work area. Known mappings:

| Project    | Work Area              | Component |
|------------|------------------------|-----------|
| `REMCLOUD` | Lambda@Edge / CDN      | `CDN`     |
| `REMCLOUD` | Infrastructure as Code | `terraform` |
| `REMCLOUD` | CI/CD pipelines        | `CI/CD`   |

If the work area is not in the table above, use the fetched list to pick the closest match.

### 4a. Create the Issue

Call `jira_create_issue` on the `user-jira` MCP server.
`summary`, `description`, `assignee`, `components` are all **top-level** parameters.

**Required parameters:**

| Parameter     | Type   | Value                                        |
|---------------|--------|----------------------------------------------|
| `project_key` | string | Ask the user if not known. Common: `REMCLOUD` |
| `summary`     | string | Short ticket title                           |
| `issue_type`  | string | `Task`, `Bug`, `Story`, `Epic`, or `Subtask` |
| `components`  | string | From step 3. Comma-separated: `"CDN"` or `"CDN,AWS"` |

**Optional parameters:**

| Parameter           | Type   | Notes                                                          |
|---------------------|--------|----------------------------------------------------------------|
| `assignee`          | string | Email from step 1                                              |
| `description`       | string | Markdown format                                                |
| `additional_fields` | string | JSON string with labels (repo + branch from step 1). See below |

**Example call** (using values from step 1: email `user@example.com`, repo `my-repo`, branch `feature-xyz`):

```
CallMcpTool: server="user-jira", toolName="jira_create_issue"
arguments: {
  "project_key": "REMCLOUD",
  "summary": "Add retry logic for S3 key fetch",
  "issue_type": "Task",
  "components": "CDN",
  "assignee": "user@example.com",
  "description": "**Objective:**\n...",
  "additional_fields": "{\"labels\": [\"my-repo\", \"feature-xyz\"]}"
}
```

### 4b. Update an Existing Issue

Call `jira_update_issue` on the `user-jira` MCP server.

> **Parameter structure differs from create:**
> `summary`, `description`, `assignee` must be nested **inside the `fields` object**.
> `components` and `additional_fields` remain **top-level**.

**Required parameters:**

| Parameter    | Type   | Value                                             |
|--------------|--------|---------------------------------------------------|
| `issue_key`  | string | The existing issue key, e.g. `REMCLOUD-8994`      |
| `fields`     | string | **JSON string** of fields to update (see keys below) |

**Supported keys inside `fields`:**

| Key           | Type   | Notes                                  |
|---------------|--------|----------------------------------------|
| `summary`     | string | New ticket title                       |
| `description` | string | Markdown format                        |
| `assignee`    | string | Email, display name, or accountId      |

**Top-level optional parameters:**

| Parameter           | Type   | Notes                                                   |
|---------------------|--------|---------------------------------------------------------|
| `components`        | string | Comma-separated component names                         |
| `additional_fields` | string | JSON string with labels (repo + branch from step 1)     |

**Example call** (using values from step 1: repo `my-repo`, branch `feature-xyz`):

```
CallMcpTool: server="user-jira", toolName="jira_update_issue"
arguments: {
  "issue_key": "REMCLOUD-8994",
  "fields": "{\"summary\": \"Redact JWT signatures from audit logs\", \"description\": \"**Objective:**\\n...\"}",
  "additional_fields": "{\"labels\": [\"my-repo\", \"feature-xyz\"]}"
}
```

