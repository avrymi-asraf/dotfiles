# Jira MCP Tools - Full Schema Reference

All tools use MCP server: `user-jira`

---

## jira_create_issue

Create a new Jira issue.

**Parameters:**

| Name               | Type   | Required | Description                                                                 |
|--------------------|--------|----------|-----------------------------------------------------------------------------|
| `project_key`      | string | Yes      | Project key (e.g., `REMCLOUD`). Pattern: `^[A-Z][A-Z0-9]+$`                |
| `summary`          | string | Yes      | Issue title                                                                 |
| `issue_type`       | string | Yes      | `Task`, `Bug`, `Story`, `Epic`, `Subtask`                                   |
| `assignee`         | string | No       | Email, display name, or `accountid:...`                                     |
| `description`      | string | No       | Markdown format                                                             |
| `components`       | string | No       | Comma-separated: `"Frontend,API"`                                           |
| `additional_fields` | string | No      | **JSON string** (not object). See examples below                            |

### additional_fields Examples

Labels:
```
"{\"labels\": [\"my-repo\"]}"
```

Priority:
```
"{\"priority\": {\"name\": \"High\"}}"
```

Reporter:
```
"{\"reporter\": {\"id\": \"accountid:xxx\"}}"
```

Parent (subtask or epic link):
```
"{\"parent\": \"PROJ-123\"}"
```

Fix versions:
```
"{\"fixVersions\": [{\"id\": \"10020\"}]}"
```

Custom fields:
```
"{\"customfield_10010\": \"value\"}"
```

---

## jira_update_issue

Update an existing issue.

| Name               | Type   | Required | Description                                                    |
|--------------------|--------|----------|----------------------------------------------------------------|
| `issue_key`        | string | Yes      | e.g., `PROJ-123`. Pattern: `^[A-Z][A-Z0-9]+-\d+$`            |
| `fields`           | object | Yes      | Dict of fields. `description` uses Markdown                    |
| `additional_fields` | string | No      | **JSON string** for custom/complex fields                      |
| `components`       | string | No      | Comma-separated component names                                |
| `attachments`      | string | No      | Comma-separated file paths or JSON array string                |

### fields Examples

```json
{
  "summary": "New title",
  "description": "## Heading\nMarkdown body",
  "assignee": "user@example.com"
}
```

---

## jira_get_issue

Get details of a specific issue.

| Name              | Type    | Required | Description                                              |
|-------------------|---------|----------|----------------------------------------------------------|
| `issue_key`       | string  | Yes      | e.g., `PROJ-123`                                         |
| `fields`          | string  | No       | Comma-separated fields, `*all` for everything             |
| `expand`          | string  | No       | `renderedFields`, `transitions`, `changelog`              |
| `comment_limit`   | integer | No       | Max comments (0-100, default 10)                          |
| `update_history`  | boolean | No       | Update view history (default true)                        |

---

## jira_search

Search issues using JQL.

| Name              | Type    | Required | Description                                              |
|-------------------|---------|----------|----------------------------------------------------------|
| `jql`             | string  | Yes      | JQL query string                                          |
| `fields`          | string  | No       | Comma-separated fields to return                          |
| `limit`           | integer | No       | Max results 1-50 (default 10)                             |
| `start_at`        | integer | No       | Pagination offset (default 0)                             |
| `projects_filter` | string  | No       | Comma-separated project keys                              |
| `expand`          | string  | No       | Fields to expand                                          |

### JQL Examples

```
project = REMCLOUD ORDER BY created DESC
issuetype = Epic AND project = REMCLOUD
assignee = currentUser() AND status != Done
labels = "my-repo" AND project = REMCLOUD
updated >= -7d AND project = REMCLOUD
```

---

## jira_get_user_profile

Look up a Jira user.

| Name              | Type   | Required | Description                                        |
|-------------------|--------|----------|----------------------------------------------------|
| `user_identifier` | string | Yes      | Email, username, account ID, or key (Server/DC)    |

---

## jira_add_comment

Add a comment to an issue.

| Name         | Type   | Required | Description                                             |
|--------------|--------|----------|---------------------------------------------------------|
| `issue_key`  | string | Yes      | e.g., `PROJ-123`                                        |
| `comment`    | string | Yes      | Markdown format                                          |
| `visibility` | string | No       | JSON string: `"{\"type\":\"group\",\"value\":\"jira-users\"}"` |

---

## jira_search_fields

Find field IDs by keyword.

| Name      | Type    | Required | Description                         |
|-----------|---------|----------|-------------------------------------|
| `keyword` | string  | No       | Fuzzy search term (empty = list all)|
| `limit`   | integer | No       | Max results (default 10)            |
| `refresh` | boolean | No       | Force refresh field list            |

---

## jira_get_field_options

Get allowed values for a custom field.

| Name          | Type   | Required | Description                                 |
|---------------|--------|----------|---------------------------------------------|
| `field_id`    | string | Yes      | e.g., `customfield_10001`                   |
| `context_id`  | string | No       | Cloud only, auto-resolved if omitted         |
| `project_key` | string | No       | Required for Server/DC                       |
| `issue_type`  | string | No       | Required for Server/DC                       |

---

## jira_batch_create_issues

Create multiple issues at once.

| Name            | Type    | Required | Description                                     |
|-----------------|---------|----------|-------------------------------------------------|
| `issues`        | string  | Yes      | JSON array string of issue objects               |
| `validate_only` | boolean | No       | If true, validates without creating              |

### issues Format

```json
"[{\"project_key\": \"PROJ\", \"summary\": \"Issue 1\", \"issue_type\": \"Task\"}, {\"project_key\": \"PROJ\", \"summary\": \"Issue 2\", \"issue_type\": \"Bug\"}]"
```
