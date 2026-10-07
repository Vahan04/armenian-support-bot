# Armenian Support Bot

Milestone 1 builds the evaluation foundation for a multilingual customer-support
bot for Armenian small businesses.

The current sample business is **Ararat Books**, a fictional bookstore with
products and FAQs in `data/sample_store/`. The evaluation set contains 40 base
questions in four forms:

- Armenian script (`hy`)
- Russian (`ru`)
- Armenian transliteration (`translit`)
- Mixed Latin/Russian/Armenian (`mixed`)

That produces 160 JSONL rows. Armenian and transliterated rows have
`needs_native_check: true`; they are intentionally not presented as native-verified.

## Run the milestone

```bash
cd armenian-support-bot
python3 -m eval.run_eval
python3 -m pytest
```

The evaluator writes:

- `results/evaluation_by_question.csv`
- `results/summary_by_form.csv`
- `results/accuracy_by_form.png`

The retrieval benchmark is a transparent lexical baseline. It checks whether the
expected product or FAQ document appears in the top three results. Answer checks
verify expected facts, prices, stock markers, and refusal behavior without
inventing an LLM score. The evaluator has an optional LLM-judge interface, but it
is disabled in this milestone to keep runs deterministic and free.
