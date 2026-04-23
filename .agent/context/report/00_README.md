# Report Content Files

One file per IEEE section. Use these as source content when writing the final .tex / Word document.

| File | Section |
|---|---|
| 01_title_abstract_keywords.md | Title, Abstract, Keywords |
| 02_introduction.md | I. Introduction |
| 03_related_work.md | II. Related Work |
| 04_dataset.md | III. Dataset |
| 05_methodology.md | IV. Methodology (includes 3-model pipeline detail) |
| 06_system_architecture.md | V. System Architecture |
| 07_chatbot.md | VI. Conversational Triage Chatbot (full Vapi architecture) |
| 08_ui_design.md | VII. User Interface Design |
| 09_implementation_details.md | VIII. Implementation Details |
| 10_results_discussion.md | IX. Results and Discussion |
| 11_limitations_future_work.md | X. Limitations and Future Work |
| 12_conclusion.md | XI. Conclusion |
| 13_references.md | XII. References |

## Key changes from the original PDF

- Abstract: removed false "confidence score" claim; updated to mention 3 models
- Introduction: 4 contributions instead of 3; Vapi replaces LangGraph/Ollama description
- Methodology: entirely new Section C covering all 3 models, comparison table, routing logic
- System Architecture: added superadmin router, JWT auth, updated health endpoint
- Chatbot: complete rewrite — Vapi architecture, stepRef pattern, patient ID normalization
- UI Design: removed 3-digit session code reference (feature was removed from implementation)
- Results: placeholder rows for Acuity 2/4/5 recall — fill from ml/logs/ before finalizing
- References: added Vapi [10] and RapidFuzz [11]

## One thing still needed from you
Fill in the Acuity 2, 4, 5 recall values in 10_results_discussion.md from your ml/logs/ cross-validation output.
