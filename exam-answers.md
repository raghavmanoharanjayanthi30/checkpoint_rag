# Technical Exam Answers

## Section A: Foundations

### Q1 (3 pts)
**Explain the relationship between context window, tokens, and cost. Why does chunking strategy materially impact both retrieval quality AND inference cost? Use specific numbers from a model you have actually used.**

More context generally means more input tokens, which means higher inference cost. This is where chunking strategy becomes important.

If the chunks are too large, the information needed to answer the question might be there, but it is surrounded by a lot of irrelevant information. This means we are sending more tokens to the model than necessary, which increases cost and can also make it harder for the model to focus on the relevant information.

On the other hand, if the chunks are too small, we might lower the amount of context we send and therefore reduce cost, but we can also lose important context. For example, information needed to answer one question might be split across multiple chunks, and retrieving only one of them could lead to an incomplete answer.

For example, GPT-4o has a 128K-token context window. If my request contains 100 tokens for the question, 500 tokens of instructions, and 10,000 tokens of retrieved context, that is about 10,600 input tokens before the model generates its answer. If better chunking allows me to retrieve only 2,000 relevant tokens, I would only be sending about 2,600 input tokens before the output.

So the goal is to find a balance: chunks should be small enough that retrieval is focused and we are not sending unnecessary tokens, but large enough that we don't lose the context needed to answer the question.


### Q2 (3 pts)
**Compare temperature, top_p, and top_k. When would you use each, and why might you set temperature=0 in a production RAG system? When would temperature=0 be the wrong call?**

*Your answer here*
The goal of an LLM is to predict the next token. At each step, the model assigns probabilities to possible next tokens and then uses a strategy to choose one.
Temperature controls how sharp or random the probability distribution is. A low temperature makes the model more likely to choose high-probability tokens, while a higher temperature makes lower-probability tokens more likely to be selected, resulting in more varied and creative responses. Top-k limits the model to the k tokens with the highest probabilities before choosing the next token. For example, with top_k=5, the model only considers the five most probable tokens. Top-p instead considers the smallest group of tokens whose probabilities add up to a specified value. For example, with top_p=0.9, the model considers the smallest set of tokens that together account for roughly 90% of the probability mass. In a production RAG system, temperature=0 can be useful because we usually want consistent and predictable answers based on the retrieved information rather than creative variations. However, temperature=0 would be the wrong choice when creativity or diversity is important, such as brainstorming, creative writing, or generating multiple different ideas.

---

## Section B: Provider Judgment

### Q3 (4 pts)
**You're building an internal HR document Q&A system for a 5,000-person healthcare company. Compare OpenAI GPT-4o, Claude Sonnet, and self-hosted Llama 3 across (a) cost at scale, (b) data privacy and compliance, (c) latency, (d) accuracy on long-context retrieval. Pick one. Defend the choice in 4�6 sentences.**

*Your answer here*

For a healthcare company, privacy and compliance are especially important, so I would lean toward self-hosted Llama 3 because it gives the company more control over sensitive HR data. With 5,000 employees and potentially heavy usage, API costs for GPT-4o or Claude Sonnet could grow quickly because they are based on usage, while self-hosting avoids those per-token API fees. However, self-hosting is not free because we would need to spend money on GPUs, infrastructure, and engineering to deploy and maintain the model. GPT-4o and Claude Sonnet would likely be easier to deploy and maintain, and they may offer better performance depending on the workload, while Llama's latency would depend on the GPUs we use. Overall, I would choose self-hosted Llama 3 because the additional infrastructure cost is a reasonable tradeoff for greater data control in a healthcare HR system.

---

### Q4 (2 pts)
**Give two specific scenarios where fine-tuning Llama 3 is the correct choice over prompt engineering with GPT-4o. What is the use case, what does the training data look like, and what does success measurement look like?**

*Your answer here*
One use case for fine-tuning Llama 3 is a specialized task, such as an orthopedic surgery assistant that needs to understand medical terminology and produce answers in a specific format. The training data could be examples of orthopedic surgery notes paired with the correct answers or outputs, and success could be measured by how closely the model's answers match expert answers. A second use case is a customer-support assistant that needs to respond in the same tone and style as a company's employees. The training data could be past customer-support conversations and employee responses, and success could be measured by response quality, tone, and customer satisfaction. Fine-tuning can be better than few-shot prompting here because we don't have to include many examples in every prompt, which saves context and token usage.



---

## Section C: RAG Architecture

### Q5 (3 pts)
**You have 50,000 PDFs of insurance policies, each 30�100 pages, with tables, headers, footers, and inline citations. Walk through your chunking strategy: chunk size, overlap, how you handle tables, what metadata you attach. Justify each decision.**

*Your answer here*
For main text: would start with larger chunks (1000 - 1500 tokens) with higher overlap ~200 tokens to presevee info context and prevent losing info at boundaries ex: clause boundaries in legal documents. For tables, use library like unstructured to get it as a html, and for each table generate a summary embed the summary and at retrieval time if chunk is retrieved, pass HTML as context. headers and footers, add as metadata to text chunks. Retrieval stragety - hybrid search (BM25 + similarity search) - good for semantic similarity search + keyyword searching.


---

