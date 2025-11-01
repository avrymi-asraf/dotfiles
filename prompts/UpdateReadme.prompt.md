---
mode: agent
---
Your task is to create the README for the current project.
The README is the entry point to the project. It should be useful for both humans and agents.
Analyze this codebase to generate or update `README.md` for guiding humans and AI coding agents.

Focus on discovering the essential knowledge that would help an humans or AI agents be immediately productive in this codebase. Consider aspects like:
- The "big picture" architecture that requires reading multiple files to understand - major components, service boundaries, data flows, and the "why" behind structural decisions
- Critical developer workflows (builds, tests, debugging) especially commands that aren't obvious from file inspection alone
- Project-specific conventions and patterns that differ from common practices
- Integration points, external dependencies, and cSross-component communication patterns

Read: the existing README (if it exists), the file system, and the code.
The purpose of the existing README (if present) is to serve as an introduction, so you do not start from scratch.
Based on this, recreate the README in the following format:

## Required Sections in the README


```markdwon
# <name of the project>

<Briefly state the project’s goal and what it is trying to achieve> (maximum 3 sentences)

# Structure

<Describe the components of the project, what each part does, and how they interact. If there are multiple workflows, describe them.>

## File Structure

<Provide a general overview of the directories and key files. Don't Do not specify marginal files>  

## <special Files name> (Optional)

If there are special configuration or definition files, mention them and their structure, with a working example.

# Usage

## Quick Start

<Provide basic usage instructions.>  

## <Other Usage Modes and settings> (Optional)

<Identify different ways the code can be used and document them.>  

```

### Notes

* The README must serve as the gateway for users, developers, and anyone seeking to understand the project. It is not a detailed implementation manual.
* Maintain the balance: the reader should know which files to explore to understand the project, but not necessarily how everything is implemented in detail.
* Write concisely and purposefully. Rewrite content as needed, using short, clear sentences.


if you need to update the readme:

1. Review the README and note which files need to be checked for changes.
2. Go through each relevant file. If it has changed, stop, update the README accordingly, then continue with the next file.

Guidelines for updateing:

* Do not reinvent the wheel. Keep the existing structure. Your role is to update, not to restructure.
* The README serves as a gateway for users, developers, and anyone who wants to understand the project. It is not a detailed implementation manual. Maintain the balance: a reader should know which file to look at for details, but not necessarily how things are implemented there.


