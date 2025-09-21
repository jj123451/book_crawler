# The Book Crawler

*the project was created in respone to "BigQuery AI - Building the Future of Data" Google competition to promote BigQuery AI usage in business solutions*

## 1. The story

### The problem

Let's take a book. A big one. With lots of rich human characters and full of twisted plots. The crime story, perhaps.
As you progress reading it, it gets harded to understand all the plot twists and who is who in the book. 
Some characters have the same names. Some appear in the beginnig, then disappear and reapear near the end.
Some lie, use psoudonyms, pretend to be somone else, then reveal themselfes.
You start to cease to understand who is who and plot gets more and more foggy.
Finally you get it: the grand mother of main character must be a daughter of drug cartel boss!
Now it all makes sense, the whole picture is clear ... no ... it doesn't make sense at all. You put the book down.

### And other problems

It was meant to be about business solutions, so where is a business here? 

Seeing on TV screen the judge sitting in a court room, with huge piles of case documents, did you ever wonder if he/she read and analysed them all thoroughly? And police? Have they connected all the dots? Or maybe the innocent one will be sentenced and the villian set free?

**Other problematic areas:**
- Insurance Claims & Fraud Detection (already mentioned) - complex insurance cases (especially fraud investigations) involve huge volumes of documents
- Financial Compliance & Risk - analyze massive document sets to detect money laundering
- Healthcare Records & Clinical Trials - track patients across long reports from different sources
- Intelligence & Security - intelligence agencies may need to track individuals across open-source data, social media, etc.

### The (too) obvious solution

Using AI seems to be obvious and easy solution. Let's put all this data into prompt and ask AI to analyze. Simple, right?
Not really. First you hit the context window limit. Ok, let's split the documents, the context windows nowadays have million of tokens, or more, so it wouldn't be so many chunks.
You put the first chunk ... and you hit the another problem. The analysis takes ages and result is nonsence. The attention process in LLM has N2 or N3 computational complexity, so it's very non-optimal to make such large inquires. Moreover the AI quality drastically reduces with large data and/or complicated prompts. In my tests, to have usefull results I needed to put 50 thousand of tokens max, preferably half of it. And there is the output token limits, sometimes much less then context windows.

So we need to split more, much much more ... but then AI losts the plot, stops to understand who is who, mixing human characters or not recognizing the same ones. Just like humans.

### The real solution

And this exactly the problem this project POC is designed for.
It is using BigQuery AI to simultaneously process huge amount of data extracted from large documents divided to smaller fragments
First extracting the identification information of every human characters. 
Pre-matching them with the help of semantic embeddings and then do the final matching with the help of AI inference, very carefuly, to not make mistakes.
All of this for multiple books at once, with multiple chuman characters at once executing AI inferece just in SQL queries for thousands of rows at once.
Finally we have the consistent picture who is who. This was the hardest part, but not the last one.

Then we again go fragment by fragment for each human character, extracting the information we want and marging it together.

Still we have unstructured text information. Usefull, but maybe we have huge number of characters and want to do some statistical analysis?
So here is the last part: clustering. Again, using AI inference, semantic embeddings, clustering statistical methods
and SQL allowing us to execute thousands or more computations and inferences in parallel.

## 2. Installation and configuration

### Google BigQuery

