# Hackathon AI Agent System - Requirements Document

## Project Overview
A flexible multi-agent AI system built with LangChain and LangGraph that can be quickly adapted to any use case during a hackathon competition. The system features configurable AI agents, a visual workflow UI, and CSV-based data handling.

## Core Requirements

### 1. Multi-Agent Architecture
- **Framework**: LangChain + LangGraph for agent orchestration
- **Agent Configuration**: Agents defined via Python classes AND JSON configuration files
- **AI Providers**: 
  - OpenAI (GPT-4/GPT-3.5) for some agents
  - Google Gemini for other agents
  - Each agent should be configurable to use either provider
- **Agent Types to Support**:
  - Data Analyst Agent (analyzes CSV data)
  - Research Agent (web search/information gathering)
  - Coordinator Agent (orchestrates other agents)
  - Task Executor Agent (performs specific tasks)
  - Reporter Agent (generates final outputs)

### 2. JSON-Based Agent Configuration
Create a `agents_config.json` file structure:
```json
{
  "agents": [
    {
      "id": "agent_1",
      "name": "DataAnalyst",
      "type": "analyst",
      "llm_provider": "openai",
      "model": "gpt-4",
      "temperature": 0.3,
      "system_prompt": "You are a data analyst...",
      "tools": ["csv_reader", "calculator"],
      "max_iterations": 5
    },
    {
      "id": "agent_2",
      "name": "Researcher",
      "type": "researcher",
      "llm_provider": "gemini",
      "model": "gemini-pro",
      "temperature": 0.7,
      "system_prompt": "You are a researcher...",
      "tools": ["web_search"],
      "max_iterations": 3
    }
  ],
  "workflow": {
    "start_node": "agent_1",
    "edges": [
      {"from": "agent_1", "to": "agent_2", "condition": "analysis_complete"},
      {"from": "agent_2", "to": "end"}
    ]
  }
}
```

### 3. File Structure
```
hackathon-ai-agents/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── agents_config.json
│   └── workflow_config.json
├── data/
│   ├── input/
│   │   └── sample_data.csv
│   └── output/
│       └── results.json
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── data_analyst_agent.py
│   │   ├── researcher_agent.py
│   │   ├── coordinator_agent.py
│   │   └── agent_factory.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── csv_tools.py
│   │   └── web_tools.py
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── graph_builder.py
│   │   └── workflow_executor.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── openai_provider.py
│   │   └── gemini_provider.py
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       └── logger.py
├── ui/
│   ├── app.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── workflow.js
│   └── templates/
│       └── index.html
└── tests/
    ├── __init__.py
    └── test_agents.py
```

### 4. CSV Data Handling
- **CSV Loader**: Utility to load and parse CSV files from `data/input/`
- **Data Validation**: Basic validation for CSV structure
- **Data Access**: Agents should access CSV data through tools
- **Sample CSV Structure**: Include a sample CSV with common fields (id, name, value, category, date)
- **Dynamic Schema**: System should handle different CSV schemas

### 5. LLM Provider Configuration
**Environment Variables** (`.env` file):
```
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_gemini_key_here
DEFAULT_LLM_PROVIDER=openai
LOG_LEVEL=INFO
```

**Provider Implementation**:
- Abstract base class for LLM providers
- OpenAI provider using `langchain-openai`
- Gemini provider using `langchain-google-genai`
- Factory pattern to select provider based on config

### 6. LangGraph Workflow
- **Graph Definition**: Use LangGraph's `StateGraph` to define agent workflow
- **State Management**: Maintain conversation state and intermediate results
- **Conditional Edges**: Support branching logic based on agent outputs
- **Visualization**: Export graph structure for UI visualization
- **Checkpointing**: Save workflow state for debugging

### 7. Web UI Requirements
**Technology**: Streamlit or Flask (Streamlit preferred for simplicity)

**Features**:
- **Workflow Visualization**: 
  - Display agent nodes and connections
  - Show current execution status
  - Highlight active agent
- **Configuration Panel**:
  - Upload/modify agents_config.json
  - Select CSV file to process
  - Set execution parameters
- **Execution Controls**:
  - Start/Stop workflow
  - Step-by-step execution mode
  - Reset workflow
- **Output Display**:
  - Real-time logs
  - Agent responses
  - Final results
- **File Upload**: Upload new CSV files
- **Export**: Download results as JSON/CSV

### 8. Code Modularity & Explainability
- **Single Responsibility**: Each module has one clear purpose
- **Clear Naming**: Descriptive variable and function names
- **Documentation**: 
  - Docstrings for all classes and functions
  - Inline comments for complex logic
  - Type hints throughout
- **Configuration Over Code**: Use JSON configs instead of hardcoding
- **Easy Adaptation**: 
  - Clear instructions in README on how to add new agents
  - Template files for creating new agent types
  - Configuration examples for common use cases

### 9. Dependencies
```
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-google-genai>=0.0.6
langgraph>=0.0.20
streamlit>=1.30.0  # OR flask>=3.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
pydantic>=2.0.0
aiohttp>=3.9.0
requests>=2.31.0
```

### 10. Key Features to Implement
- [x] **Agent Factory**: Dynamically create agents from JSON config
- [x] **Tool Registry**: Register and manage tools available to agents
- [x] **Workflow Builder**: Build LangGraph workflow from JSON definition
- [x] **State Persistence**: Save/load workflow state
- [x] **Error Handling**: Comprehensive error handling and logging
- [x] **Testing**: Unit tests for core components
- [x] **Quick Start**: One-command setup and execution

## Implementation Priority

### Phase 1: Core Foundation (CRITICAL)
1. Project structure setup
2. Environment configuration (.env, config loading)
3. LLM provider implementations (OpenAI + Gemini)
4. Base agent class
5. CSV data loader tool

### Phase 2: Agent System (CRITICAL)
1. Agent factory from JSON config
2. Implement 3 basic agent types
3. Tool registry and integration
4. Simple LangGraph workflow (linear: agent1 -> agent2 -> end)

### Phase 3: Workflow Enhancement (IMPORTANT)
1. Complex LangGraph workflows with conditional edges
2. State management and checkpointing
3. Workflow visualization export

### Phase 4: UI (IMPORTANT)
1. Basic Streamlit UI
2. Workflow visualization
3. Configuration editor
4. Log viewer and results display

### Phase 5: Polish (NICE TO HAVE)
1. Advanced UI features
2. Comprehensive testing
3. Documentation improvements
4. Example use cases

## Success Criteria
- [ ] System can create agents from JSON config in under 1 minute
- [ ] Supports both OpenAI and Gemini with easy switching
- [ ] Can process CSV files and use data in agent reasoning
- [ ] LangGraph workflow executes reliably
- [ ] UI clearly shows workflow progress
- [ ] Code structure is simple enough to explain in 5 minutes
- [ ] Can adapt to new use case by modifying JSON config only (no code changes)
- [ ] Complete setup possible in under 5 minutes

## Adaptation Guide for Hackathon Day
When given a new use case:
1. Define required agents in `agents_config.json`
2. Prepare relevant CSV data in `data/input/`
3. Update system prompts for each agent based on use case
4. Configure workflow edges for desired agent interaction
5. Run workflow and iterate on prompts/config
6. Present results via UI

## Notes for AI Coding Assistants
- Prioritize simplicity and readability over optimization
- Use standard patterns (factory, registry, builder)
- Include extensive comments explaining the "why" not just "what"
- Create helper functions for common operations
- All configuration should be external (JSON/env) not hardcoded
- Test each component independently before integration
- Keep the system modular so components can be demoed separately