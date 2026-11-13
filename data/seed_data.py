"""
Seed data generator for the Mock Interview Coach system.
Produces a realistic synthetic 10-year archive of:
  - Interview questions (company/role/year/difficulty)
  - Historical candidate feedback patterns
"""

import json
import random
from pathlib import Path

random.seed(42)

COMPANIES = [
    "Google", "Amazon", "Microsoft", "TCS", "Infosys",
    "Wipro", "Accenture", "Goldman Sachs", "Deloitte", "Flipkart"
]

ROLES = [
    "Software Development Engineer",
    "Data Analyst",
    "Machine Learning Engineer",
    "Product Manager",
    "Business Analyst"
]

YEARS = list(range(2015, 2025))

# ─── Question templates per role ───────────────────────────────────────────

QUESTION_BANK = {
    "Software Development Engineer": [
        {
            "question": "Explain the difference between a process and a thread. When would you use multithreading?",
            "key_points": ["process has own memory space", "threads share memory within process", "multithreading for I/O bound tasks", "GIL in Python", "concurrency vs parallelism"],
            "tags": ["OS", "concurrency", "fundamentals"],
            "difficulty": "medium"
        },
        {
            "question": "Given an array of integers, find the two numbers that sum to a target value. Optimise for time complexity.",
            "key_points": ["brute force O(n²)", "hash map approach O(n)", "handle duplicates", "edge cases: empty array", "explain trade-offs"],
            "tags": ["algorithms", "hash map", "arrays"],
            "difficulty": "easy"
        },
        {
            "question": "Design a URL shortener service like bit.ly. Walk me through your system design.",
            "key_points": ["functional requirements", "base62 encoding", "database schema", "cache layer (Redis)", "load balancing", "analytics"],
            "tags": ["system design", "scalability", "databases"],
            "difficulty": "hard"
        },
        {
            "question": "What is the difference between REST and GraphQL? When would you choose one over the other?",
            "key_points": ["REST: multiple endpoints", "GraphQL: single endpoint", "over-fetching vs under-fetching", "use GraphQL for complex nested data", "REST for simple CRUD"],
            "tags": ["API design", "web", "architecture"],
            "difficulty": "medium"
        },
        {
            "question": "Explain SOLID principles with a real-world example.",
            "key_points": ["Single Responsibility", "Open/Closed", "Liskov Substitution", "Interface Segregation", "Dependency Inversion", "concrete example for each"],
            "tags": ["OOP", "design patterns", "best practices"],
            "difficulty": "medium"
        },
        {
            "question": "How does garbage collection work in Java/Python? What are memory leaks and how do you prevent them?",
            "key_points": ["reference counting", "mark and sweep", "generational GC", "circular references", "tools: memory profiler"],
            "tags": ["memory management", "JVM", "Python"],
            "difficulty": "hard"
        },
        {
            "question": "Implement a Least Recently Used (LRU) cache.",
            "key_points": ["OrderedDict or doubly linked list + hashmap", "O(1) get and put", "capacity management", "eviction policy", "thread safety consideration"],
            "tags": ["data structures", "algorithms", "cache"],
            "difficulty": "hard"
        },
        {
            "question": "What is a deadlock? How do you detect and prevent it?",
            "key_points": ["four conditions: mutual exclusion, hold and wait, no preemption, circular wait", "prevention: break any condition", "detection: resource allocation graph", "banker's algorithm"],
            "tags": ["OS", "concurrency", "deadlock"],
            "difficulty": "hard"
        },
        {
            "question": "Describe the CAP theorem and its implications for distributed systems.",
            "key_points": ["Consistency, Availability, Partition tolerance", "can only guarantee 2 of 3", "CP vs AP systems", "real-world examples (Zookeeper vs Cassandra)"],
            "tags": ["distributed systems", "databases", "system design"],
            "difficulty": "hard"
        },
        {
            "question": "What is the difference between TCP and UDP? Give examples of when to use each.",
            "key_points": ["TCP: connection-oriented, reliable", "UDP: connectionless, faster", "TCP: HTTP, FTP, SSH", "UDP: video streaming, DNS, gaming"],
            "tags": ["networking", "protocols", "fundamentals"],
            "difficulty": "easy"
        },
        {
            "question": "Explain how a binary search tree works. What are its time complexities?",
            "key_points": ["BST property: left < node < right", "search O(h)", "balanced vs unbalanced", "AVL trees, Red-Black trees", "worst case O(n) for skewed"],
            "tags": ["data structures", "trees", "algorithms"],
            "difficulty": "medium"
        },
        {
            "question": "What is Docker and how does containerisation differ from virtualisation?",
            "key_points": ["containers share host OS kernel", "VMs have full OS", "Docker image layers", "faster startup, less overhead", "Kubernetes for orchestration"],
            "tags": ["DevOps", "containers", "infrastructure"],
            "difficulty": "medium"
        },
        {
            "question": "Tell me about a challenging bug you encountered and how you resolved it.",
            "key_points": ["STAR method", "technical depth", "debugging approach", "tools used", "lessons learned", "prevention measures"],
            "tags": ["behavioral", "debugging", "problem-solving"],
            "difficulty": "medium"
        },
        {
            "question": "How does indexing work in databases? When should you not use an index?",
            "key_points": ["B-tree index", "speeds up reads, slows writes", "avoid on small tables", "avoid on frequently updated columns", "composite indexes"],
            "tags": ["databases", "SQL", "performance"],
            "difficulty": "medium"
        },
        {
            "question": "What is the difference between synchronous and asynchronous programming?",
            "key_points": ["sync: blocking execution", "async: non-blocking, event loop", "async/await in Python", "use async for I/O bound tasks", "callbacks vs promises vs coroutines"],
            "tags": ["async", "programming", "Python", "JavaScript"],
            "difficulty": "medium"
        }
    ],
    "Data Analyst": [
        {
            "question": "How would you handle missing data in a dataset? Walk me through your approach.",
            "key_points": ["identify pattern: MCAR, MAR, MNAR", "deletion: listwise, pairwise", "imputation: mean/median/mode/KNN", "business context matters", "document decisions"],
            "tags": ["data cleaning", "statistics", "pandas"],
            "difficulty": "medium"
        },
        {
            "question": "Explain the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN with examples.",
            "key_points": ["INNER: matching rows only", "LEFT: all from left table", "FULL OUTER: all rows from both", "NULL handling", "practical use cases"],
            "tags": ["SQL", "joins", "databases"],
            "difficulty": "easy"
        },
        {
            "question": "What is A/B testing? Walk me through how you would design an experiment.",
            "key_points": ["control vs treatment group", "hypothesis formation", "sample size calculation", "statistical significance", "p-value and confidence intervals", "avoiding biases"],
            "tags": ["statistics", "experimentation", "product analytics"],
            "difficulty": "hard"
        },
        {
            "question": "What is the difference between correlation and causation? Give an example.",
            "key_points": ["correlation: statistical relationship", "causation: direct cause", "confounding variables", "ice cream vs drowning example", "RCT for causation"],
            "tags": ["statistics", "critical thinking"],
            "difficulty": "easy"
        },
        {
            "question": "How would you approach analysing a sudden 20% drop in daily active users?",
            "key_points": ["check data pipeline first", "segment by platform/region/cohort", "timeline correlation", "funnel analysis", "external factors", "stakeholder communication"],
            "tags": ["product analytics", "problem-solving", "metrics"],
            "difficulty": "hard"
        },
        {
            "question": "Explain the difference between a data warehouse and a data lake.",
            "key_points": ["warehouse: structured, schema-on-write", "lake: raw, schema-on-read", "warehouse: Redshift, BigQuery", "lake: S3, HDFS", "lakehouse concept"],
            "tags": ["data engineering", "architecture", "big data"],
            "difficulty": "medium"
        },
        {
            "question": "What is normalisation in databases? Explain 1NF, 2NF, and 3NF.",
            "key_points": ["1NF: atomic values", "2NF: no partial dependency", "3NF: no transitive dependency", "denormalisation for performance", "trade-offs"],
            "tags": ["databases", "SQL", "schema design"],
            "difficulty": "medium"
        },
        {
            "question": "Describe a situation where your data analysis influenced a business decision.",
            "key_points": ["STAR method", "quantify the impact", "data-driven recommendation", "stakeholder alignment", "outcome measurement"],
            "tags": ["behavioral", "business impact"],
            "difficulty": "medium"
        }
    ],
    "Machine Learning Engineer": [
        {
            "question": "Explain the bias-variance tradeoff. How do you manage it in practice?",
            "key_points": ["bias: underfitting", "variance: overfitting", "regularisation (L1/L2)", "cross-validation", "ensemble methods", "learning curves"],
            "tags": ["ML fundamentals", "model selection"],
            "difficulty": "medium"
        },
        {
            "question": "How does a Random Forest work, and what are its advantages over a single decision tree?",
            "key_points": ["bagging: bootstrap sampling", "random feature selection", "majority voting", "reduces variance", "handles high dimensions", "feature importance"],
            "tags": ["ensemble methods", "decision trees"],
            "difficulty": "medium"
        },
        {
            "question": "Explain the transformer architecture. What problem does attention solve?",
            "key_points": ["self-attention mechanism", "query, key, value", "positional encoding", "multi-head attention", "encoder-decoder", "long-range dependencies"],
            "tags": ["deep learning", "NLP", "transformers"],
            "difficulty": "hard"
        },
        {
            "question": "How do you handle class imbalance in a classification problem?",
            "key_points": ["oversampling: SMOTE", "undersampling", "class weights", "precision/recall trade-off", "F1-score over accuracy", "threshold adjustment"],
            "tags": ["classification", "imbalanced data", "metrics"],
            "difficulty": "medium"
        },
        {
            "question": "Describe the steps to deploy a machine learning model to production.",
            "key_points": ["model serialisation (pickle/ONNX)", "API wrapping (FastAPI/Flask)", "containerisation (Docker)", "CI/CD pipeline", "monitoring: data drift, performance", "A/B testing"],
            "tags": ["MLOps", "deployment", "production"],
            "difficulty": "hard"
        },
        {
            "question": "What is the difference between gradient descent, SGD, and Adam optimiser?",
            "key_points": ["GD: full batch", "SGD: single sample, noisy", "mini-batch SGD", "Adam: adaptive learning rates", "momentum", "convergence speed"],
            "tags": ["optimisation", "neural networks", "deep learning"],
            "difficulty": "hard"
        },
        {
            "question": "How would you detect and handle data drift in a production ML system?",
            "key_points": ["statistical tests: KS test, PSI", "monitoring dashboards", "reference vs production distribution", "retraining triggers", "shadow deployment"],
            "tags": ["MLOps", "monitoring", "production"],
            "difficulty": "hard"
        },
        {
            "question": "Explain how BERT differs from GPT in terms of architecture and use cases.",
            "key_points": ["BERT: bidirectional encoder", "GPT: autoregressive decoder", "BERT: classification, NER", "GPT: text generation", "masked LM vs causal LM", "fine-tuning vs prompting"],
            "tags": ["NLP", "transformers", "LLMs"],
            "difficulty": "hard"
        }
    ],
    "Product Manager": [
        {
            "question": "How would you prioritise a product backlog with 50 features and limited engineering capacity?",
            "key_points": ["RICE framework", "MoSCoW method", "user impact vs effort", "align with company goals", "stakeholder alignment", "data-driven prioritisation"],
            "tags": ["prioritisation", "product strategy", "frameworks"],
            "difficulty": "hard"
        },
        {
            "question": "Tell me about a product you admire. What would you change about it?",
            "key_points": ["shows product thinking", "user empathy", "identify pain points", "propose solutions with data", "business viability", "trade-off awareness"],
            "tags": ["product sense", "critical thinking"],
            "difficulty": "medium"
        },
        {
            "question": "How would you define success metrics for a new feature launch?",
            "key_points": ["north star metric", "leading vs lagging indicators", "HEART framework", "counter-metrics", "baseline establishment", "experimentation plan"],
            "tags": ["metrics", "analytics", "product strategy"],
            "difficulty": "medium"
        },
        {
            "question": "Describe a time you had to say no to a stakeholder request. How did you handle it?",
            "key_points": ["STAR method", "data-backed reasoning", "empathy", "offer alternatives", "maintain relationship", "outcome"],
            "tags": ["behavioral", "stakeholder management"],
            "difficulty": "medium"
        },
        {
            "question": "How would you approach building a product for a market you know little about?",
            "key_points": ["user research", "competitive analysis", "domain expert interviews", "rapid prototyping", "lean startup principles", "fail fast"],
            "tags": ["product discovery", "research", "strategy"],
            "difficulty": "hard"
        },
        {
            "question": "What is your process for writing a Product Requirements Document (PRD)?",
            "key_points": ["problem statement", "user personas", "success metrics", "scope: in/out", "user stories", "edge cases", "technical constraints"],
            "tags": ["PRD", "documentation", "process"],
            "difficulty": "medium"
        }
    ],
    "Business Analyst": [
        {
            "question": "How do you gather and document requirements from stakeholders?",
            "key_points": ["interviews", "workshops", "use cases", "user stories", "MoSCoW prioritisation", "sign-off process", "change management"],
            "tags": ["requirements", "stakeholder management"],
            "difficulty": "medium"
        },
        {
            "question": "Explain the difference between functional and non-functional requirements.",
            "key_points": ["functional: what system does", "non-functional: how well it does it", "NFR: performance, security, scalability", "examples for each", "trade-offs"],
            "tags": ["requirements", "SDLC"],
            "difficulty": "easy"
        },
        {
            "question": "Describe a process improvement you implemented. What was the outcome?",
            "key_points": ["STAR method", "as-is vs to-be process", "stakeholder buy-in", "quantify improvement", "lessons learned"],
            "tags": ["behavioral", "process improvement"],
            "difficulty": "medium"
        },
        {
            "question": "How would you perform a cost-benefit analysis for a new IT system?",
            "key_points": ["identify all costs: capex/opex", "quantify benefits: direct/indirect", "NPV, ROI, payback period", "risk assessment", "sensitivity analysis", "recommendation"],
            "tags": ["financial analysis", "decision making"],
            "difficulty": "hard"
        },
        {
            "question": "What is an Entity Relationship Diagram? Create one for an e-commerce system.",
            "key_points": ["entities, attributes, relationships", "cardinality: 1:1, 1:M, M:M", "Customer, Order, Product, Payment", "primary and foreign keys", "normalisation"],
            "tags": ["data modelling", "databases", "analysis"],
            "difficulty": "medium"
        },
        {
            "question": "How do you ensure that a software solution meets business requirements after delivery?",
            "key_points": ["UAT planning", "acceptance criteria", "test scenarios", "defect tracking", "sign-off process", "post-implementation review"],
            "tags": ["UAT", "quality", "delivery"],
            "difficulty": "medium"
        }
    ]
}

