# 🤖 Rule-Based AI Task Routing Agent

A simple **Rule-Based AI Agent** developed for the **Week 8 Celebal Technologies Assignment**. This project demonstrates the fundamentals of an intelligent agent by implementing a task-routing pipeline that analyzes user queries and routes them to the appropriate tool based on predefined conditions. The agent supports mathematical calculations, keyword extraction, general query handling, and structured JSON responses.

---

# 📖 Project Overview

Modern AI systems often consist of multiple specialized tools working together under a central agent. Instead of solving every problem directly, an agent first identifies the user's intent and then routes the request to the most appropriate tool.

This project implements a **rule-based task routing agent** that receives natural language queries, determines the requested task using simple conditional logic, invokes the appropriate tool, and returns the result in a standardized JSON format. The implementation demonstrates the basic principles of agent-based architectures without relying on external AI frameworks.

---

# 🎯 Project Objectives

* Build a simple Rule-Based AI Agent.
* Analyze user queries using conditional intent detection.
* Route mathematical expressions to a Calculator Tool.
* Route text analysis requests to a Keyword Extraction Tool.
* Handle unsupported or conversational queries using a fallback response.
* Return all outputs in a structured JSON-compatible format.
* Validate the agent using automated test cases and an interactive execution loop.

---

# ⚙️ Project Workflow

```text
User Query
      │
      ▼
Convert Query to Lowercase
      │
      ▼
Intent Detection
      │
      ▼
Conditional Task Routing
      │
 ┌────┴───────────────┐
 │                    │
 ▼                    ▼
Calculator Tool   Keyword Extractor
 │                    │
 └─────────┬──────────┘
           │
           ▼
General Fallback Handler
           │
           ▼
Structured JSON Response
```

---

# 🧠 Agent Architecture

The project consists of four major components:

### Calculator Tool

* Receives mathematical expressions.
* Evaluates arithmetic operations.
* Returns calculated results.
* Handles invalid expressions safely.

### Keyword Extraction Tool

* Accepts text input.
* Splits text into words.
* Removes duplicate words.
* Returns meaningful keywords based on simple filtering rules.

### Task Routing Agent

* Converts queries to lowercase.
* Detects user intent using conditional statements.
* Routes requests to the appropriate processing tool.
* Handles unsupported queries through a fallback response.

### Response Generator

Every execution path returns a standardized JSON-compatible dictionary containing:

* Response Type
* Processing Result

---

# 🛠️ Technologies Used

* Python
* Jupyter Notebook
* Conditional Statements (`if`, `elif`, `else`)
* Exception Handling (`try-except`)
* Built-in Python Functions

---

# 📊 Agent Execution

The agent processes user requests through the following stages:

* Query Input
* Intent Detection
* Task Routing
* Tool Execution
* Response Formatting
* Interactive User Testing

The project also includes automated validation queries and an interactive `while True` loop for continuous testing.

---

# 📈 Sample Outputs

### Calculation Request

Input

```
Calculate 20 + 5
```

Output

```json
{
    "type": "calculation",
    "result": 25
}
```

---

### Keyword Extraction

Input

```
Extract keywords from Artificial Intelligence is transforming industries
```

Output

```json
{
    "type": "keywords",
    "result": [
        "artificial",
        "intelligence",
        "transforming",
        "industries"
    ]
}
```

---

### General Query

Input

```
What is Machine Learning?
```

Output

```json
{
    "type": "general",
    "result": "This query does not require any specialized tool."
}
```

---

### Error Handling

Input

```
Calculate 20 +
```

Output

```json
{
    "type": "error",
    "result": "Invalid mathematical expression."
}
```

---

# 💡 Key Learnings

* Understood the fundamentals of AI Agent architectures.
* Implemented a rule-based task routing pipeline.
* Learned intent detection using conditional logic.
* Integrated multiple tools within a single agent workflow.
* Implemented structured JSON response formatting.
* Applied exception handling for robust execution.
* Validated agent behavior using automated and interactive testing.

---

# 🚀 Future Improvements

* Integrate Natural Language Processing (NLP) for smarter intent detection.
* Replace rule-based routing with machine learning classifiers.
* Add additional tools such as translation, summarization, and question answering.
* Support multiple routing conditions using semantic similarity.
* Build a web-based interface using Streamlit or Flask.

---

# 📁 Repository Structure

```text
.
├── Week8_Assignment.ipynb
├── README.md

```

---

# 🎓 Conclusion

This project demonstrates the implementation of a **Rule-Based AI Task Routing Agent** capable of analyzing user queries and directing them to specialized processing tools. By combining conditional intent detection, modular tool integration, structured JSON responses, and robust error handling, the project provides a practical introduction to intelligent agent pipelines. It serves as a strong foundation for understanding how modern AI agents coordinate multiple tools to solve diverse user requests efficiently.

---

# 👨‍💻 Author

**Kamlesh Deora**  
B.Tech CSE (AI & ML)  
Celebal Technologies – Data Science Internship (Week 8)
