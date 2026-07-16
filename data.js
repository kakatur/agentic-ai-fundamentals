// Course modules for Agentic AI Fundamentals
window.MODULE_COLORS = ["blue", "purple", "teal", "emerald", "amber", "rose", "indigo", "cyan", "orange", "pink", "violet", "lime", "sky", "fuchsia", "green"];

window.MODULES = [
  {
    id: 1,
    title: "Python Fundamentals for AI",
    color: "blue",
    videoCount: 8,
    description: "Master Python essentials needed for AI development - from basics to async programming.",
    playlistUrl: "https://www.youtube.com/playlist?list=PLcEtUFoF7ycg",
    videos: [
      {
        title: "Python Basics for AI: Variables, Types & Control Flow",
        description: "Learn Python fundamentals including variables, data types, control structures, and functions with practical AI examples.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=Ct4fFvOF8as",
        thumbnailUrl: "https://i.ytimg.com/vi/Ct4fFvOF8as/maxresdefault.jpg"
      },
      {
        title: "Object-Oriented Python: Classes, Inheritance & Pydantic",
        description: "Master OOP concepts, dataclasses, and Pydantic models essential for agent development.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=Hd9I2xuPf7Q",
        thumbnailUrl: "https://i.ytimg.com/vi/Hd9I2xuPf7Q/maxresdefault.jpg"
      },
      {
        title: "Python Data Structures Deep Dive",
        description: "Comprehensive guide to lists, tuples, sets, dicts, and collections module for efficient data handling.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=hzmzhOsLHA0",
        thumbnailUrl: "https://i.ytimg.com/vi/hzmzhOsLHA0/maxresdefault.jpg"
      },
      {
        title: "Error Handling & File I/O in Python",
        description: "Exception handling, context managers, and working with JSON, CSV, and binary files.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=UwsceTJhZZk",
        thumbnailUrl: "https://i.ytimg.com/vi/UwsceTJhZZk/maxresdefault.jpg"
      },
      {
        title: "Working with HTTP APIs using Requests",
        description: "Learn to call APIs, handle authentication, rate limits, and implement retry logic with tenacity.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=DnSeXOKDHWo",
        thumbnailUrl: "https://i.ytimg.com/vi/DnSeXOKDHWo/maxresdefault.jpg"
      },
      {
        title: "Database Connectivity: SQL & ORMs",
        description: "Connect to databases with psycopg2 and SQLAlchemy, manage connections, and write efficient queries.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=Jl0b8naz6qI",
        thumbnailUrl: "https://i.ytimg.com/vi/Jl0b8naz6qI/maxresdefault.jpg"
      },
      {
        title: "Building APIs with FastAPI",
        description: "Create your first FastAPI endpoint with Pydantic models, dependency injection, and automatic docs.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=KjviMDjWzB4",
        thumbnailUrl: "https://i.ytimg.com/vi/KjviMDjWzB4/maxresdefault.jpg"
      },
      {
        title: "Async Programming with asyncio",
        description: "Master async/await, event loops, parallel execution, and timeouts for concurrent AI operations.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=FMy2kwGvxL4",
        thumbnailUrl: "https://i.ytimg.com/vi/FMy2kwGvxL4/maxresdefault.jpg"
      }
    ]
  },
  {
    id: 2,
    title: "AI & LLM Fundamentals",
    color: "purple",
    videoCount: 7,
    description: "Understand how LLMs work, from tokenization to model selection and RAG basics.",
    videos: [
      {
        title: "What is an LLM? Neural Networks & Transformers Explained",
        description: "Demystify large language models, neural networks, and transformer architecture without complex math.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tokenization & Context Windows: The Hidden Mechanics",
        description: "Learn how text becomes tokens, understand context limits, and why your prompt might get truncated.",
        duration: "45 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Embeddings: Turning Text into Vectors",
        description: "Deep dive into embeddings, vector representations, and semantic similarity for AI applications.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Reasoning Models vs Base Models: o1, Claude, GPT-4",
        description: "Compare reasoning models (o1, Claude Sonnet thinking) with base models and when to use each.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Reading Model Benchmarks: MMLU, HumanEval & More",
        description: "Understand AI benchmarks, leaderboards, and how to critically evaluate model performance claims.",
        duration: "40 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Choosing the Right Model: GPT vs Claude vs Gemini",
        description: "Compare major models on cost, quality, speed, and context length to pick the best for your use case.",
        duration: "45 min",
        url: "PLACEHOLDER"
      },
      {
        title: "RAG Overview: When LLMs Need External Knowledge",
        description: "Introduction to Retrieval-Augmented Generation and why it's essential for production AI systems.",
        duration: "50 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 3,
    title: "Prompt Engineering & LLM APIs",
    color: "teal",
    videoCount: 8,
    description: "Master the art and science of prompting, from API basics to advanced techniques.",
    videos: [
      {
        title: "UI vs API: Understanding the Difference",
        description: "Why ChatGPT behaves differently than API calls and what you need to know for production.",
        duration: "35 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Calling LLMs via API: OpenAI, Anthropic & Claude",
        description: "Hands-on guide to using OpenAI SDK, Anthropic SDK, and handling API responses.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Anatomy of a Great Prompt",
        description: "Learn prompt structure: system vs user messages, roles, personas, and formatting with XML/Markdown.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Core Prompting Techniques: Zero-Shot, Few-Shot & Chain-of-Thought",
        description: "Master fundamental prompting patterns with real examples and when to use each technique.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Applied Prompt Patterns: Extract, Classify, Transform",
        description: "Practical prompting for entity extraction, classification tasks, and data transformation.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Advanced Reasoning: Self-Consistency & Self-Refine",
        description: "Implement advanced techniques like multi-path reasoning, self-critique loops, and Tree of Thought.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Structured Outputs: JSON Mode & Function Schemas",
        description: "Force reliable structured outputs using JSON mode, tool schemas, and XML parsing.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Prompt Management & Cost Optimization",
        description: "Version control prompts, A/B test variants, implement caching, and slash costs with smart strategies.",
        duration: "60 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 4,
    title: "Vector Databases & Embeddings",
    color: "emerald",
    videoCount: 7,
    description: "Deep dive into embeddings, similarity search, and vector database operations.",
    videos: [
      {
        title: "Understanding Embeddings: From Text to High-Dimensional Vectors",
        description: "Comprehensive explanation of how embeddings work and why they're crucial for semantic search.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Similarity Search: Cosine, Dot Product & Distance Metrics",
        description: "Learn different similarity measures and when to use each for optimal search results.",
        duration: "45 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Vector Databases Explained: Architecture & Use Cases",
        description: "Understand vector database internals, indexes (HNSW, IVF), and when you need them.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Getting Started with FAISS & Chroma",
        description: "Hands-on tutorial: set up local vector search with FAISS and Chroma for development.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Production Vector Databases: Pinecone & Weaviate",
        description: "Deploy and manage production vector databases with Pinecone and Weaviate.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Chunking Strategies for Better Retrieval",
        description: "Master document chunking: fixed-width, semantic, overlap windows, and parent-child strategies.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Hybrid Search: Combining Vector & Keyword Search",
        description: "Implement hybrid retrieval combining dense vectors with BM25 keyword search for best results.",
        duration: "55 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 5,
    title: "Building RAG Systems",
    color: "amber",
    videoCount: 8,
    description: "Build production-ready Retrieval-Augmented Generation systems from scratch.",
    videos: [
      {
        title: "Why RAG Exists & When to Use It",
        description: "Understand the RAG architecture, its benefits over fine-tuning, and ideal use cases.",
        duration: "40 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Document Ingestion Pipelines with Docling",
        description: "Build robust ingestion pipelines: parse PDFs, extract layout, handle tables and images.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Advanced Chunking: Semantic & Late Chunking",
        description: "Implement semantic chunking by structure and late chunking for context preservation.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Chunk Enrichment: PII, NER & Metadata",
        description: "Enrich chunks with PII detection, named entity recognition, and metadata for better retrieval.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Advanced Retrieval: Reranking & Query Expansion",
        description: "Improve retrieval with cross-encoder reranking, query expansion, and ColBERT/ColPali.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Graph-Augmented RAG with Neo4j",
        description: "Combine vector search with graph relationships for multi-hop reasoning and complex queries.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "RAG Evaluation: Metrics That Matter",
        description: "Measure RAG quality with Precision@k, Recall@k, RAG Triad, and LLM-as-judge patterns.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Production RAG: End-to-End System Design",
        description: "Design and deploy a complete RAG system with monitoring, caching, and error handling.",
        duration: "80 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 6,
    title: "Function Calling & Tools",
    color: "rose",
    videoCount: 8,
    description: "Give LLMs the ability to use tools and interact with external systems.",
    videos: [
      {
        title: "Introduction to Function Calling",
        description: "Understand how LLMs can call functions, the request-response cycle, and why it's powerful.",
        duration: "45 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tool Schema Design with JSON Schema",
        description: "Write clear tool schemas that LLMs understand, using JSON Schema and Pydantic.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Building Your First Tool: Step-by-Step",
        description: "Hands-on: create a weather API tool, search tool, and calculator with proper error handling.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tool Design Principles & Best Practices",
        description: "Learn the 'one tool, one job' principle, clear docstrings, and structured return patterns.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Error Handling in Tools",
        description: "Handle tool failures gracefully: timeouts, retries, fallbacks, and user-friendly error messages.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "MCP: Model Context Protocol Explained",
        description: "Introduction to MCP - the universal adapter for connecting LLMs to any data source or tool.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Building Custom MCP Servers",
        description: "Create your own MCP servers for filesystem access, APIs, databases, and custom integrations.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tool Security & Sandboxing",
        description: "Secure your tools: input validation, read-only enforcement, rate limits, and execution sandboxing.",
        duration: "60 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 7,
    title: "Single Agent Systems",
    color: "indigo",
    videoCount: 7,
    description: "Build intelligent single-agent systems with reasoning, tools, and memory.",
    videos: [
      {
        title: "The ReAct Pattern: Reasoning + Acting",
        description: "Master the ReAct loop - think, act, observe, repeat - the foundation of agent behavior.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Building Agents with LangChain",
        description: "Create your first LangChain agent with create_agent, tool integration, and structured outputs.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Agent Memory & State Management",
        description: "Implement agent memory using checkpointers, state stores, and conversation history.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Human-in-the-Loop Patterns",
        description: "Add human approval gates for sensitive operations, implement resume flows, and handle feedback.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tool Orchestration & Parallel Execution",
        description: "Execute multiple tools in parallel, handle dependencies, and optimize agent performance.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Agent Debugging & Observability",
        description: "Debug agent behavior with LangSmith tracing, logging strategies, and performance monitoring.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Computer Use & Browser Automation Agents",
        description: "Build agents that control browsers and desktops using Anthropic Computer Use and Playwright.",
        duration: "75 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 8,
    title: "Context Engineering & Agent Memory",
    color: "cyan",
    videoCount: 8,
    description: "Design context windows, memory layers, compression, caching, and privacy controls for reliable agents.",
    playlistUrl: "https://www.youtube.com/playlist?list=PLCGcx-QjmAI8",
    videos: [
      {
        title: "08.01 - Context Windows and Token Budgets",
        description: "Budget prompt space, protect critical context, and avoid losing important facts in long inputs.",
        duration: "5 min",
        url: "https://www.youtube.com/watch?v=oxoaACfCfG4",
        thumbnailUrl: "https://i.ytimg.com/vi/oxoaACfCfG4/maxresdefault.jpg"
      },
      {
        title: "08.02 - Prompt Boundaries: Instructions, Context, and User Input",
        description: "Separate instructions, retrieved context, and user input so agents stay easier to debug and safer to operate.",
        duration: "9 min",
        url: "https://www.youtube.com/watch?v=tNnmFRIMsPM",
        thumbnailUrl: "https://i.ytimg.com/vi/tNnmFRIMsPM/maxresdefault.jpg"
      },
      {
        title: "Short-Term Memory and Conversation Windows",
        description: "Keep recent turns useful with sliding windows, pinned facts, and intact user-assistant pairs.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Semantic Caching for Faster Agents",
        description: "Reuse answers for similar requests with similarity scoring, thresholds, and cache safety rules.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Episodic Memory and Lessons Learned",
        description: "Store past interactions as episodes, retrieve relevant experience, and promote lessons into reusable rules.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Context Compression and Summarization",
        description: "Shrink long histories while preserving decisions, constraints, open tasks, and user preferences.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Long-Term Memory with Profiles and Retrieval",
        description: "Build durable memory around profiles, facts, retrieval records, confidence, and provenance.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Memory Privacy and Right-to-Forget Workflows",
        description: "Design memory records so users can inspect, export, suppress, and delete stored information.",
        duration: "60 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 9,
    title: "Multi-Agent Systems",
    color: "orange",
    videoCount: 8,
    playlistUrl: "https://www.youtube.com/playlist?list=PLdMCsmGiN-78",
    description: "Orchestrate multiple specialized agents to solve complex problems.",
    videos: [
      {
        title: "09.01 - When To Use Multi-Agent Systems",
        description: "Learn when to choose deterministic software, one agent with tools, or a multi-agent system.",
        duration: "8 min",
        url: "https://www.youtube.com/watch?v=NB9yP6E9zKc",
        thumbnailUrl: "https://i.ytimg.com/vi/NB9yP6E9zKc/maxresdefault.jpg"
      },
      {
        title: "09.02 - LangGraph Nodes, Edges, And State",
        description: "Learn LangGraph's graph mental model with typed state, nodes, normal edges, conditional edges, and reducers.",
        duration: "5 min",
        url: "https://www.youtube.com/watch?v=JgBJGAQEqUQ",
        thumbnailUrl: "https://i.ytimg.com/vi/JgBJGAQEqUQ/maxresdefault.jpg"
      },
      {
        title: "09.03 - Common Multi-Agent Patterns",
        description: "Learn router, parallel specialist, verifier, and escalation patterns before choosing a framework.",
        duration: "7 min",
        url: "https://www.youtube.com/watch?v=djhHR-jqGRo",
        thumbnailUrl: "https://i.ytimg.com/vi/djhHR-jqGRo/maxresdefault.jpg"
      },
      {
        title: "09.04 - Agent-as-Tool: The Lightweight Alternative",
        description: "Wrap sub-agents as tools for simpler orchestration without graph complexity.",
        duration: "5 min",
        url: "https://www.youtube.com/watch?v=j-9TcJhGBuE",
        thumbnailUrl: "https://i.ytimg.com/vi/j-9TcJhGBuE/maxresdefault.jpg"
      },
      {
        title: "09.05 - State Management in Multi-Agent Systems",
        description: "Design typed state with Pydantic, manage shared state, and implement checkpointers.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=1DNcdTrvjH0",
        thumbnailUrl: "https://i.ytimg.com/vi/1DNcdTrvjH0/maxresdefault.jpg"
      },
      {
        title: "09.06 - Agent-to-Agent Protocol (A2A)",
        description: "Enable agent discovery, capability cards, and cross-framework delegation with A2A.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=xWXq6DkuG2k",
        thumbnailUrl: "https://i.ytimg.com/vi/xWXq6DkuG2k/maxresdefault.jpg"
      },
      {
        title: "09.07 - Framework Comparison: LangGraph vs CrewAI vs AutoGen",
        description: "Compare major multi-agent frameworks and choose the right one for your project.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=qnk7iLS6CcY",
        thumbnailUrl: "https://i.ytimg.com/vi/qnk7iLS6CcY/maxresdefault.jpg"
      },
      {
        title: "09.08 - Debugging Multi-Agent Systems",
        description: "Debug complex agent interactions, trace message flow, and fix infinite loops.",
        duration: "4 min",
        url: "https://www.youtube.com/watch?v=fLeOESOSXIg",
        thumbnailUrl: "https://i.ytimg.com/vi/fLeOESOSXIg/maxresdefault.jpg"
      }
    ]
  },
  {
    id: 10,
    title: "Security & Guardrails",
    color: "pink",
    videoCount: 7,
    description: "Secure your agents against attacks and implement robust safety guardrails.",
    videos: [
      {
        title: "Prompt Injection Attacks: Understanding the Threat",
        description: "Learn how prompt injection works, real-world examples, and why it's a critical security issue.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Defending Against Prompt Injection: Advanced Techniques",
        description: "Implement defenses: input sanitization, structural separation, and detection patterns.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Three-Layer Guardrail Architecture",
        description: "Design robust guardrails: input (deterministic), output (LLM-judge), and action (tool-level).",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Input Guardrails: Fast Deterministic Checks",
        description: "Build gateway filters for PII, toxicity, out-of-domain requests, and malicious patterns.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Output Guardrails: LLM-as-Judge Validation",
        description: "Validate agent outputs for faithfulness, contradictions, and safety before delivery.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Semantic Routing & Intent Classification",
        description: "Route requests to specialized handlers based on semantic understanding and intent detection.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "AWS Bedrock Guardrails for Production",
        description: "Leverage managed guardrails: contextual grounding, content filtering, and topic blocking.",
        duration: "55 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 11,
    title: "Agent Testing & Evaluation",
    color: "violet",
    videoCount: 7,
    description: "Test, evaluate, and ensure quality in your agentic systems.",
    videos: [
      {
        title: "Unit Testing for Agents: Strategies & Patterns",
        description: "Write effective unit tests for agent components, tools, and memory systems.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Integration Testing Agentic Systems",
        description: "Test full agent workflows, tool interactions, and end-to-end scenarios.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Simulation Environments for Agent Testing",
        description: "Build sandboxed simulation environments to safely test agent behavior.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Evaluation Metrics & Frameworks",
        description: "Measure agent performance with task completion rates, accuracy, and custom metrics.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "LLM-as-Judge: Automated Evaluation Patterns",
        description: "Use LLMs to judge output quality, faithfulness, relevance, and helpfulness at scale.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Building Golden Datasets for Regression Testing",
        description: "Create and maintain golden test datasets for continuous validation of agent behavior.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Monitoring Agents in Production",
        description: "Set up monitoring, alerts, and dashboards to track agent performance in the wild.",
        duration: "60 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 12,
    title: "Streaming & Real-Time Agents",
    color: "lime",
    videoCount: 6,
    description: "Build responsive real-time agents with streaming capabilities.",
    videos: [
      {
        title: "Understanding Streaming Responses",
        description: "Learn how LLM streaming works, token-by-token delivery, and when to use it.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Server-Sent Events (SSE) for Token Streaming",
        description: "Implement SSE for one-way streaming from server to client with code examples.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "WebSockets for Bidirectional Communication",
        description: "Build real-time bidirectional agent communication with WebSockets.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Building Streaming Chat Interfaces",
        description: "Create responsive chat UIs that display tokens as they arrive from the agent.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Real-Time Agent Communication Patterns",
        description: "Design patterns for multi-agent real-time collaboration and message passing.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Handling Backpressure & Streaming Errors",
        description: "Manage connection issues, timeouts, and backpressure in streaming scenarios.",
        duration: "50 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 13,
    title: "LLM-Ops & Observability",
    color: "sky",
    videoCount: 6,
    description: "Operationalize your agents with monitoring, tracing, and continuous improvement.",
    videos: [
      {
        title: "Introduction to LLM-Ops",
        description: "Understand LLM-Ops principles, the deployment lifecycle, and production challenges.",
        duration: "16 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Tracing with LangSmith & LangFuse",
        description: "Set up comprehensive tracing to understand agent behavior and debug issues.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Cost Tracking & Optimization",
        description: "Monitor token usage, track costs per request, and optimize spending without sacrificing quality.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Latency Monitoring & Performance Optimization",
        description: "Track p50/p95/p99 latency, identify bottlenecks, and optimize agent response times.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "A/B Testing Prompts & Models",
        description: "Systematically test prompt variations and model choices to improve performance.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Feedback Loops & Continuous Improvement",
        description: "Collect user feedback, detect drift, and continuously improve agent quality.",
        duration: "55 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 14,
    title: "Cloud Deployment & Infrastructure",
    color: "fuchsia",
    videoCount: 7,
    description: "Deploy agents to production with AWS, containers, and managed AI services.",
    videos: [
      {
        title: "AWS Basics for AI Engineers",
        description: "Essential AWS services: S3, RDS, DynamoDB, Lambda, and IAM for agent deployment.",
        duration: "60 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Containerizing Agents with Docker",
        description: "Package FastAPI agents in Docker containers for consistent deployment anywhere.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Deploying to AWS ECS Fargate",
        description: "Deploy containerized agents to ECS Fargate with auto-scaling and load balancing.",
        duration: "70 min",
        url: "PLACEHOLDER"
      },
      {
        title: "AWS Bedrock: Managed Foundation Models",
        description: "Use AWS Bedrock for serverless access to Claude, Llama, and other foundation models.",
        duration: "55 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Secrets Management & Environment Variables",
        description: "Secure API keys and credentials with AWS Secrets Manager and parameter store.",
        duration: "50 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Load Testing & Capacity Planning",
        description: "Use locust/k6 to load test agents, identify limits, and plan infrastructure capacity.",
        duration: "65 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Production Cost Optimization Strategies",
        description: "Implement caching, model routing, prompt compression, and token limits to control costs.",
        duration: "60 min",
        url: "PLACEHOLDER"
      }
    ]
  },
  {
    id: 15,
    title: "Hands-On Projects",
    color: "green",
    videoCount: 8,
    description: "Build real-world projects from scratch to cement your learning.",
    videos: [
      {
        title: "Project 1: Simple Chatbot with Memory",
        description: "Build a conversational chatbot with session memory and personality.",
        duration: "75 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 2: Document Q&A System with RAG",
        description: "Create a document question-answering system using RAG and vector search.",
        duration: "90 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 3: Tool-Using Research Assistant",
        description: "Build an agent that searches the web, reads documents, and synthesizes research.",
        duration: "85 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 4: Email Assistant with Function Calling",
        description: "Create an email assistant that reads, categorizes, and drafts responses.",
        duration: "80 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 5: Multi-Agent Code Review System",
        description: "Build a multi-agent system that reviews code for bugs, style, and security.",
        duration: "95 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 6: Customer Support Chatbot with Guardrails",
        description: "Production-ready support bot with sentiment analysis, routing, and safety guardrails.",
        duration: "90 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 7: SQL Query Agent for Analytics",
        description: "Build an agent that converts natural language to SQL for business analytics.",
        duration: "85 min",
        url: "PLACEHOLDER"
      },
      {
        title: "Project 8: Automated Social Media Content Generator",
        description: "Create an agent that generates, schedules, and posts social media content.",
        duration: "80 min",
        url: "PLACEHOLDER"
      }
    ]
  }
];

const parseVideoDurationMinutes = (duration) => {
  const minutes = Number.parseInt(duration, 10);
  return Number.isFinite(minutes) ? minutes : 0;
};

window.MODULES = window.MODULES.map((module) => {
  const durationMinutes = module.videos.reduce((sum, video) => (
    sum + parseVideoDurationMinutes(video.duration)
  ), 0);

  return {
    ...module,
    durationMinutes,
    duration: `${(durationMinutes / 60).toFixed(1)} hours`
  };
});

window.PROJECT_TEMPLATES = [
  {
    id: 1,
    title: "Beginner Projects",
    difficulty: "Beginner",
    projects: [
      {
        name: "Personal Journal Chatbot",
        description: "A chatbot that remembers your conversations and helps you reflect on your day.",
        skills: ["Basic prompting", "Conversation memory", "LLM API calls"],
        estimatedTime: "4-6 hours"
      },
      {
        name: "PDF Summarizer",
        description: "Upload PDFs and get concise summaries with key points extracted.",
        skills: ["Document parsing", "Summarization prompts", "File handling"],
        estimatedTime: "6-8 hours"
      },
      {
        name: "Recipe Recommendation Bot",
        description: "Enter ingredients you have, get recipe suggestions with cooking instructions.",
        skills: ["Structured prompts", "Data formatting", "Simple UI"],
        estimatedTime: "5-7 hours"
      }
    ]
  },
  {
    id: 2,
    title: "Intermediate Projects",
    difficulty: "Intermediate",
    projects: [
      {
        name: "Smart Document Search",
        description: "RAG system that searches through your personal documents and answers questions.",
        skills: ["RAG", "Embeddings", "Vector database", "Chunking"],
        estimatedTime: "15-20 hours"
      },
      {
        name: "GitHub Issue Analyzer",
        description: "Agent that analyzes GitHub issues, categorizes them, and suggests solutions.",
        skills: ["Tool use", "API integration", "Classification", "Function calling"],
        estimatedTime: "12-15 hours"
      },
      {
        name: "Meeting Notes Assistant",
        description: "Transcribe meetings, extract action items, and send summaries to participants.",
        skills: ["Transcription", "Extraction", "Email integration", "Structured outputs"],
        estimatedTime: "10-12 hours"
      },
      {
        name: "Shopping Price Tracker",
        description: "Monitor product prices across websites and alert when prices drop.",
        skills: ["Web scraping", "Alerts", "Data persistence", "Scheduling"],
        estimatedTime: "12-16 hours"
      }
    ]
  },
  {
    id: 3,
    title: "Advanced Projects",
    difficulty: "Advanced",
    projects: [
      {
        name: "Multi-Agent Research Team",
        description: "Coordinator, researcher, summarizer, and critic agents working together on research tasks.",
        skills: ["Multi-agent orchestration", "LangGraph", "State management", "Complex workflows"],
        estimatedTime: "25-30 hours"
      },
      {
        name: "Production RAG Knowledge Base",
        description: "Enterprise-grade RAG system with evaluation, monitoring, and deployment to AWS.",
        skills: ["Advanced RAG", "Evaluation metrics", "Deployment", "Monitoring", "Cost optimization"],
        estimatedTime: "30-40 hours"
      },
      {
        name: "AI Code Review Assistant",
        description: "Multi-agent system that reviews PRs for bugs, security issues, style, and performance.",
        skills: ["Code analysis", "Multi-agent patterns", "GitHub integration", "Security scanning"],
        estimatedTime: "30-35 hours"
      },
      {
        name: "Conversational SQL Analytics",
        description: "Natural language to SQL with validation, execution guardrails, and result visualization.",
        skills: ["NL-to-SQL", "Database security", "Guardrails", "Multi-agent validation"],
        estimatedTime: "25-30 hours"
      },
      {
        name: "Automated Customer Support System",
        description: "Full customer support system with intent routing, knowledge base, escalation, and analytics.",
        skills: ["Routing", "RAG", "Guardrails", "Real-time streaming", "Production deployment"],
        estimatedTime: "40-50 hours"
      }
    ]
  }
];

window.RESOURCES = [
  {
    category: "Documentation",
    items: [
      { name: "OpenAI API Docs", url: "https://platform.openai.com/docs" },
      { name: "Anthropic Claude API", url: "https://docs.anthropic.com" },
      { name: "LangChain Docs", url: "https://python.langchain.com" },
      { name: "LangGraph Docs", url: "https://langchain-ai.github.io/langgraph/" },
      { name: "Pinecone Docs", url: "https://docs.pinecone.io" }
    ]
  },
  {
    category: "Tools & Frameworks",
    items: [
      { name: "LangSmith (Tracing)", url: "https://smith.langchain.com" },
      { name: "FastAPI", url: "https://fastapi.tiangolo.com" },
      { name: "Pydantic", url: "https://docs.pydantic.dev" },
      { name: "Streamlit", url: "https://streamlit.io" },
      { name: "AWS Bedrock", url: "https://aws.amazon.com/bedrock/" }
    ]
  },
  {
    category: "Learning Resources",
    items: [
      { name: "Anthropic's Building Effective Agents", url: "https://www.anthropic.com/research/building-effective-agents" },
      { name: "LangChain Blog", url: "https://blog.langchain.dev" },
      { name: "Latent Space Podcast", url: "https://www.latent.space/podcast" },
      { name: "Eugene Yan's Blog", url: "https://eugeneyan.com" },
      { name: "Model Context Protocol", url: "https://modelcontextprotocol.io" }
    ]
  }
];
