Generate the content for a new file named `Agents.md`. The output must strictly follow this Markdown template and schema. Populate the sections within the `[ ]` placeholders with the project's specific details.
Go over the project thoroughly.
Make sure you understand the big picture, what the project is about, how it runs, etc.
If something is not clear enough, ask!

````markdown
## Project Goal

* **Description:** <Provide a 1-2 sentence description of the project's primary objective, Describe **how** the code is executed (e.g., as a command-line script, a background service, an API, Describe) **where** the code is designed to run (e.g., locally, in a specific cloud environment like AWS EMR Serverless, within a Docker container)>

---

## Project Structure

* **Architecture:** <Explain the high-level architecture, main components, and overall design. and the **Code Flow:** Describe the main code flow, detailing how data or control moves through the system from initiation to completion. You may use a numbered list or simple diagram.>

---

## File Structure

<Provide a clear, tree-like representation of the project's directory and file layout. Follow the tree with brief descriptions for the purpose of key directories and important files.>

**Example:**
\`\`\`
/project-root
├── src/
│   └── main.py     # Main application entry point
├── docs/
│   └── agents.md   # This file
├── tests/
│   └── test_main.py
└── README.md
\`\`\`

* `src/`: [Description of this directory]
* `docs/`: [Description of this directory]
* `tests/`: [Description of this directory]

---

## Building and Running

**Prerequisites:**
* <List all necessary prerequisites, dependencies (e.g., Python 3.10+, pip), and configuration steps.>

**Build Steps (if applicable):**
1.  <Step 1 for building/compiling>
2.  <Step 2...>

**Running the Application:**
1.  <Step 1 for running the code>
2.  <Step 2...>

---

## Code Writing Rules

* **Style Guide:** [Specify the code style guide to follow (e.g., PEP 8 for Python, Google C++ Style Guide).]
* **Conventions:** [List any other project-specific development rules (e.g., commit message format, branching strategy, naming conventions).]
```"
````