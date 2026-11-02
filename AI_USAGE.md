# Generative AI Usage Statement

## Tools used

The group used OpenAI ChatGPT/Codex and Anthropic Claude as coding and writing assistants during the project.

## How the tools were used

Generative AI was used to help translate the group's research plan into Python, draft and debug parts of the data-cleaning, exploratory-analysis, matching, inference, bootstrap, permutation-test, and robustness code, and improve the clarity of documentation and result interpretations. It also helped draft the initial presentation structure, wording, editable charts, and speaker notes from the group's verified aggregate results. Substantial portions of the initial code were suggested by an AI tool in response to the team's specified research question, matching rules, statistical methods, and desired outputs.

The group, rather than the AI tools, selected the research question, obtained the Orbis data, decided the sample restrictions, chose the matching variables and robustness specifications, and made the final modelling and reporting decisions.

## Human verification

Group members executed the code themselves in the project environment and did not treat generated code or prose as automatically correct. Verification included:

- checking row counts, identifiers, duplicate records, units, missing values, and listing-status totals after merging and cleaning;
- comparing notebook outputs with the saved aggregate CSV tables;
- confirming that listed-firm subsidiaries were excluded consistently;
- checking that controls were not reused and that matched firms shared the required strata;
- comparing age balance before and after matching;
- fixing incorporation-year parsing and nullable-value errors encountered during execution;
- re-running notebooks from top to bottom with fixed random seeds;
- checking sign-test, permutation-test, bootstrap, quantile-gap, and robustness results for consistency; and
- revising AI-drafted explanations and presentation slides to match the executed results and the group's intended interpretation.

All final outputs, modelling choices, interpretations, and any remaining errors are the responsibility of the group members. The results are reported as associations and not as causal effects.

## Data confidentiality

No passwords, API keys, or SMU credentials were provided to the AI tools. Work involving the licensed Orbis extract was conducted within the authorised local/private project environment. Firm-level data must not be copied into public AI prompts or published in a public repository.
