---
name: langchain
description: 'LangChain/LangGraph orchestration patterns: chains, agents, tools, memory, RAG, callbacks, streaming, error handling, multi-tenant isolation. Trigger: When implementing LLM orchestration, building agentic workflows, or integrating LangChain/LangGraph with FastAPI.'
version: 1.1
metadata:
  phase:
    - construction
  layer:
    - backend
  enforcement: mandatory
  depends_on:
    - costos-llm
    - observabilidad
  consumed_by:
    - agent-backend
    - agent-fullstack
    - pgvector
  agent_roles:
  - delivery-agent
  validation_profile: architecture
  mcp_usage: context7
---

## Purpose

Define the patterns for LLM orchestration with LangChain and LangGraph in the framework. Covers chain composition, agent patterns, tool integration, memory management, RAG pipelines, callback handlers for observability, streaming responses, error handling, and multi-tenant isolation. This skill ensures consistent patterns for building agentic applications.

## When to use this skill

Activate this skill when:

- Implementing LLM orchestration with LangChain or LangGraph
- Building agentic workflows (ReAct, Plan-and-Execute, etc.)
- Creating custom tools for agents
- Implementing RAG (Retrieval-Augmented Generation) pipelines
- Setting up conversation memory with pgvector
- Integrating LangChain with FastAPI endpoints
- Implementing streaming responses from LLMs
- Adding observability to LLM calls (Langfuse, OpenTelemetry)

**Do not** activate when:

- Only using direct LLM API calls without orchestration
- Working with frontend code (use `react`/`react-services` or `angular`/`angular-services`)
- Implementing basic CRUD operations (use `backend-api`)

## Relation to other skills

| Skill | Relation | Description |
|-------|----------|-------------|
| `costos-llm` | Complementaria | Token tracking and cost management for LLM calls |
| `observabilidad` | Complementaria | OpenTelemetry + Langfuse for LLM observability |
| `database-modeling` | Predecesora | pgvector for embeddings and memory storage |
| `authentication` | Complementaria | Multi-tenant isolation for agent sessions |
| `api-resilience` | Complementaria | Retry and fallback for LLM calls |

## Critical Rules

1. **Use LangGraph for complex workflows** — LangChain chains for simple pipelines, LangGraph for stateful multi-agent systems
2. **Always use callbacks** — Every LLM call must have callbacks for observability (Langfuse, OpenTelemetry)
3. **Multi-tenant isolation** — All memory, tools, and agent state must be isolated by tenant_id
4. **Streaming by default** — Use streaming for all user-facing LLM responses
5. **Tools are functions** — All tools must be typed Pydantic models with clear input/output schemas
6. **Memory in pgvector** — Use PostgreSQL + pgvector for conversation memory, not in-memory stores

## What the agent must do

1. **Define the orchestration pattern** — Chain vs Agent vs Graph
2. **Create tools with schemas** — Pydantic models for inputs/outputs
3. **Configure memory** — pgvector for embeddings, Redis for session state
4. **Add callbacks** — LangfuseCallbackHandler + OpenTelemetry
5. **Implement streaming** — Async generators for SSE/WebSocket
6. **Handle errors** — Fallback models, retry logic, graceful degradation
7. **Isolate by tenant** — tenant_id in all memory queries and tool context

## Code patterns

### LangChain Chain with FastAPI

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langfuse.callback import CallbackHandler
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    tenant_id: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    langfuse_handler = CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        session_id=request.session_id,
        metadata={"tenant_id": request.tenant_id}
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        streaming=True
    )
    
    chain = prompt | model | StrOutputParser()
    
    response = await chain.ainvoke(
        {"input": request.message},
        config={"callbacks": [langfuse_handler]}
    )
    
    return ChatResponse(response=response, session_id=request.session_id)
```

### LangGraph Agent with Tools

```python
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    tenant_id: str
    next_action: str

@tool
def search_database(query: str, tenant_id: str) -> str:
    """Search the tenant's database for information."""
    # Implementation with tenant isolation
    return f"Results for '{query}' in tenant {tenant_id}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    # Implementation
    return f"Email sent to {to}"

tools = [search_database, send_email]
model = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def agent_node(state: AgentState) -> AgentState:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile()
```

### RAG Pipeline with pgvector

```python
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough

class RAGPipeline:
    def __init__(self, tenant_id: str):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = PGVector(
            embeddings=self.embeddings,
            connection=settings.DATABASE_URL,
            collection_name=f"tenant_{tenant_id}_documents"
        )
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        self.model = ChatOpenAI(model="gpt-4o-mini")
    
    async def query(self, question: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer based on the context:\n\n{context}"),
            ("human", "{question}")
        ])
        
        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.model
        )
        
        return await chain.ainvoke(question)

# Usage in FastAPI
@router.post("/rag/query")
async def rag_query(request: RAGRequest):
    pipeline = RAGPipeline(tenant_id=request.tenant_id)
    response = await pipeline.query(request.question)
    return {"response": response}
```

### Streaming with SSE

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    model = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    chain = prompt | model
    
    async def generate():
        async for chunk in chain.astream({"input": request.message}):
            yield f"data: {json.dumps({'text': chunk.content})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
```

### Memory with pgvector

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_core.chat_history import InMemoryChatMessageHistory

class TenantMemoryManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.histories: dict[str, InMemoryChatMessageHistory] = {}
    
    def get_history(self, tenant_id: str, session_id: str) -> InMemoryChatMessageHistory:
        key = f"{tenant_id}:{session_id}"
        if key not in self.histories:
            self.histories[key] = InMemoryChatMessageHistory()
        return self.histories[key]
    
    def get_vectorstore(self, tenant_id: str) -> PGVector:
        return PGVector(
            embeddings=self.embeddings,
            connection=settings.DATABASE_URL,
            collection_name=f"tenant_{tenant_id}_memory"
        )

# Usage
memory_manager = TenantMemoryManager()

@router.post("/chat/with-memory")
async def chat_with_memory(request: ChatRequest):
    history = memory_manager.get_history(request.tenant_id, request.session_id)
    
    # Use history in chain
    chain = prompt | model
    
    response = await chain.ainvoke(
        {"input": request.message},
        config={"chat_history": history}
    )
    
    return {"response": response}
```

### Error Handling with Fallback

```python
from langchain_core.runnables import RunnableWithFallbacks
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

primary_model = ChatOpenAI(model="gpt-4o")
fallback_model = AzureChatOpenAI(deployment_name="gpt-4o-backup")

resilient_chain = RunnableWithFallbacks(
    runnable=primary_model,
    fallbacks=[fallback_model]
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_with_retry(chain, input_data):
    try:
        return await chain.ainvoke(input_data)
    except Exception as e:
        # Log to Langfuse
        langfuse.score(name="error", value=1, comment=str(e))
        raise
```

## Decision table

| Situation | Wrong response | Expected response |
|-----------|---------------|-------------------|
| Simple Q&A | LangGraph agent | LangChain chain |
| Multi-step workflow | Single chain | LangGraph StateGraph |
| Need memory | In-memory dict | pgvector + tenant isolation |
| Need streaming | Return full response | Async generator + SSE |
| Tool calling | String parsing | Pydantic @tool decorator |
| Error handling | Let it fail | Fallback model + retry |

## Verification checklist

- [ ] LangChain/LangGraph properly imported
- [ ] Callbacks configured (Langfuse + OpenTelemetry)
- [ ] Multi-tenant isolation implemented
- [ ] Streaming for user-facing responses
- [ ] Tools have Pydantic schemas
- [ ] Memory uses pgvector
- [ ] Error handling with fallbacks
- [ ] Cost tracking via costos-llm
