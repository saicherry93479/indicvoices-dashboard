# IndicVoices Audio Dashboard

A Streamlit dashboard for browsing and listening to audio samples from the IndicVoices S3 bucket.

## Features

- 🌐 Browse by language (Telugu, Hindi, etc.)
- 📁 View all samples within each language folder
- 🔊 Play original, denoised, and denoised+normalized audio
- 📝 View verbatim text from metadata
- 📄 Pagination at top and bottom

## Local Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/indicvoices-dashboard.git
cd indicvoices-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.streamlit/secrets.toml` with your AWS credentials:
```toml
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
S3_BUCKET_NAME = "indicvoices"
```

4. Run the dashboard:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Add secrets in the Streamlit Cloud dashboard:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_BUCKET_NAME`
6. Deploy!

## Environment Variables

| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for S3 |
| `S3_BUCKET_NAME` | S3 bucket name (default: indicvoices) |
