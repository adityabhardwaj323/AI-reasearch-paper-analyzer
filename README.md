# PaperMind — AI Research Analyst

PaperMind lets you upload PDF and DOCX research papers, ask questions about them, and generate research insights with Gemini. Groq is an optional fallback for answer generation when Gemini reaches a quota limit.

**Live web app:** [Open PaperMind on Streamlit](https://ai-reasearch-paper-analyzer.streamlit.app/)

## Features

- Upload one or more PDF or DOCX papers (up to 200 MB per file), extract their text, and build a searchable, per-session index.
- Ask questions across indexed papers in an AI chat, use suggested prompts, and receive answers grounded in retrieved passages with source names.
- Run focused analysis for methodology, key contributions, research gaps and limitations, technology stack, research quality, and standardized abstract comparisons.
- Explore paper statistics and visualizations for keyword frequency, document comparison, readability, sentence lengths, citation years, and indexed/retrieved chunks.
- Review document and session metrics, clear the chat, refresh analysis, or start a new session that removes the session's local index.
- Configure a Google Gemini API key in the app; optionally add a Groq key as a fallback for answer generation when Gemini reaches quota. Keys entered in the interface are held for the current Streamlit session.

Gemini is required for embeddings, search, and primary answers. Groq does not replace Gemini for indexing. See the key and data handling notes below before using the hosted app.

## Run locally

Use Python 3.12 and install the pinned dependencies:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

You can enter Google Gemini and optional Groq API keys in the app's **Configure AI provider keys** panel. Keys entered there are held in that Streamlit session and are not written to project files. For server-provided defaults, create an ignored `.env.local` file:

```text
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_optional_groq_key
```

Google Gemini is required for document and query embeddings, search, and primary answers. Groq only handles answer generation when Gemini reaches quota; it cannot replace Gemini embeddings. Paper text is sent to Gemini. Retrieved passages and questions may also be sent to Groq during fallback.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), choose **Create app** and select this repository and the `main` branch.
3. Set the app file path to `app.py`.
4. In **Advanced settings**, select Python 3.12, then deploy.
5. Open the deployed app and enter the keys in **Configure AI provider keys**. You can deploy without keys, but document analysis stays disabled until a Google Gemini key is provided.

If you prefer to provide default keys through Cloud settings, add root-level values in the app's **Secrets** settings:

```toml
GOOGLE_API_KEY = "your_google_key"
GROQ_API_KEY = "your_optional_groq_key"
```

Never commit `.streamlit/secrets.toml` or real API keys. The repository ignores local secrets files. For public deployments, users' session keys are processed by the app server; use a trusted host and HTTPS.

Uploaded papers are indexed in a local temporary directory unique to each session. **New Session** removes that session's index. Temporary data can be lost when the hosted app restarts, so users may need to upload papers again after a restart.

## Notes

- `.streamlit/config.toml` sets the dark theme and the 200 MB per-file upload limit.
- The dependency versions in `requirements.txt` are pinned for repeatable builds.
- The default Streamlit Community Cloud Python version is 3.12; keep the deploy setting aligned with this project.

## Technology

- Streamlit
- LangChain, Gemini, and optional Groq fallback
- FAISS for per-session vector search
- pypdf and python-docx for document extraction
- Plotly and textstat for analysis visuals and reading metrics

## License

MIT