### Q6 (2 pts)
**Explain hybrid search (BM25 + semantic). When does it meaningfully outperform pure vector search? Give a concrete example with the kind of query that would fail under pure vector retrieval but succeed under hybrid.**

*Your answer here*
Hybrid search combines BM25 keyword search with semantic vector search. BM25 is useful when the exact words in the query matter, such as dates, names, product IDs, or specific terms, while semantic search is better at finding information with similar meaning even when the exact words are different. Hybrid search can outperform pure vector search when a query has both an important keyword constraint and a semantic meaning. For example, if I ask, "What happened before the 2024 NBA Finals?", pure semantic search might retrieve information about NBA Finals from other years because it is semantically similar. BM25 can match the exact terms "2024" and "NBA Finals," while semantic search helps find relevant information, so combining them gives better retrieval.


---

### Q7 (2 pts)
**What is reranking, and why do production RAG systems often add a reranker even when retrieval looks 'good enough' on top-5 metrics? Name a specific reranker you would use and explain when you would reach for it.**

*Your answer here*
Reranking is a second step after retrieval where we reorder the retrieved documents based on how relevant they are to the actual question. The highest similarity score from vector search does not always mean that the chunk is the best one for answering the question. For example, vector search might return five chunks that are all related to the topic, but a reranker can identify which chunk actually contains the information needed to answer the question. A specific reranker I would use is a cross-encoder reranker, which scores the question and each retrieved chunk together and then sorts the chunks by relevance. I would use reranking in a production RAG system when retrieval returns many similar documents and I need to improve the precision of the final context sent to the LLM.



---

### Q8 (3 pts)
**Compare vector RAG vs Graph RAG. Describe a use case where Graph RAG meaningfully outperforms vector RAG and explain the underlying reason. Not just 'it has relationships' but specifically what kind of query benefits from a traversal that embeddings cannot answer.**

*Your answer here*
Vector RAG retrieves chunks based on semantic similarity, while Graph RAG is better when we need to connect information across multiple entities. For example, if we ask, "Which employees will be affected by this immigration rule change?", we may need to connect the employee to their department, location, and visa status, and then check whether those attributes are affected by the new rule. Vector search might retrieve documents about the employees, visa rules, and departments, but it does not reliably connect all of these pieces together. Graph RAG can traverse these relationships and identify the employees who actually meet the conditions.



---

## Section D: Evaluation & Production

### Q9 (3 pts)
**Define faithfulness, answer relevance, and context precision in RAG evaluation. For each, give one concrete failure mode you have seen (or could see) in your build from Part 1. How would you collect a ground-truth set if you didn't have one provided?**

*Your answer here*
Faithfulness measures whether the answer is supported by the retrieved context rather than making up information. A failure mode would be the model giving an answer that sounds correct but is not actually supported by the retrieved documents. Answer relevance measures whether the answer actually addresses the user's question. A failure mode would be a user asking about the company's vacation policy and the model giving a general explanation of employee benefits without answering the vacation question. Context precision measures whether the most relevant chunks are ranked highly and unnecessary chunks are kept out of the retrieved context. A failure mode would be retrieving five chunks where the correct policy is only in the fifth chunk and the first four are mostly irrelevant. If I did not have a ground-truth set, I would collect common and important real user questions and have domain experts provide the correct answers and identify the documents that should support each answer. I could then use these questions as a test set to measure retrieval and answer quality.



---

### Q10 (3 pts)
**List 3 production failure modes for a deployed RAG system and how you would detect each in monitoring. Be specific about the signal, not 'monitor accuracy' but what metric, what threshold, what alert.**

*Your answer here*
Retrieval failure: The retriever fails to find the document or chunk needed to answer the question. I would monitor retrieval recall@5 on a labeled evaluation set and alert if it drops below 90%, since this means the correct chunk is missing from the top 5 results too often. 

Poor context ranking: The correct chunk is retrieved but ranked below many irrelevant chunks, so the LLM may not focus on the right information. I would monitor context precision@5 and alert if it drops below 80% or decreases by more than 10% from the normal baseline. 

Generation failure: The retriever finds the right information, but the LLM still produces an incorrect or unsupported answer. I would monitor faithfulness/groundedness scores on sampled production queries and alert if the score drops below a set threshold such as 90%, or if there is a sudden 10% drop from the baseline.



---

### Q11 (2 pts)
**Your RAG chatbot is hallucinating on questions where the answer genuinely is not in the corpus. Walk through your debugging process step by step. What do you check first, second, third? What is the fix when the issue is the model 'helping' instead of admitting uncertainty?**

*Your answer here*
First, I would check what documents or chunks are being retrieved for questions where the answer is not in the corpus. Ideally, there should be no strongly relevant chunks, so I would compare the similarity scores with scores from questions that do have answers; if unanswerable questions have much lower scores, I could add a minimum similarity threshold and ignore results below it. Second, I would check the reranker to see whether it also considers the retrieved chunks irrelevant to the question. Third, if retrieval is working correctly but the LLM still gives an answer, the problem is likely that the model is trying to "help" instead of admitting it does not know. In that case, I would change the prompt to tell the model to only answer using the retrieved context and say that the answer is not available when the context does not contain enough information. If retrieval is also failing on questions that should be answerable, then I would look at things like hybrid search, chunking, or HyDE (similarity search with hypothetical document that answers the question) to improve retrieval.



