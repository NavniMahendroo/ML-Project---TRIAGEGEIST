# X. Limitations and Future Work

## Current Limitations

**Geographic bias** — the training data originates from a single hospital system in Northern Europe. Demographic distributions, coding practices, and ESI scoring conventions may differ significantly from Indian emergency departments, potentially reducing model performance without domain adaptation.

**Offline evaluation only** — the model has been evaluated against a static Kaggle dataset. Prospective clinical validation under real ED conditions—with live patient data, varying nurse behaviour, and concurrent system load—is required before the system is considered for any advisory deployment role.

**English-only chatbot** — the Vapi voice assistant currently operates in English only, limiting accessibility for patients who speak Hindi or regional Indian languages.

**v1.0.2-c accuracy gap** — the history-free fallback model (v1.0.2-c) necessarily produces less accurate acuity predictions than v1.0.2 for patients where history would have been informative. The current implementation selects v1.0.2-c when no history record exists in MongoDB; a future improvement would use a confidence threshold to decide whether the history NaN penalty in v1.0.2 is preferable to v1.0.2-c.

**No real-time vitals ingestion** — vitals are manually entered or spoken by the patient. Bedside IoT monitor integration would eliminate transcription errors and capture continuous vital trends rather than point-in-time snapshots.

## Planned Future Extensions

1. **Fine-tuning on Indian clinical data** — adapt PubMedBERT on Indian clinical notes and Hindi-transliterated chief complaints to improve model calibration for the target deployment population

2. **Multilingual voice support** — integrate Whisper-based speech recognition for Hindi and major regional languages, enabling the chatbot to conduct intake interviews in the patient's native language

3. **Real-time vital sign ingestion** — WebSocket endpoint for bedside IoT monitor integration, allowing the system to ingest continuous HR, SpO2, and BP streams directly rather than relying on patient self-report

4. **Docker containerization** — simplify hospital IT deployment and environment replication across heterogeneous infrastructure

5. **Prospective clinical study** — partnership with an NSUT-affiliated medical centre to measure clinical impact on triage-to-treatment time, inter-rater consistency, and Level 1 miss rate

6. **Confidence-based model selection** — replace the binary history-available/unavailable routing with a confidence-score comparison between v1.0.2 (with NaN history) and v1.0.2-c, selecting the model that produces a higher prediction confidence for each individual case

7. **v1.0.2-b expansion** — extend the complaint classifier beyond 14 body-system classes to finer-grained complaint categories, providing richer routing signals for specialty assignment
