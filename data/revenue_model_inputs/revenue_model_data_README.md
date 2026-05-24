# Revenue Model Data Files

Prepared: 2026-05-23

## Files

- `frontier_llm_price_observations.csv`: Historical frontier and frontier-adjacent launch price observations. Use this file to support the token-price decay half-life estimate and historical pricing discussion.
- `revenue_pricing_scenarios.csv`: Direct revenue-pricing inputs under the requested assumption that monetized inference is priced identically to OpenAI `gpt-5.4-pro` daily prices.
- `revenue_model_assumptions.csv`: Model parameters, recommended values, sensitivities, distributions, and formulas.
- `revenue_inference_model_notes.md`: Planning-doc-ready narrative explanation.
- `revenue_inference_model_assumptions.docx`: Copy/paste-friendly Word version.
- `revenue_inference_model_assumptions.pdf`: Copy/paste-friendly PDF version.

## Revenue Pricing Assumption

Per request, the revenue model should not use a market-basket average price. It should assume all monetized frontier inference is priced identically to OpenAI `gpt-5.4-pro` daily prices.

Current standard OpenAI `gpt-5.4-pro` pricing:

```text
input_price = 30 USD / 1M input tokens
output_price = 180 USD / 1M output tokens
```

Requested revenue token mix:

```text
input_share = 2/3
output_share = 1/3
```

Standard blended revenue price:

```text
blended_revenue_price =
  (2/3) * 30
  + (1/3) * 180
  = 80 USD / 1M served tokens
```

Daily revenue:

```text
revenue_capacity_tokens_t =
  max(0, total_capacity_tokens_t - training_allocated_capacity_tokens_t)

revenue_t =
  (revenue_capacity_tokens_t / 1_000_000)
  * blended_revenue_price_t
```

## Scenario Values

The `revenue_pricing_scenarios.csv` file includes these current blended prices:

| Scenario | Blended revenue price |
|---|---:|
| Standard | $80 / 1M served tokens |
| Batch/Flex | $40 / 1M served tokens |
| Priority | $160 / 1M served tokens |
| Long context >272K input | $130 / 1M served tokens |
| Regional/data residency | $88 / 1M served tokens |

## Remaining Modeling Assumptions

Token-price decay half-life:

```text
recommended = 60 days
sensitivity = 30 / 45 / 60 / 90 / 120 days
distribution = LogNormal(median=60, p10=35, p90=120)
```

Per-release quality multiplier:

```text
recommended = 1.25
sensitivity = 1.10 / 1.25 / 1.50 / 1.80
distribution = LogNormal(median=1.25, p10=1.08, p90=1.65)
```

## Source Links

- OpenAI GPT-5.4 Pro model/pricing page: https://developers.openai.com/api/docs/models/gpt-5.4-pro
- OpenAI GPT-5.4 launch/pricing page: https://openai.com/index/introducing-gpt-5-4/
- OpenRouter market-share rankings: https://openrouter.ai/rankings#market-share
- OpenRouter State of AI usage study: https://openrouter.ai/state-of-ai