# Company-specific question additions
COMPANY_SPECIFIC_ADDITIONS = {
    "Google": {
        "Software Development Engineer": [
            {
                "question": "Design a distributed key-value store like Google Bigtable.",
                "key_points": ["tablet servers", "consistent hashing", "replication", "compaction", "read/write path"],
                "tags": ["system design", "distributed systems", "Google-specific"],
                "difficulty": "hard"
            }
        ],
        "Machine Learning Engineer": [
            {
                "question": "How would you improve Google Search ranking using ML?",
                "key_points": ["query understanding", "PageRank", "learning to rank", "user signals", "BERT integration"],
                "tags": ["search", "ranking", "NLP", "Google-specific"],
                "difficulty": "hard"
            }
        ]
    },
    "Amazon": {
        "Software Development Engineer": [
            {
                "question": "Design Amazon's recommendation system.",
                "key_points": ["collaborative filtering", "item-based vs user-based", "cold start", "real-time vs batch", "A/B testing"],
                "tags": ["recommendation systems", "ML", "Amazon-specific"],
                "difficulty": "hard"
            }
        ],
        "Product Manager": [
            {
                "question": "Amazon uses 6-pager documents instead of PowerPoint. Write a mock 6-pager for a new Prime feature.",
                "key_points": ["narrative format", "working backwards from customer", "data-backed", "FAQs", "press release style"],
                "tags": ["Amazon leadership principles", "communication", "Amazon-specific"],
                "difficulty": "hard"
            }
        ]
    },
    "Goldman Sachs": {
        "Business Analyst": [
            {
                "question": "How would you model credit risk for a portfolio of loans?",
                "key_points": ["probability of default", "loss given default", "exposure at default", "Monte Carlo simulation", "regulatory capital (Basel III)"],
                "tags": ["finance", "risk management", "Goldman-specific"],
                "difficulty": "hard"
            }
        ]
    }
}

