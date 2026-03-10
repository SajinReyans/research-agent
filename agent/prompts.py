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