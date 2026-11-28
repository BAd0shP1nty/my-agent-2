# 📡 Telecom ITSM RAG Operations Assistant

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot specifically designed for the **Telecommunications** domain and **IT Service Management (ITSM)** sub-domain.

Built with:
- **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`) with cosine similarity indexing
- **Embedding Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Large Language Model (LLM)**: DeepSeek (`deepseek-chat`)
- **Web Interface**: Streamlit with interactive grounding validation and document inspection
- **Dataset**: Comprehensive 3-page synthetic Telecom Core (Mediation, OCS, SS7, Diameter Gy, Kafka) incident and runbook knowledge base

---

## 🏗️ Architecture & Domain Coverage

1. **Page 1: Architecture & ITSM Framework**:
   - Subsystem topologies: Passive Mediation, Online Charging System (OCS), SS7 / SCCP, Policy Control (PCRF), SMSC / SMPP, Packet Core.
   - ITSM Incident Priority Matrix (P1, P2, P3) and SLA targets (<2h for P1, <4h for P2, <24h for P3).
   - Triage, blast radius scoping, and Post-Incident Review (PIR) governance.

2. **Page 2: Standard Incident Records & Post-Mortems**:
   - `TEL-INC-2026-0001`: Mediation SFTP collector delay due to expired partner credentials.
   - `TEL-INC-2026-0002`: P1 destination-code rating table mapping error and rollback.
   - `TEL-INC-2026-0003`: P1 Diameter Gy credit-control timeout from firewall ephemeral port exhaustion.
   - `TEL-INC-2026-0004`: P2 prepaid balance cache invalidation drop after async recharge.
   - `TEL-INC-2026-0005`: P1 SS7 SCCP translation failures caused by obsolete Global Title Translation (GTT).
   - `TEL-INC-2026-0012`: P1 Kafka consumer lag caused by poison-pill deserialization failure.
   - `TEL-INC-2026-0030`: P1 promotional bundle tariff priority precedence inversion.

3. **Page 3: Operational Runbooks & Preventive SOPs**:
   - `RB-ITSM-01`: Service Account Credential Rotation & 48h Overlap Windows.
   - `RB-ITSM-02`: Diameter & Signaling Firewall Change Validation & Concurrency Benchmarks.
   - `RB-ITSM-03`: Kafka Consumer Lag & Poison-Pill Dead-Letter Queue (DLQ) Remediation.
   - `RB-ITSM-04`: Tariff Rule Release & Rating Precedence Hierarchy (Priority 10 to 99).
   - `RB-ITSM-05`: Problem Management & Known Error Database (KEDB) Linkage.

---

## 🚀 Running Locally

1. **Install dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Configure secrets**:
   Create or edit `.streamlit/secrets.toml`:
   ```toml
   DEEPSEEK_API_KEY = "your-deepseek-api-key"
   OPENAI_API_KEY = "your-openai-api-key"
   AI_BASE_URL = "https://api.deepseek.com"
   AI_MODEL = "deepseek-chat"
   ```

3. **Start the Streamlit App**:
   ```bash
   python -m streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "feat: complete Telecom ITSM RAG chatbot with FAISS, OpenAI, and DeepSeek"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
   - Click **Create app** -> **Deploy a public app from GitHub**.
   - Select your repository (`my-agent-2` or your chosen repo name), branch `main`, and main file `app.py`.

3. **Add Secrets in Streamlit Cloud**:
   - Expand **Advanced Settings** before clicking Deploy (or in your app's Settings -> Secrets).
   - Paste the following:
     ```toml
     DEEPSEEK_API_KEY = "sk-your-deepseek-key"
     OPENAI_API_KEY = "sk-your-openai-key"
     AI_BASE_URL = "https://api.deepseek.com"
     AI_MODEL = "deepseek-chat"
     ```
   - Click **Save** and **Deploy**.

4. **Verify Deployment**:
   - Streamlit Cloud will automatically install packages from `requirements.txt` (`faiss-cpu`, `openai`, `numpy`, `pandas`, `streamlit`).
   - Your live app URL will end in `.streamlit.app`.