# ─── Historical Feedback Templates ─────────────────────────────────────────

FEEDBACK_TEMPLATES = {
    "Google": {
        "Software Development Engineer": [
            {"strengths": ["strong algorithmic thinking", "clean code structure"], "gaps": ["system design depth", "scalability considerations"], "pattern": "Google SDE candidates often struggle with distributed systems. Strong on algorithms but weak on scale."},
            {"strengths": ["excellent system design", "clear communication"], "gaps": ["time complexity analysis", "edge case handling"], "pattern": "Candidates strong in design but sometimes forget to analyse Big-O explicitly."},
            {"strengths": ["good data structures knowledge"], "gaps": ["behavioural answers lack specificity", "no STAR structure"], "pattern": "Technical ability strong but Googleyness competency often underperforms."}
        ],
        "Machine Learning Engineer": [
            {"strengths": ["solid ML theory", "good at bias-variance"], "gaps": ["MLOps and deployment knowledge", "production experience"], "pattern": "Research-oriented candidates lack production ML experience. MLOps is a frequent gap at Google MLE."},
        ]
    },
    "Amazon": {
        "Software Development Engineer": [
            {"strengths": ["good problem-solving"], "gaps": ["leadership principles not demonstrated", "answers not customer-centric"], "pattern": "Amazon strongly weights LP demonstrations. Candidates who ignore LPs rarely pass."},
            {"strengths": ["strong LPs demonstrated"], "gaps": ["system design too theoretical", "not enough data-driven reasoning"], "pattern": "Amazon SDE candidates must ground designs in real-world constraints and data."}
        ],
        "Product Manager": [
            {"strengths": ["great metrics definition", "customer empathy"], "gaps": ["financial acumen", "technical depth"], "pattern": "Amazon PMs need strong financial sense. TCO and ROI calculations are frequently tested."}
        ]
    },
    "Microsoft": {
        "Software Development Engineer": [
            {"strengths": ["solid CS fundamentals"], "gaps": ["growth mindset not conveyed", "defensive about failures"], "pattern": "Microsoft values growth mindset. Candidates who cannot discuss failures openly underperform."},
        ],
        "Data Analyst": [
            {"strengths": ["strong SQL skills", "good at data storytelling"], "gaps": ["business impact articulation", "uncertainty quantification"], "pattern": "Microsoft DA candidates need to connect data findings to business outcomes more explicitly."}
        ]
    },
    "TCS": {
        "Software Development Engineer": [
            {"strengths": ["programming fundamentals solid"], "gaps": ["communication clarity", "real project examples"], "pattern": "TCS interviews weigh communication highly. Technical candidates with poor articulation often fail."},
        ],
        "Business Analyst": [
            {"strengths": ["process knowledge"], "gaps": ["tool proficiency (JIRA, Confluence)", "agile methodology depth"], "pattern": "TCS BA roles expect strong tool knowledge. Agile/Scrum experience is a key differentiator."}
        ]
    },
    "Infosys": {
        "Software Development Engineer": [
            {"strengths": ["enthusiasm", "quick learner signals"], "gaps": ["depth in specialisation", "research contributions"], "pattern": "Infosys values adaptability but expects depth in at least one domain."},
        ]
    },
    "Wipro": {
        "Data Analyst": [
            {"strengths": ["data visualisation skills"], "gaps": ["statistical rigour", "hypothesis testing"], "pattern": "Wipro DA candidates often lack formal statistics. Hypothesis testing is frequently a differentiator."},
        ]
    },
    "Accenture": {
        "Business Analyst": [
            {"strengths": ["client communication skills"], "gaps": ["technical depth in tools", "quantified impact examples"], "pattern": "Accenture BA interviews focus on consulting mindset. Candidates must frame everything as client value."},
        ]
    },
    "Goldman Sachs": {
        "Machine Learning Engineer": [
            {"strengths": ["strong quantitative background"], "gaps": ["business domain knowledge", "regulatory awareness"], "pattern": "Goldman MLE candidates need finance domain understanding alongside ML. Regulatory constraints (MiFID II, Basel) are tested."},
        ]
    },
    "Deloitte": {
        "Business Analyst": [
            {"strengths": ["structured problem-solving"], "gaps": ["technology stack awareness", "data-driven recommendations"], "pattern": "Deloitte BA roles increasingly expect tech-savvy analysts. Data literacy is becoming table stakes."},
        ]
    },
    "Flipkart": {
        "Product Manager": [
            {"strengths": ["user empathy", "product sense"], "gaps": ["growth hacking mindset", "unit economics understanding"], "pattern": "Flipkart PMs are expected to deeply understand e-commerce unit economics. GMV, take rate, and contribution margin are key."},
        ],
        "Machine Learning Engineer": [
            {"strengths": ["recommendation system knowledge"], "gaps": ["real-time serving experience", "feature engineering creativity"], "pattern": "Flipkart MLE candidates need experience with high-throughput real-time ML serving."}
        ]
    }
}


