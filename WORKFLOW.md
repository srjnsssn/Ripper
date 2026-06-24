# WORKFLOW.md - Strict Iterative Development Protocol

## 1. Core Philosophy
This project operates on a Strict Iterative Development Loop (The Loop). As an AI agent (OpenCode), your execution must be atomic, precise, and linearly constrained. Do not write code for entire systems at once. You must wait for human validation before proceeding to the next step.

## 2. The Loop Execution Steps

### Step 1: Scope Isolation (Wait for Prompt)
* ONLY execute the specific, isolated task requested in the user's prompt.
* DO NOT write code for adjacent features.
* DO NOT modify files outside the immediate scope of the current task.

### Step 2: Context Retrieval
* Before generating code, silently verify the task requirements.
* Cross-reference `AGENT.md` (Skills), `spec.md` (Requirements), and `design.md` (Architecture/UI).
* Strictly apply the rules found in the `.agents/skills/` directory relevant to the current task.

### Step 3: Atomic Generation
* Output the exact, production-ready code required for the isolated task.
* **Prohibition:** DO NOT use placeholders like `// TODO: implement later` or `pass` unless explicitly requested to draft a skeleton.
* Ensure strict type safety (TypeScript/Python), proper imports, and alignment with the project's visual/structural guidelines.

### Step 4: Halt for Validation
* Once the atomic code is generated, **STOP**.
* Wait for the human developer to execute the code locally and provide feedback (success confirmation, visual correction, or terminal traceback).

### Step 5: Root-Cause Refinement
* If an error log or traceback is provided, DO NOT blindly guess.
* Analyze the root cause based on the stack trace.
* Provide the specific fix. Do not rewrite the entire file unless structurally necessary.
* Repeat Steps 4 and 5 until the human confirms the component works flawlessly.

### Step 6: Loop Closure
* The loop is closed only when the human confirms success.
* The human will handle the `git commit` locally.
* Await the next isolated task prompt.

## 3. Strict Prohibitions
* **No Unsolicited Refactoring:** Do not refactor existing code unless instructed.
* **No Hallucinated Dependencies:** Only use libraries defined in the project configuration or explicitly approved.
* **No Skipped Steps:** Never assume a test passed; always wait for human input.
