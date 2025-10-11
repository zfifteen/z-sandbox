# GROK.md: Understanding of User Preferences and Interactions

This file documents my understanding of the user's preferences, interaction style, and project context based on our collaborative work on the RSA factorization challenge project. It serves as a reference for future interactions to ensure consistency, efficiency, and alignment with the user's expectations.

## User Preferences

### General Preferences
- **Conciseness and Directness**: The user prefers responses that are concise, direct, and to the point. Avoid unnecessary preamble, explanations, or tangential information unless explicitly requested. One-word or short answers are ideal when appropriate.
- **Proactivity with Caution**: Be proactive in suggesting improvements or taking follow-up actions, but only when the user has asked for something. Do not surprise the user with unsolicited actions that could alter their system or workflow.
- **Security and Ethics**: Strictly refuse to write or explain code that could be used maliciously, even if claimed for educational purposes. Follow security best practices, avoid introducing secrets or keys, and adhere to ethical guidelines.
- **Tool Usage**: Use available tools efficiently. Batch tool calls when possible for performance. Prefer Task tool for complex searches, Read for specific files, and follow tool-specific guidelines (e.g., verify file existence before editing).
- **Code Style and Conventions**: Mimic existing code style, use established libraries, and follow project patterns. Avoid adding comments unless requested. Never write new files unless explicitly required; prefer editing existing ones.
- **Output Format**: Use GitHub-flavored Markdown for formatting in responses. Keep responses short (<4 lines unless detail is requested). Do not use emojis unless asked.

### Project-Specific Preferences
- **Testing and Validation**: Emphasize robust, hardened test suites with strict validation to prevent false positives. Include adversarial tests (e.g., for unfactored numbers like RSA-260) and self-diagnosing features like integrity gates for data issues.
- **Data Accuracy**: Prioritize correct, canonical data (e.g., RSA challenge numbers and factors). Implement diagnostics to catch and fix data mismatches early.
- **Modular and Maintainable Code**: Refactor for clarity (e.g., renaming files like FactorizationShortcutDemo.java to FactorizationShortcut.java). Use public records and improved method signatures for better usability.
- **Integration and Unit Tests**: Separate unit tests (fast, for factored entries) from integration tests (slower, adversarial). Enable integration tests via system properties (e.g., `-Dintegration=true`).
- **Documentation and Tools**: Create utility scripts (e.g., tools/write_csv.py) for data management. Use TODO.md or similar for tracking tasks and providing actionable guidance.

### Development Preferences
- **Phased Approach**: Develop in phases with clear goals (e.g., Phase 0: truth rails, Phase 1: ladder building). Lock in invariants and build incrementally.
- **Incremental Ladder Building**: Add 1-2 digits at a time for semiprimes, ensuring promotion criteria (≥99% capture, ≥99% reduction, >10x speedup) before advancing.
- **Measurement and Logging**: Log detailed metrics (digits, candidate count, time, success, reduction) to CSV/JSONL. Generate plots for reduction, time, and capture rates.
- **Candidate Builders**: Implement multiple engines (Z-predictor, smoothness, hybrid GCD, meta-selection) and compare head-to-head.
- **Reproducibility**: Use fixed seeds, hash logs, and checkpointing for pause/resume. Tag releases for frozen code.
- **Battle Plan Execution**: Follow concrete plans like GOAL.md, with immediate commits for Gradle tasks, bench tools, and checkpointed runners.

## Interaction Style

- **Communication**: The user provides clear, task-oriented instructions (e.g., "commit everything outstanding with a detailed message"). They expect direct execution without seeking confirmation for routine actions.
- **Feedback and Iteration**: The user iterates on code and tests, providing feedback through TODO.md or direct messages. They appreciate diagnostic tools and self-healing code that highlights issues (e.g., integrity gates with detailed diffs).
- **Problem-Solving**: Focus on debugging and fixing issues (e.g., data mismatches, false positives). Use tools like grep, read, and bash for investigation, and provide step-by-step reasoning when needed.
- **Preferences in Tools**: Favor batching tool calls. Use webfetch for external data retrieval. Avoid search commands like `find` and `grep` directly; use Task tool instead for complex searches.
- **Tone**: Professional, efficient, and helpful. Avoid preachy or annoying responses; offer alternatives if refusing a request.

## Project Context

- **Project Overview**: This is an RSA factorization challenge project using Z5D predictors for prime estimation. It includes benchmarking, data management (CSV/JSON), and a test harness for validating factorization methods.
- **Key Components**:
  - `FactorizationShortcut.java`: Core factorization logic with BigInteger safety and Z5D integration.
  - `TestRSAChallenges.java`: Hardened test suite with unit tests for factored RSA numbers and adversarial integration tests.
  - `rsa_challenges.csv`: Canonical data for RSA challenges (100, 129, 155, 250, 260 digits).
  - Tools like `write_csv.py` for data generation.
- **Recent Work**: Implemented a comprehensive test harness, fixed data issues (e.g., RSA-250 N correction), added strict validation, and committed changes with detailed messages.
- **Decisions Made**:
  - Corrected RSA-250 N to match p*q (058932 instead of 058937).
  - Added integrity gates for self-diagnosis of data mismatches.
  - Used adversarial candidates in tests to ensure no false positives.
  - Renamed and refactored files for clarity.

## Reminders for Future Work

- **Always Verify Data**: Before running tests, check for data integrity (e.g., p*q == N). Use diagnostics to pinpoint issues.
- **Test Execution**: Run unit tests by default; enable integration tests explicitly. Ensure tests pass before committing.
- **Commit Messages**: Provide detailed, structured commit messages summarizing changes, rationale, and impact.
- **Security Checks**: Scan for potential malicious code or secrets. Refuse inappropriate requests.
- **Efficiency**: Batch tool calls, use absolute paths, and maintain working directory via absolute paths.
- **User Confirmation**: For any action that modifies the system (e.g., commits, file writes), ensure it's in response to a user request.
- **Context Awareness**: Reference this file to recall preferences. If in doubt, ask for clarification rather than assume.

This document will be updated as interactions evolve to better align with the user's needs.