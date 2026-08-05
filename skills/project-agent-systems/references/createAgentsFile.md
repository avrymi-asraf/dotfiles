Create or update the content for the `AGENTS.md` file. The output must strictly follow this Markdown template and schema. Populate the sections within the `[ ]` placeholders with the project's specific details.
Go over the project thoroughly.
If the file already exists, read it and update it with the latest project information.
Make sure you understand the big picture, what the project is about, how it runs, etc.
If something is not clear enough, ask!

````markdown
## Project Goal

* **Description:** <Provide a 1-2 sentence description of the project's primary objective, Describe **how** the code is executed (e.g., as a command-line script, a background service, an API, Describe) **where** the code is designed to run (e.g., locally, in a specific cloud environment like AWS EMR Serverless, within a Docker container)>

---

## Project Structure - remember to update it when you make changes

* **Architecture:** <Explain the high-level architecture, main components, and overall design. and the **Code Flow:** Describe the main code flow, detailing how data or control moves through the system from initiation to completion. You may use a  simple diagram. you need to describe it in terms of the code, functions ect>

---

## File Structure - remember to update it with the latest project information
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

## Running and using the code

**Prerequisites:**
* <List all necessary prerequisites, dependencies (e.g., Python 3.10+, pip), and configuration steps.>

**Build Steps (if applicable):**
1.  <Step 1 for building/compiling>
2.  <Step 2...>
<short description of the code flow of this command, how it works, etc.>

**Running the Application:**
1.  <Step 1 for running the code>
2.  <Step 2...>
<short description of the code flow of this command, how it works, etc.>

**use some options to run the code, for example:**
```bash
app arg1 arg2 --option1 value1 --option2 value2
```
<short description of the code flow of this command, how it works, etc.>

---

<<<<<<<< HEAD:skills/project-agent-systems/references/createAgentsFile.md
## Status - remember to update it
========

## relevant documents
<Provide links to any relevant documents, such as design documents, plans, skills that are relevant to this project (not general skills)>




## Status
>>>>>>>> refs/remotes/origin/main:skills/project-agent-systems/references/AgentsFile.md
<What are the status of the project? in dev, if we need to deploy - in prsees. it soulde be smale pharagrap that describe what is the status.
we use projct x on google, initlaize the bla bla.
>
<This section must be added to the `Agents.md` file exactly as written below:>

## Code Writing Rules
Do not create new documentation files (unless explicitly requested). Only update documentation via the `README` if necessary.

### File Header (Mandatory)
In the header of every code file, you **must** describe how that file relates to the **overall project architecture** and **code flow**.

Each code file **must** include a short description (no more than 4–5 sentences) that explains the following:
- Its role in the **big picture** (as defined in the **Project Structure** section).
- Its connection to the main **code flow** of the project.
- The intended **execution environment** (where this code will run, as defined in the **Project Goal** section).
<<<<<<<< HEAD:skills/project-agent-systems/references/createAgentsFile.md
- The skills, memory, shared docs are very important to continue working on on the project. you have all this are live files. and currently update them it is very very important. remember to do it!
- 
```

all the section above it is the template for the `AGENTS.md` file. You should fill in the sections with the specific details of your project. Make sure to provide clear and concise information that accurately reflects the project's goals, structure, and status.
========
Remember to update important documents, remember to update your memory remeber to update the relelevent skills (if nedded).
Shared documents are super super important, they allow you to learn from mistakes and move forward. Remember to use them and update them.

The skills folder has tutorials on how to handle important tools and things. Remember to read - and if you need to update them, update them. Integrate the new information with the existing information, don't reinvent the wheel.
The docs folder has important documents that are only relevant to this project. Plans, etc. If there is a document that relates to your task, use it - and update it. Again - integrate the information, don't reinvent the wheel.
Remember to update your memory. This is important
We are in research and development, not a running product. We are not interested in backward compatibility. It is much more important that the code is clean, clear and readable.
>>>>>>>> refs/remotes/origin/main:skills/project-agent-systems/references/AgentsFile.md
