# The Book Crawler

*This project is a working prototype created in response to the Google competition: "BigQuery AI - Building the Future of Data".*

## 1. Problem

### The Story

Let’s take a book. A big one. Full of rich human characters and twisted plots. A crime story, perhaps.  
As you keep reading, it becomes harder and harder to follow all the twists and turns, and to remember who is who.  
Some characters share the same name, some disappear and reappear, some lie about who they are, while others are referred to by titles or pseudonyms.  
Gradually, your understanding fades and the plot grows foggier.  

Finally, you think you’ve figured it out: *the grandmother of the main character must be the daughter of a drug cartel boss!*  
Now the story makes sense—the whole picture is clear. … No. It doesn’t make sense at all.  
You put the book down. It’s fine, you’ll just get an easier one.

### But There Are Other Stories

On TV, a judge sits in a courtroom, with piles of case documents stacked on his desk. He speaks with confidence, condemning the defendant for horrific crimes.  
You glance at the mountains of documents—one stacked on top of another, and another, and another. Has he really read and analyzed them all thoroughly? He must be superhuman if he has. How long would that take? Months? Longer?  
You feel pity for him and hope he doesn’t have other cases at the same time. But how many judges are there to handle this overwhelming workload?

### The (Too) Obvious Solution

Using AI seems like the obvious and easy solution. Just throw all the data into a prompt and ask AI to analyze it. Simple, right?  
Not really. First, you hit the context window limit. Okay, so let’s split the documents. Today’s models can handle millions of tokens, so that shouldn’t be too many chunks.  

You put in the first chunk … and hit another problem. The analysis takes forever because of the computational complexity of attention. Worse, the results are nonsense—response quality drops as data size and prompt complexity grow.  
In my tests, useful results required a maximum of 50,000 tokens, preferably half that. And then there’s the output token limit, which is often much smaller than the context window.  

So we need to split the data even more … but then the AI loses track of the plot, confuses characters, or fails to recognize recurring ones. Just like humans.  
We can generate embeddings for all the text and search over it, but that doesn’t solve consistency across stories and characters.

### The Proposed Solution

This proof of concept uses **BigQuery AI** to simultaneously process large volumes of data extracted from documents, split into smaller fragments.  

The high-level approach is:  
1. Extract identifying information for every human character in each fragment.  
2. Pre-match them using semantic embeddings.  
3. Carefully match them with AI inference.  
4. Repeat until stable.  

BigQuery AI allows us to perform these operations on multiple books, fragments, and characters at once—thousands of rows processed simultaneously and independently.  

The rest becomes easier. Tracking characters gives us a reference plane on which to map information, fragment by fragment.  
When this is done, we get consistent information about each person across their entire history.  

But there are many people—often far too many—so the final step is clustering the gathered data.  
Again, we use AI inference, semantic embeddings, and statistical clustering methods—all running simultaneously in SQL queries.  
After that, we can perform statistical analyses of the relationships between pieces of information.

### Other Use Cases

Besides legal case analysis, this approach could be applied to:  
- **Insurance Claims & Fraud Detection** – complex insurance cases (especially fraud) involve huge volumes of documents.  
- **Financial Compliance & Risk** – analyzing massive document sets to detect money laundering.  
- **Healthcare Records & Clinical Trials** – tracking patients across long reports from multiple sources.  
- **Intelligence & Security** – monitoring individuals across open-source data, social media, and more.  
- **Enterprise Knowledge Management** – tracking projects, people, or companies across reports, emails, meeting notes.  
- **Education** – analyzing biographies and historical texts; even fiction reveals how people thought in a given era.  

---

## 2. Installation and Configuration

### Google BigQuery

First, you need a Google Cloud account with permissions for both BigQuery and AI, and a configured connection between them (they are semi-independent within Google Cloud, so a “connection” is required).  

