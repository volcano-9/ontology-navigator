# Ontology RAG Skill

This skill provides semantic search capabilities for the Ontology Navigator expert.

## Features
- Semantic search using TF-IDF + cosine similarity (zero-dependency)
- Context injection for system prompt enhancement
- JSON-formatted results for programmatic use

## Usage

### Direct Skill Call (WorkBuddy)
```python
# In a WorkBuddy conversation:
result = skill_main("query_knowledge", {"query": "反模式", "top_k": 3})
```

### CLI Usage
```bash
python ontology_rag.py query "身份解析" 2
```

## Files
- `ontology_rag.py` - Core vector store implementation
- `ontology_rag_inject.py` - Context builder CLI
- `ontology_rag_integration.py` - Embedding extension point
- `ontology_rag_skill.py` - Skill interface
- `ontology_vectorstore.json` - Persistent vector store data