# Card-isolation follow-up: new maintenance version, not automatic retry

Preserve both clarification_followup outputs: C01 Baseline completed; C01 Improved failed because the model assigned globally valid question IDs to an unrelated card. The runner stopped. Do not replace that failure or count the corrected version as its original result.

Change only the common final checker: withhold a card with an unrelated question assignment, expose the limitation and retain independently validated recommendations. Do not transfer the question, invent an answer or perform another model call automatically. Unknown/supplied fact references, schema failures and unreviewed cards still fail validation. Add an offline regression using the saved failed response, explicitly marked replay, to confirm this protection. This regression is not a genuine new model output.

Run four fresh C01/C05 model calls in a new folder, using the prior clarification expectations and settings/corpus unchanged. Each first result is saved, without replacement or retry. Review the changed output and missing questions against the source. Original first-audit 12 outputs and the intermediate failure remain available. Check the other four cases have identical model requests/evidence and replay their saved decisions through the new checker as offline regression only. Final hosted generation is verified separately.
