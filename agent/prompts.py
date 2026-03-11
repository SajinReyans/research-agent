REVIEW_PROMPT = """
You are an expert academic writer specializing in AI and computer science literature reviews.

You are given summaries, extractions, and a comparison report of two research papers on the topic: "{topic}"

Your job is to write a comprehensive, well-structured academic literature review based on these two papers.

Use the following format exactly:

---

# 📝 Literature Review: {topic}

## Abstract
Write a concise 150-200 word abstract summarizing what this literature review covers, the papers reviewed, and the key findings.

---

## 1. Introduction & Background
- Introduce the research topic and why it matters
- Provide background context for the field
- State the purpose of this literature review
- Briefly mention the two papers being reviewed

---

## 2. Related Work
- Discuss the broader research landscape around this topic
- How do these two papers fit into the existing body of work?
- What problems were they trying to solve?

---

## 3. Methodology Overview
- Summarize the methodology of Paper 1
- Summarize the methodology of Paper 2
- Highlight key methodological similarities and differences

---

## 4. Results & Discussion
- Present the key results from Paper 1
- Present the key results from Paper 2
- Compare and discuss the results critically
- Which approach performed better and why?
- What do these results mean for the field?

---

## 5. Conclusion & Future Directions
- Summarize the key takeaways from both papers
- What gaps remain in the research?
- What future directions do the authors or you suggest?
- What is the overall state of this research area?

---

## 6. References
- [{title1}]
- [{title2}]

---

Writing Guidelines:
- Write in formal academic style
- Be critical and analytical, not just descriptive
- Use paragraphs, not bullet points for main sections
- Minimum 600 words total
- Do not hallucinate — only use information from the provided inputs

Topic: {topic}

Paper 1 Title: {title1}
Paper 1 Summary:
{summary1}
Paper 1 Extraction:
{extraction1}

Paper 2 Title: {title2}
Paper 2 Summary:
{summary2}
Paper 2 Extraction:
{extraction2}

Comparison Report:
{comparison}
"""

EXTRACTION_PROMPT = """
You are an expert AI research analyst. You are given the text of a research paper.

Your job is to extract specific structured information from the paper using the following format exactly:

---

## 🔬 Research Methodology
Describe the overall research approach. Is it experimental, theoretical, empirical, or survey-based? What steps did the authors follow?

## 📦 Dataset Used
List all datasets mentioned in the paper. For each, include:
- Dataset name
- Size (if mentioned)
- Source or origin (if mentioned)
- How it was used (training, testing, evaluation)

If no dataset is mentioned, state: "No dataset used (theoretical/survey paper)"

## 🏗️ Model Architecture
Describe the model or system architecture in detail:
- Type of model (Transformer, CNN, RNN, etc.)
- Number of layers, parameters (if mentioned)
- Key components or modules
- Any novel architectural choices

If no model is proposed, state: "No new model proposed"

## 📊 Evaluation Metrics
List all metrics used to evaluate the model or approach:
- Metric name (e.g. Accuracy, F1, BLEU, ROUGE)
- Score or value achieved (if mentioned)
- Benchmark or dataset it was measured on

## ⚠️ Limitations
What are the weaknesses, constraints, or shortcomings acknowledged by the authors or observable from the work?

## 🚀 Future Work
What do the authors suggest as next steps or open problems?

## 💡 Key Contributions
List the 3–5 most important contributions of this paper as bullet points.

---

Be precise and factual. Only extract what is explicitly stated in the paper. Do not hallucinate or infer beyond what is written.

Paper Text:
{paper_text}
"""

COMPARISON_PROMPT = """
You are an expert AI research analyst. You are given structured extraction reports from two research papers.

Your job is to compare both papers across all key dimensions and produce a detailed side-by-side comparison.

Use the following format exactly:

---

## 📊 Side-by-Side Comparison

| Aspect | {title1} | {title2} |
|--------|----------|----------|
| **Methodology** | (summarize in 1-2 sentences) | (summarize in 1-2 sentences) |
| **Dataset** | (name + size if known) | (name + size if known) |
| **Model Architecture** | (model type + key details) | (model type + key details) |
| **Evaluation Metrics** | (metrics used) | (metrics used) |
| **Results & Performance** | (key scores/outcomes) | (key scores/outcomes) |
| **Limitations** | (main weaknesses) | (main weaknesses) |

---

## 🔍 Detailed Analysis

### Methodology Comparison
How do the research approaches differ? Which is more rigorous or novel?

### Dataset Comparison
How do the datasets differ in size, diversity, or suitability?

### Architecture Comparison
How do the model designs differ? What are the trade-offs?

### Performance Comparison
Which paper achieves better results, and on what benchmarks?

### Limitations Comparison
Which paper has more significant limitations?

---

## 🏆 Overall Verdict

| Category | Winner | Reason |
|----------|--------|--------|
| Methodology | Paper 1 / Paper 2 / Tie | (one line reason) |
| Dataset | Paper 1 / Paper 2 / Tie | (one line reason) |
| Architecture | Paper 1 / Paper 2 / Tie | (one line reason) |
| Performance | Paper 1 / Paper 2 / Tie | (one line reason) |
| Overall | Paper 1 / Paper 2 / Tie | (one line reason) |

---

Be factual and precise. Base your comparison only on the provided extractions. Do not hallucinate.

Paper 1 Title: {title1}
Paper 1 Extraction:
{extraction1}

Paper 2 Title: {title2}
Paper 2 Extraction:
{extraction2}
"""

SUMMARY_PROMPT = """
You are an expert research assistant. You are given the text of a research paper.

Your job is to produce a clean, structured summary using the following format:

---

## 📄 Paper Summary

### 🔍 Problem Statement
What problem is this paper trying to solve? Why does it matter?

### 🛠️ Methodology
What approach, techniques, or models did the authors use?

### 📊 Results
What were the key findings, metrics, or outcomes?

### ✅ Conclusion
What is the overall takeaway? What do the authors suggest for future work?

### 🏷️ Keywords
List 5–8 relevant keywords from the paper.

---

Be concise but thorough. Use bullet points where helpful. Do not hallucinate — only use information from the paper text provided.

Paper Text:
{paper_text}
"""