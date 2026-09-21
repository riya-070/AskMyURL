# AskMyURL: Mistral to Groq migration

## 1. Create the key

Create an API key at https://console.groq.com/.

## 2. Configure locally

Copy `.env.example` to `.env`, then replace the placeholder:

```env
GROQ_API_KEY=your_real_groq_key
GROQ_MODEL=openai/gpt-oss-20b
MAX_ANALYSIS_CHARS=80000
```

Keep your existing `SARVAM_API_KEY` if you use Hindi/Hinglish audio.

## 3. Install the updated dependencies

In PowerShell, from the project directory:

```powershell
python -m pip install -r requirements.txt
```

## 4. Run locally

```powershell
python -m streamlit run app.py
```

Test with a short captioned YouTube video. The analysis now uses one Groq call
instead of separate title, summary, and extraction calls.

## 5. Deploy on Streamlit Community Cloud

Push the updated project to GitHub. In Streamlit Cloud, open the app settings,
then add these values under Secrets:

```toml
GROQ_API_KEY = "your_real_groq_key"
GROQ_MODEL = "openai/gpt-oss-20b"
```

Add `SARVAM_API_KEY` there only when Hindi/Hinglish transcription is required.
Never commit `.env` or `cookies.txt`.

## Fallback behavior

If Groq is missing, unavailable, or rate-limited, AskMyURL automatically:

- creates an extractive summary locally;
- detects likely action items, decisions, and questions;
- returns relevant transcript passages for Q&A.

This keeps the public app usable without exposing a technical API error.
