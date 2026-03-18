# smu-genai-language-tutor

A multi-agent language tutor built with LangGraph for SMU's Generative AI with LLMs course. Uses 6 specialized agents (Orchestrator, Diagnostic, Cross-Lingual Transfer, Pedagogy, Student Model, Content Generator) to teach a languages to speakers by leveraging their existing language knowledge.

## Architecture

```
Student Input
      │
      ▼
┌──────────────┐
│  Orchestrator │──── Routes to correct flow
└──────┬───────┘
       │
  ┌────┴────────────────────┐
  ▼                         ▼
Diagnose Flow         Generate Content
  │                         │
  ▼                         ▼
Diagnostic Agent      Content Generator ──→ END
  │
  ▼
Cross-Lingual Transfer Agent
  │
  ▼
Pedagogy Agent
  │
  ▼
Student Model Agent ──→ END
```

## The 6 Agents

| Agent | Role |
|-------|------|
| **Orchestrator** | Routes student input to the correct flow |
| **Diagnostic** | Analyzes errors and classifies them by type |
| **Cross-Lingual Transfer** | Bridges explanations using different languages |
| **Pedagogy** | Decides teaching strategy (hint → scaffold → direct) |
| **Student Model** | Tracks student progress and learning history |
| **Content Generator** | Creates tailored exercises for weak areas |

## Setup

```bash
# Clone the repo
git clone https://github.com/your-team/smu-genai-language-tutor.git
cd smu-genai-language-tutor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run examples
python main.py

# Run interactive mode
python main.py --interactive
```

## Project Structure

```
smu-genai-language-tutor/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py        # Agent 1: Router
│   ├── diagnostic.py          # Agent 2: Error analysis
│   ├── cross_lingual.py       # Agent 3: Language bridging
│   ├── pedagogy.py            # Agent 4: Teaching strategy
│   ├── student_model.py       # Agent 5: Student memory
│   └── content_generator.py   # Agent 6: Exercise creation
├── data/
│   ├── transfer_maps/
│   │   ├── mandarin_to_japanese.json
│   │   └── english_to_japanese.json
│   └── student_profiles/
│       └── demo_profiles.json
├── evaluation/
│   └── test_cases.json
├── graph.py                   # LangGraph wiring
├── state.py                   # Shared state schema
├── main.py                    # Entry point
├── requirements.txt
└── README.md
```

## Languages Covered

- **Target language:** Japanese (JLPT N5 scope)
- **Student's known languages:** Mandarin (native) + English (fluent)
- **Transfer directions:** Mandarin → Japanese, English → Japanese

## Team

SMU Generative AI with LLMs — Group Project