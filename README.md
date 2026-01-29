# RefineAI

## Project Title and Team Members
**Project Title:** RefineAI

**Team Members:**
*   Advaith S Menon
*   Rohith Parambil
*   Sebin Thomas

## Problem Statement and Approach
**Problem Statement**
Data cleaning is often a tedious, manual, and error-prone process. RefineAI streamlines this by automating data cleaning rules using Large Language Models (LLMs). It allows users to define cleaning intentions in plain English, removing the barrier of writing complex cleaning scripts.

**Approach**
RefineAI employs a sophisticated pipeline powered by Google's Gemini LLM. The approach involves:
1.  **Interpretation:** Translating natural language rules into executable Python code.
2.  **Safety:** Executing generated code in a sandboxed environment to prevent malicious actions.
3.  **Validation:** Using the LLM to audit changes and ensure they match the user's intent.
4.  **Interface:** Providing both a CLI agent and a web-based dashboard for managing the workflow.

## Tools and Technologies Used
The project is built using the following technologies:
*   **Backend Framework:** Flask (Python)
*   **LLM Provider:** Google Gemini (via Google Cloud Vertex AI/Generative AI)
*   **Data Processing:** Pandas
*   **Frontend Reference:** HTML, CSS, JavaScript (Template based)
*   **Version Control:** Git
*   **Authentication:** Google Application Default Credentials (ADC)

## Installation and Setup Instructions
To get started with RefineAI, ensure you have Python installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/RefineAI.git
    cd RefineAI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r Cleaning_agent/requirements.txt
    ```

3.  **Environment Setup:**
    RefineAI uses Google's Gemini LLM. You must verify your authentication:
    *   Install the `gcloud` CLI.
    *   Run `gcloud auth application-default login` to set up Application Default Credentials (ADC).

## Usage Guide and Examples

### Option 1: Web Interface (Recommended)
The web interface provides a visual way to manage projects and run the cleaning pipeline.

1.  **Start the Server:**
    ```bash
    python app.py
    ```
2.  **Access the Application:**
    Open your browser and navigate to `http://127.0.0.1:5000/`.
3.  **Workflow:**
    *   **Login:** Use any username/password (Currently in demo mode).
    *   **Upload:** Upload your CSV file and Rules file (Excel/Text).
    *   **Dashboard:** View project statistics.
    *   **Run:** Execute the cleaning process.
    *   **Review:** Check the `Logs` and `Comparison` tabs to see the audit results.

### Option 2: Command Line Interface (CLI)
For direct execution without the web UI:

1.  **Prepare Data:**
    *   Place `input.csv` in `Cleaning_agent/data/`.
    *   Create `rules.toon` (text file with rules) in `Cleaning_agent/data/`.
    *   (Optional) Create `metadata.toon` for schema description.

2.  **Run the Agent:**
    ```bash
    python Cleaning_agent/run.py
    ```

3.  **Output:**
    *   Cleaned data: `Cleaning_agent/data/cleaned_output.csv`
    *   Audit logs will be printed to the console.

## Limitations and Future Scope
**Limitations**
*   **Authentication:** The current login system is a placeholder. A robust database-backed auth system is needed for production.
*   **Web Interface:** The UI serves as a template and requires further integration with backend states for real-time progress tracking.
*   **LLM Dependency:** Heavily relies on Google Cloud credentials being active on the host machine.

**Future Scope**
*   **Database Integration:** Implement SQL/NoSQL database for user management and project history.
*   **Enhanced Sandboxing:** Improve the code execution environment (e.g., using Docker containers) for higher security.
*   **Rule Suggestions:** Use the LLM to proactively suggest cleaning rules based on data profiling.
*   **Multiple Code Formats:** Support R or SQL generation in addition to Python.
