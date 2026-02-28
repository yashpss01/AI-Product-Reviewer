# AI-Powered Review Analytics System

## Problem Statement
Analyzing large volumes of product reviews manually is time-consuming and inefficient. Businesses need a structured way to quantify customer satisfaction, identify the best and worst-performing products, and securely restrict data access based on user roles (Admin vs. Analyst). This system provides an automated, SQL-backed analytics dashboard to track Net Promoter Score (NPS), sentiment distribution, and product rankings without relying on complex, over-engineered architectures.

## Architecture Diagram

```text
+-------------------+       +-------------------+       +-------------------+
|      User UI      |       |  Business Logic   |       |     Database      |
|  (Streamlit App)  |<----->|   (services/)     |<----->|     (SQLite)      |
|                   |       |                   |       |                   |
| - Login Form      |       | - auth.py         |       | - users table     |
| - Dashboard       |       | - analytics.py    |       | - reviews table   |
| - Reports View    |       | - reports.py      |       | - reports table   |
|                   |       | - ai_router.py    |       |                   |
|                   |       | - ai_summary.py   |       |                   |
+-------------------+       +-------------------+       +-------------------+
        ^                           ^                           ^
        |                           |                           |
        +-- Session State           +-- bcrypt hashing          +-- Local .db file
        +-- LLM Intent Parser       +-- SQL Querying

## Tech Stack
- **Python 3**: Core programming language.
- **Streamlit**: For the interactive web dashboard and UI orchestration.
- **SQLite3**: Lightweight, file-based relational database.
- **Pandas**: For data processing and CSV ingestion.
- **Plotly**: For interactive data visualization (bar charts).
- **bcrypt**: For secure password hashing.
- **OpenAI**: For LLM-driven query intent parsing and NLP summarization.
- **python-dotenv**: For securely injecting environment variables.

## Setup Instructions
1. **Navigate to the project directory**:
   ```bash
   cd Desktop/AI-Product-Reviewer
   ```
2. **Install dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```
3. **Environment Setup**:
   Create a `.env` file in the root directory and add your OpenAI API Key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. **Data Preparation**:
   Place the `Reviews.csv` file inside the `data/` folder, then run the processing script to clean, assign feature-engineered categories, and load 20,000 rows into the database:
   ```bash
   python3 data/process_csv.py
   ```
4. **Seed the Database with Demo Users**:
   ```bash
   python3 test_auth.py
   ```
5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Demo Credentials
- **Admin Role** (Full Access)
  - Username: `admin_user`
  - Password: `adminpass`
- **Analyst Role** (Restricted to 'Electronics')
  - Username: `analyst_electronics`
  - Password: `analystpass`

## Feature List
- **Role-Based Access Control (RBAC)**: Secure login system with `bcrypt` password hashing. Analysts are locked to specific categories while admins have global access.
- **NPS Calculation**: Computes accurate Net Promoter Scores (-100 to +100) dynamically using raw SQL queries.
- **Satisfaction Distribution**: Groups reviews into Happy (4-5), Neutral (3), and Unhappy (1-2) with visual bar charts.
- **Product Rankings**: Identifies the Top 5 and Worst 5 products (minimum 10 reviews to ensure statistical significance).
- **ChatGPT-like NLP Querying**: Uses an AI router (`services/ai_router.py`) to understand natural language intents (e.g., "What is the NPS for Books?"). The LLM strictly classifies the intent and extracts parameters cleanly into JSON while the Streamlit backend strictly enforces role constraints overlaying the LLM's decisions. 
- **AI Complaint Summarization**: Fetches the top negative reviews and securely runs them against OpenAI's API to generate a concise bulleted summary of why customers are unhappy.
- **Traceability & Report Saving**: Automatically saves user queries, stringified results, and AI summaries to the database for historical auditing.

## Known Limitations
1. **Database Performance**: The application queries the SQLite database fresh on every page load or interaction. While extremely fast for 20,000 rows, this would not scale efficiently for millions of rows.
2. **Data Mutability**: There is currently no UI to upload new CSVs or update existing reviews.
3. **API Rate Limits**: Currently constrained by personal OpenAI API limits (`insufficient_quota`). The app defensively catches this gracefully so it doesn't crash on testing.

## Future Improvements
1. **Query Optimization & Caching**: Implement `@st.cache_data` in Streamlit to cache expensive SQL queries and prevent database hammering on UI refreshes.
2. **Database Migration**: Move from local SQLite to a robust production database like PostgreSQL.
3. **Advanced Visualizations**: Add time-series charts to track NPS trends over time rather than just aggregate metrics.
