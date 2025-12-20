
# THETA Project – Data Explorer

A small Streamlit web app to interactively explore the THETA project dataset
(or any other CSV/TSV dataset).

## How to use

1. Install dependencies (ideally in a fresh virtual environment):

```bash
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run streamlit_app.py
```

3. In the sidebar:

- Choose **"From URL"** and paste the direct CSV/TSV download link from Figshare  
  (click **Download** on the dataset page and copy the final URL), **or**
- Choose **"Upload CSV"** and upload a local extract of the THETA dataset.

4. Use the automatically generated filters in the sidebar to subset the data,
   build quick summaries, and download the filtered subset.

You can deploy this app to:

- **Streamlit Cloud** (free tier)  
- **Docker + any server**  
- **Internal IPH server** via `streamlit run` behind a reverse proxy

The filtering UI is generic and should work for most rectangular datasets, not
only THETA.
