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