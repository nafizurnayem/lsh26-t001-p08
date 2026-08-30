# Third-Party Material and AI Disclosure

Material frameworks, libraries, starters, templates, UI kits, fonts, icons and
assets used in this repository.

| Name | Version or source URL | Licence | Used for |
|---|---|---|---|
| Streamlit | `>=1.44` — <https://github.com/streamlit/streamlit> | Apache-2.0 | Web UI, tabs, tables, file upload, deployment target |
| pandas | `>=2.0` — <https://github.com/pandas-dev/pandas> | BSD-3-Clause | Table building and the cell styling in the results view |
| Python standard library | 3.12 — `json`, `decimal`, `random`, `pathlib` | PSF-2.0 | Parsing, half-up rounding, the seeded cohort generator |
| Inter (web font) | <https://fonts.google.com/specimen/Inter> | SIL Open Font License 1.1 | Page typography, loaded from Google Fonts |
| Material Symbols | Bundled with Streamlit | Apache-2.0 | Streamlit's own interface icons |
| `P08_school_results_public.json` | Organizer submission kit, `fixtures/` | Supplied for the event | Sample data. **Not redistributed in this repository** — judges upload it through the sidebar |

No UI kit, template, starter repository or generated scaffold was used. The
CSS, the rule engine, the generator and the tests were written during the
event window.

## AI tools

| Tool | Used for | How the output was verified |
|---|---|---|
| Claude Code (Anthropic, Opus 5) | Drafting `engine.py`, `app.py`, `test_engine.py` and the documentation from the team's specification of the P08 rules | Every rule was checked against the organizers' published clarifications; `python engine.py` reproduces all seven published population counts over the full fixture (1,765 students); `python test_engine.py` runs 17 rule checks covering each documented trap; five students were re-computed by hand |

The same disclosure is recorded in `evaluation-manifest.json`. The team is
responsible for understanding, testing and defending everything submitted.

## Original-work statement

Everything not declared in this file or `EVENT.md` was created by the
registered team during the event window.
