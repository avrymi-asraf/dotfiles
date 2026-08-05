---
name: coding-principles
description: coding-principles
---
Coding principles.
Code is the way to communicate with the machine, it is critical that it be clear to a person who enters from the outside.
The architecture, structure and names of the objects in the code must tell in the clearest way what is happening in the code. It must be that way.
Updating code - it is sensitive, it must be done gently, not to refactor what you were not asked to do.
3 \ 4 lines must be added at the beginning of the file that explain how this file fits into all the existing code.
Building code requires checking that it actually connects and works.
Code should be elegant, cleverness, tricks, sophisticated things should not be in the code, they should only be in certain cases.
Uniformity of concepts and names - the choice of names is very important. If a component in the system has a name, that same name must be preserved every time it is mentioned, everywhere it appears. One concept, one name. This is what makes code easy to understand for someone reading it from the outside.
For example, if a service has tests and dedicated auxiliary functions that support those tests, the same name should run through all of them - the service, its tests, and its helpers - so the reader quickly understands what the auxiliary functions serve. Do not invent a new synonym for something that already has a name; reusing the established name is clarity, inventing variants is confusion.
The way of working is - building something, once it is assembled - you make sure that it actually works and continue.
This is a research and development project, it is critical that it be clean. There is no need to maintain backward compatibility at all.
We will always strive for there to be only one clear and direct way to use the code. We will only deviate from this when necessary.