1. [Select or create a Google Cloud project](https://console.cloud.google.com/cloud-resource-manager). *Note: a new account comes with $300 in free credits.*  
2. [Enable billing for your project](https://cloud.google.com/billing/docs/how-to/modify-project).  
3. [Enable the BigQuery, BigQuery Connection, and Vertex AI APIs](https://console.cloud.google.com/flows/enableapi?apiid=bigquery.googleapis.com,bigqueryconnection.googleapis.com,aiplatform.googleapis.com).  
4. [Configure a connection between BigQuery and Vertex AI](https://cloud.google.com/bigquery/docs/create-cloud-resource-connection).  

*Note: Configuring permissions can be tricky. In the console UI, open the top-left dropdown menu, go to **IAM & Admin → IAM**, click **Grant access**, and enter the full connection name (in an email-like format) as the principal. Then assign the required role.*  

For authentication from notebooks, you need a credential JSON. [See here how to obtain one](https://cloud.google.com/docs/authentication/application-default-credentials).

---

### Local Environment

Example setup with **uv** and **VS Code**:

1. Save the BigQuery credential JSON locally and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to its full path.  
2. Clone the GitHub project to a local folder.  
3. Create the uv virtual environment, e.g.: `uv venv --python 3.13`
4. Install dependencies:
```
uv pip install nltk
uv pip install pydantic
uv pip install ipykernel
uv pip install google-cloud-bigquery
uv pip install bigquery_magics
uv pip install bigframes
```
5. Configure VS Code:
Press Ctrl+Shift+P, choose **Python: Select Interpreter**, and select `.venv\Scripts\python.exe`
6. Update project and dataset IDs at the beginning of the notebooks (second cell).

### Google Colab

1. Put the credential JSON as value of `BIGQUERY_CREDENTIALS` secret
2. Remove first line from the notebooks: `%%script false --no-raise-error`
3. Update project and dataset IDs at the beginning of the notebooks (second cell).

## 3. Running

In short: run the three notebooks in order—schema preparation, book selection, and processing. Simply run all cells in each one.
Details with links are below:

### Prepare schema and metadata
This notebook creates the necessary tables, prompts, SQL procedures, and statistical views. It only needs to be run once.

[Prepare schema](https://github.com/jj123451/book_crawler/blob/main/bc_phase0_prepare_schema.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase0_prepare_schema.ipynb)

### Gather the books
This notebook randomly selects three moderately sized books (configurable at the beginning of the notebook) from the GDELT Processed Internet Archive.
The GDELT Archive, stored on Google Cloud, contains scanned books from 1800–2015 (with full text available up to 1922). Thousands of books per year.

The selection process first checks whether books contain human characters (using SQL with AI inference) to avoid irrelevant ones like gardening manuals.

[Load random books](https://github.com/jj123451/book_crawler/blob/main/bc_phase1_load_random_books.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase1_load_random_books.ipynb)

### Processing

This notebook performs the full processing, consisting of several phases:
- **Correcting the books** - OCR errors are fixed to avoid downstream issues. Python ensures fragments align with sentence boundaries, while the correction itself is handled in SQL.
- **Chunking** - corrected books are split into larger overlapping fragments. Smaller chunks work better for OCR correction; larger ones for semantic understanding.
- **Summarization** - generates summaries to be used as supplementary context.
- **Characters identification** - the core of the project, extracting character information with AI inference and iterative matching (vector search, hierarchical queries, inference).
- **Characters enrichment** - collects additional attributes of interest (here: financial status, social position, values & principles, gender).
- **Clustering** - clusters character attributes into standardized groups for statistical analysis, using SQL-based embeddings and k-means clustering.

[Processing](https://github.com/jj123451/book_crawler/blob/main/bc_phase2_to_7_processing.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase2_to_7_processing.ipynb)

## 4. Data analysis

The final data is stored in the following tables:
- **'characters'** - the main table containing all extracted data and cluster IDs for each attribute.
- **'clusters'** - metadata about discovered clusters.
- **'character_cluster_details'** - stores sub-cluster IDs for decomposed attribute values. For example:
    - A complex value such as `Described as a poor exile without a roof over his head...` is split into shorter sub-values like `poor, no significant wealth` and `homeless`.
    - Each sub-value receives a sub-cluster ID.
- **'v_characters_enriched'** - a SQL view similar to `characters` but with cluster names and normalized gender values.

Another key table is **book**, which stores book content, corrected content, and summaries.

*Note: the `characters.id` column is not unique on its own. Use it together with `book_id`.*

Predefined SQL views for analysis:
- `v_formatted_cluster_statistics` - lists all clusters from k-means.
- `v_formatted_crosstab_sex_social` - gender vs. social class.
- `v_formatted_crosstab_sex_wealth` - gender vs. wealth.
- `v_formatted_crosstab_sex_values` - gender vs. values.
- `v_formatted_crosstab_social_wealth` - social class vs. wealth.
- `v_formatted_crosstab_social_values` - social class vs. values.
- `v_formatted_crosstab_wealth_values` - wealth vs. values.
- `v_formatted_character_profiles` - groups characters by all four dimensions (gender, wealth, values, social class), requiring at least two characters per group.
- `v_formatted_gender_analysis` - similar to above but with gender-related counts and percentages.

Example visualizations:

[Statistical Analysis Examples](https://github.com/jj123451/book_crawler/blob/main/bc_phase2_tobc_phase8_statistical_analysis_examples_7_processing.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase8_statistical_analysis_examples.ipynb)

## 5. Technical documentation

1. See the [architectural diagram](./tree/main/diagrams)
2. Check comments inside notebooks, especially:
- [Preparing schema notebook](./bc_phase0_prepare_schema.ipynb)
- [Processing notebook](./bc_phase2_to_7_processing.ipynb)

You can also explore [split_notebooks](https://github.com/jj123451/book_crawler/tree/main/split_notebooks)
, which contain the same code as the main notebooks but split into multiple smaller, functionally separated parts for clarity.

## 6. Other helpful information

### Cleaning 

This notebook contains utilities for cleanup, e.g., dropping all temporary tables after processing.

[Cleaning](https://github.com/jj123451/book_crawler/blob/main/bc_util_clean_tables.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_util_clean_tables.ipynb)

### Adding new books

After Phase 6, all processed books in the `book` table are marked as `processed` and won’t be processed again.

You can safely add new books and re-run the pipeline—only new books will be processed. Existing data in the `characters` table will remain unchanged, with new characters appended.

### Re-Clustering

If you want to repeat clustering with a different number of clusters, simply re-run Phase 7 notebooks.
They will regenerate clustering data without altering the existing `characters` table
