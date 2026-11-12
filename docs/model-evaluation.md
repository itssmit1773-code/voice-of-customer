# Classification and error review

The offline NLP pipeline first ran a multinomial Naive Bayes benchmark using word unigrams and adjacent bigrams. The benchmark used Laplace smoothing, class priors, and a top-two log-score margin. A small training library supplied eight phrases per theme and six cues per sentiment or severity label. It handled paraphrases poorly, so the shipped dashboard uses an explicit taxonomy. Themes follow the first clause with a recognizable product signal. Multiple themes in that clause or no signal yield `review`. Sentiment needs explicit tone or neutral context cues. Severity looks for blocked work, workarounds, or explicit low impact. Review flags cover uncertain labels, blockers, and selected exposure cues.

## Evidence sets

- **Development, 42 examples.** Originally used to compare the benchmark. These examples informed taxonomy design and are reported as development results.
- **Audit, 24 examples.** New fictional cases authored after the main taxonomy rules were written. This set includes paraphrases, multi-topic text, no-context text and negation. Both classifiers used the same set. One access-exposure routing cue for the word “restricted” was extended during build. It changes the routing reason and has no effect on the three label metrics. Labels were assigned by one author, so this audit has no inter-rater agreement measurement.
- **Simulation, 3,510 records.** The source generator emits latent labels and uses a different phrase bank from the statistical training examples. Its templated language and designed cue omissions limit interpretation. The benchmark and decision warehouse never train on the simulation's latent labels. The dashboard also reports slices by channel.

| Audit axis | Correct / 24 | Taxonomy macro F1 | Naive Bayes macro F1 | Taxonomy coverage | Accuracy among accepted |
|---|---:|---:|---:|---:|---:|
| Topic | 20 | 0.825 | 0.252 | 75.0% | 18 / 18 |
| Sentiment | 21 | 0.825 | 0.261 | 79.2% | 19 / 19 |
| Severity | 23 | 0.902 | 0.688 | 91.7% | 22 / 22 |

Accuracy credits a correct `review` when ambiguity is expected. Coverage excludes all predicted `review` rows. Accepted accuracy uses accepted predictions as its denominator. Macro F1 weights each gold class equally and includes `review` when it is a gold class. Perfect accepted accuracy on this small authored set has substantial uncertainty. Simulation topic accuracy was **94.8%**. Blocking recall in simulation was **88.3%** against 721 latent blocker labels. Inspect exact values and per-channel differences in [evaluation.json](../artifacts/evaluation.json).

## Where the rules fail

| Audit record | Failure | Operating response |
|---|---|---|
| A01 | “Authorize” and a suspended assignee indicate an approval issue. The theme rule abstains, although severity routes it as a blocker. | Include unclassified blockers in weekly review and test alternative approval vocabulary. |
| A04 | “The bell” and reminders refer to notifications. There is no matching topic cue. | Ask support to supply product context and add validated vocabulary from reviewed cases. |
| A19 / A21 | Text sizing and timeline contrast have weak product vocabulary. The rules abstain on “Other.” | Keep emerging categories visible via unclassified review and sample recurring language. |
| A24 | “Not blocked” is misread as a blocker cue. A manual workaround cue causes severity to abstain. | Validate negation, quoted language and conflicting cues before production use. |

The July–September queue contains **777 of 1,854** reports with at least one review flag. Review operations should count workload and audit a sample of auto-labeled rows for silent errors. Keep a standing incident route for access exposure. Pattern matching is a supplemental signal and can miss security reports. On real data, restrict raw-text access, redact identifiers, audit by language and channel, and validate against independently labeled feedback before deployment. No external model, credentials, or LLM-generated summaries are used. The prototype is suitable for analyst-assisted exploration of this fictional case.

Source rows and outputs are available in [audit predictions](../artifacts/audit_predictions.csv), [baseline predictions](../artifacts/baseline_audit_predictions.csv) and [simulation errors](../artifacts/simulation_errors.csv).