First you need to have the Google cloud account with permissions to use BigQuery and AI, with configured connection between them.
- [Select or create a Google Cloud project](https://console.cloud.google.com/cloud-resource-manager). When you first create an account, you get a $300 free credit - it is surprisingly efficient, during this project preparation I was repeatedly running queries, executing even hundreds of AI inferences at the same time - still I didn't use even 1/10 of this sum.
- [Make sure that billing is enabled for your project](https://cloud.google.com/billing/docs/how-to/modify-project)
- [Enable the BigQuery, BigQuery Connection, and Vertex AI APIs](https://console.cloud.google.com/flows/enableapi?apiid=bigquery.googleapis.com,bigqueryconnection.googleapis.com,aiplatform.googleapis.com)
- [Configure connection between BigQuery and Vertex AI](https://cloud.google.com/bigquery/docs/create-cloud-resource-connection)
*note: The connection needs permissions and finding where to add it may be tricky (it was for me). On the console UI, go to left top drop down menu and select IAM & Admin -> IAM, click Grant access, fill in full connection name (email alike) in the principal, then add required role.*

For authentication from the notebooks you need the credential JSON, [please see here how to obtain one](https://cloud.google.com/docs/authentication/application-default-credentials)

### Local environment

1. Save the BigQuery credential JSON into local file and set `GOOGLE_APPLICATION_CREDENTIALS` environment variable with full path pointing to this file
2. Clone the git project to local folder
3. Create the uv venv: e.g. uv venv --python 3.13
4. Install dependencies:
```
uv pip install nltk
uv pip install pydantic
uv pip install ipykernel
uv pip install google-cloud-bigquery
uv pip install bigquery_magics
uv pip install bigframes
```
5. Configure vscode:
ctr + shift + p, choose "Python: Select interpreter" : .\.venv\Scripts\python.exe
6. Change the project and data set ids to your own at the notebooks beginning (in second cell)

### Google Colab

1. Put the credential JSON as value of `BIGQUERY_CREDENTIALS` secret (the field is very small comparing to JSON size, but it will work, it is probably that no one took picture of your key)
2. Remove first line from the notebooks: `%%script false --no-raise-error`
3. Change the project and data set ids at the notebooks beginning (in second cell)

## 3. Running

### Prepare initialization code
The following notebook creates necessary tables, prompts, SQL procedures and statistical analysis SQL views. Needs to bu run once before executing other notebooks.

[Prepare schema](https://github.com/jj123451/book_crawler/blob/main/bc_phase0_prepare_schema.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase0_prepare_schema.ipynb)

### Gather the books
The following notebook randomly choses 3 not very large books (it can be configured in the notebook at the beginning) from GDELT Processes Internet Archive.
It containig content of scanned books from years 1800 - 2015 (currently google has full texts up to year 1922). Thousands of them in each year.
The choosing mechanism first asses the books against containg human characters (using SQL with AI inference), to not choose books about e.g. gardening.

[Load random books](https://github.com/jj123451/book_crawler/blob/main/bc_phase1_load_random_books.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase1_load_random_books.ipynb)

### Processing

This notebook does the whole processing, which internally consists of several phases:
- **Correcting the books** - the OCR of many of the books was imprecise causing a lot of typing errors in the text - so they need to be corrected. This is the only part of the processing using python code, it needs it to fragment the books on sentences boundaries. The correction itself uses SQL with AI inference
- **Chunking** - we chunk the corrected books again, this time to bigger fragments with overlaps. From now on only SQL with BigQuery AI will be used
- **Summarization** - with multiple prompts book summary is used as a supplementary information
- **Characters identification** - it is the most complicated part involving multiple extraction of information using AI inference, matching human characters with help of Vector Search, hierarchical queries and AI inference
- **Enrich characters** - this part gathers the human characters information we are interested in. For the demonstration sake, this project gethers for type of informations: the financial status of the character, the information about position in the society, the values this characters adheres to and the sex
- **Clustering** - all the gathered information are clustered to provide enumarated classification for statistical analysis. It uses embeddings generation with Vector Search together with KMean clustering - all using SQL only

[Processing](https://github.com/jj123451/book_crawler/blob/main/bc_phase2_to_7_processing.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase2_to_7_processing.ipynb)

## 4. Data analysis

The final data are in follow tables:
- **'characters'** - the main table with all the gathered data and dominating cluster ids for each type of gathered data
- 'clusters' - contains information about discovered clusters
- 'character_cluster_details' - contains information about sub-cluster ids for gathered data. 
    - For example let's assume that 'wealth' data is long and complicated, e.g.: "Described as a poor exile without a roof over his head, implying no significant wealth. Also noted as being part of Kmita's company and having implied noble standing." 
    - The 'character_cluster_details' will have more of much shorter data without unnecessary information: e.g. "poor, no significant wealth" and "homeless". 
    - Each sub-data will have its sub-claster id assigned
    - To join character_cluster_details' with 'characters' table, use 'id' and 'book_id' columns ('id' alone is not unique)
- 'v_characters_enriched' - view similar to 'characters' table but with cluster names and sanitized gender values

For data analysis you can use following predefined SQL views as basic examples:
- `v_formatted_cluster_statistics` - shows all the clusters identified by KMean analysis
- `v_formatted_crosstab_sex_social` - shows relationships between gender and social class
- `v_formatted_crosstab_sex_wealth` - shows relationships between gender and wealth
- `v_formatted_crosstab_sex_values` - shows relationships between gender and values
- `v_formatted_crosstab_social_wealth` - shows relationships between social class and wealth
- `v_formatted_crosstab_social_values` - shows relationships between social class and values
- `v_formatted_crosstab_wealth_values` - shows relationships between social wealth and values
- `v_formatted_character_profiles` - it groups the characters by all the four dimensions (gender, wealth, values, social class) that contains at least 2 persons
- `v_formatted_gender_analysis` - similar to above but with gender related counts and percentage columns

You can also see the simple examples how to use the views to vizualize data using bigframes pandas library:

[Statistical Analysis Examples](https://github.com/jj123451/book_crawler/blob/main/bc_phase2_tobc_phase8_statistical_analysis_examples_7_processing.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_phase8_statistical_analysis_examples.ipynb)

## 5. Technical documentation

1. Please see the [architectural diagram](./tree/main/diagrams)
2. Please see comments inside the notebooks, especially these two:
- [Preparing schema notebook](./bc_phase0_prepare_schema.ipynb)
- [Processing notebook](./bc_phase2_to_7_processing.ipynb)

You can also see the notebooks in [split_notebooks](https://github.com/jj123451/book_crawler/tree/main/split_notebooks) folder.
They contain the same code as notebooks in main folders, but are splitted to multiple, functionally sepearated, parts, for better clarity.

## 6. Other helpful information

### Cleaning 

This notebook contains some helpful cleaning mehods, e.g. to drop all temporary tables

[Cleaning](https://github.com/jj123451/book_crawler/blob/main/bc_util_clean_tables.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jj123451/book_crawler/blob/main/bc_util_clean_tables.ipynb)

### Adding new books

After Phase 6, all processed books in 'book' table are marked as 'processed' and will not be processed again. 

You can then safely add new books and re-run whole processing - only the new books will be processed. The old content of 'characters' table will remain intact. Characters from new books will be appended to it.

### Clustering again

If you want to repeat clustering with new clusters size, just run all notebooks from Phase 7 again. They will recreate clustering data, leaving 'characters' data intact.