def generate_question_bank():
    """Generate the full question bank with company/role/year assignments."""
    questions = []
    q_id = 1

    for company in COMPANIES:
        for role in ROLES:
            base_questions = QUESTION_BANK.get(role, [])
            company_extras = COMPANY_SPECIFIC_ADDITIONS.get(company, {}).get(role, [])
            all_questions = base_questions + company_extras

            for year in YEARS:
                # Pick 3-5 questions per company/role/year
                selected = random.sample(all_questions, min(len(all_questions), random.randint(3, 5)))
                for q in selected:
                    questions.append({
                        "id": f"Q{q_id:04d}",
                        "company": company,
                        "role": role,
                        "year": year,
                        "question": q["question"],
                        "key_points": q["key_points"],
                        "difficulty": q["difficulty"],
                        "tags": q["tags"],
                        "text": f"[{company} | {role} | {year} | {q['difficulty'].upper()}] {q['question']}"
                    })
                    q_id += 1

    return questions


def generate_feedback_bank():
    """Generate historical candidate feedback entries."""
    feedbacks = []
    f_id = 1
    scores = [3, 4, 5, 6, 7, 8, 9]

    for company, roles_data in FEEDBACK_TEMPLATES.items():
        for role, entries in roles_data.items():
            for year in YEARS:
                for entry in entries:
                    for _ in range(random.randint(2, 5)):
                        score = random.choice(scores)
                        feedbacks.append({
                            "id": f"F{f_id:04d}",
                            "company": company,
                            "role": role,
                            "year": year,
                            "candidate_score": score,
                            "strengths": entry["strengths"],
                            "gaps": entry["gaps"],
                            "pattern_summary": entry["pattern"],
                            "text": (
                                f"[{company} | {role} | {year} | Score:{score}/10] "
                                f"Pattern: {entry['pattern']} "
                                f"Strengths: {', '.join(entry['strengths'])}. "
                                f"Gaps: {', '.join(entry['gaps'])}."
                            )
                        })
                        f_id += 1

    return feedbacks


def save_seed_data():
    """Save generated data to JSON files."""
    out_dir = Path(__file__).parent
    out_dir.mkdir(exist_ok=True)

    questions = generate_question_bank()
    feedbacks = generate_feedback_bank()

    q_path = out_dir / "questions.json"
    f_path = out_dir / "feedback.json"

    with open(q_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    with open(f_path, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {len(questions)} questions → {q_path}")
    print(f"✅ Generated {len(feedbacks)} feedback entries → {f_path}")
    return questions, feedbacks


if __name__ == "__main__":
    save_seed_data()
