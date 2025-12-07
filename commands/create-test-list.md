You are required to meticulously analyze the service under consideration and generate a structured list of required tests across three distinct categories: **E2E**, **Module**, and **Unittest**.

The core challenge is navigating the system's dependencies:
* **Acknowledge External Services:** Explicitly distinguish between external services whose mechanics are **known** and those that are **unknown**. Do not invent information for the unknown. Instead, articulate the dependencies clearly.
* **Minimize Mocks:** The plan should prioritize **real-world execution** over mocking wherever feasible, maximizing the use of actual running services and data structures.

---

### 1. 🌐 End-to-End (E2E) Tests
**Goal:** Exhaustive verification of the entire system's functionality in a live environment.
* **Scope:** Identify tests that exercise the service from start to finish, reflecting **all business use cases** and **end-user scenarios**.
* **Condition:** These tests must access **real services** and **live information**. All dependent services must be assumed operational.
* **Requirement:** List the E2E test scenarios, ensuring they cover the complete spectrum of the service's intended usage.

### 2. 🧩 Module Tests
**Goal:** Focused testing of complex logic within libraries or critical functions that involve interaction with external services. This is the most complex and critical section.
* **Scope:** Analyze all significant **modules/libraries** and **complex functions** that communicate with other services.
* **Requirement:** For each identified test, provide an **explicit dependency annotation** detailing the required external environment.
    * **Type 1: Generic Access Dependency:** If the test only requires access to a service (e.g., Elasticsearch) without caring about the data content, state this:
        > *Example Annotation:* `Requires access to Elasticsearch.`
    * **Type 2: Specific Data Dependency:** If the test's successful execution relies on a specific data structure or content within the external service, state the exact requirement:
        > *Example Annotation:* `Requires access to Elasticsearch with the data structure: { specific_fields: type } for scenario X.`
* **Handling Unknowns:** For dependencies on external services where the interaction details are **unknown**, specify the different possibilities or clearly mark the area for further investigation:
    > *Example Annotation:* `Dependency on Service Z. Interaction mechanism is unknown (Options: REST API/RPC/Queue). Needs clarification.`

### 3. 🔬 Unittest
**Goal:** Focused testing of complex, internal, single-purpose unit functions that handle intricate logic or potential edge cases.
* **Scope:** Limit this to unit functions that perform a **complex, non-trivial, or recently modified operation**. Avoid testing simple, universally known functions (e.g., basic getters/setters).
* **Exception:** If a function's **only external access** is a simple connection to a **data structure** (e.g., an in-memory cache) or to **S3** (for basic file I/O), it should remain classified as a Unittest, prioritizing real access over mocking if possible.
* **Requirement:** Identify and list the critical unit functions requiring tests, emphasizing complexity and change history as the primary criteria for inclusion.

---

**Output Format:** Provide the list of tests strictly categorized under the three headings, following the constraints on dependencies and the goal of real-world testing.
