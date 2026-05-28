# Building Agentic Applications with OGX and Elasticsearch

This repository contains the example application to build a basic
agentic applications with [OGX](https://ogx-ai.github.io/) and
[Elasticsearch](https://github.com/elastic/elasticsearch).

This code example is part of the article []() published in
[Elasticsearch Labs](https://www.elastic.co/search-labs) of Elastic.

## Getting Started

Create an activate a virtual env:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies of the project using:

```bash
pip install -r requirements.txt
```

We need to configure the `.env` file copying the structure from the `.env.example` file.
We can generate a new `env` file as follows:

```bash
cp .env.example .env
```

We can edit the `.env` adding the missing information (e.g. `ELASTICSEARCH_API_KEY`, `OPENAI_API_KEY`):

```
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=your-api-key-here
ELASTICSEARCH_INDEX_NAME=eu-documents
OGX_URL=http://localhost:8321
OPENAI_API_KEY=your-api-key-here
INFERENCE_MODEL="openai/gpt-5-mini-2025-08-07"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

This project example uses GPT-5-mini from OpenAI as LLM and the [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) as embedding model.


## Elasticsearch

If you already have an Elasticsearch instance running, you can specify the `ELASTICSEARCH_URL` and
the `ELASTICSEARCH_API_KEY`. If you don't know how to create an API key, you can refer to [this guide](https://www.elastic.co/docs/deploy-manage/api-keys/elasticsearch-api-keys).

If you don't have an Elasticsearch server available, you can activate a free trial on 
[Elastic Cloud](https://www.elastic.co/cloud) or install it locally using the [start-local](https://github.com/elastic/start-local) script:

```bash
curl -fsSL https://elastic.co/start-local | sh
```

This will install Elasticsearch (and [Kibana](https://github.com/elastic/kibana)) on your computer and generate an API key.

The API key will be shown as output of the previous command and stored in a `.env` file
in the `elastic-start-local` folder.

## OGX server

Before executing the RAG example, we need to start the OGX server. The OGX framework uses a client-server architecture.
The OGX client send all the request as embedding, inference, etc. to the OGX server.
For more details about OGX we suggest to read the [official documentation](https://ogx-ai.github.io/docs).

To start the OGX server you need to execute the following command from the root folder of the project:

```bash
set -a && source .env && set +a && uvx --from 'ogx[starter]' --with 'sentence-transformers>=3.0.0' ogx stack run ./config.yaml
```

The configuration of the server is provided in the `config.yaml`file.

## Execute the RAG application

To start the RAG application you have to execute the following command:

```shell
python src/rag.py
```

The first time, the script will read the data/*.pdf files, create the chunks from the content, create the embedding
and storing it in Elasticearch. This is automatically provided by the OGX server.

When the upload of the files will finish you will have a basic chat system, as follows:

```
Index already exists: eu-documents
Vector store ID: vs_32318e6f-4f48-41bb-8127-05fd067e52ea

Ask a question about EU documents (or 'exit' to quit):
```

You can ask any question related to the EU documents stored in the `data` folder.
For instance, you can ask:

```
What are the risks of using AI as presented in the EU AI Act document?
```

And the RAG will respond something like this:

```
🔧 Executing file_search (server-side)...
🤔 Brief summary of the main risks the EU AI Act identifies for AI use:

- Harm to health, safety or fundamental rights from specific AI applications and uses <|71213903-602c-460c-b0e8-ac43d38c41c6:3eadea8d-32dc-93f2-f3b9-1708eada93ac|>.  
- Discrimination and biased outcomes (notably from biometric identification and categorisation, including risks for age, ethnicity, race, sex or disabilities) <|71213903-602c-460c-b0e8-ac43d38c41c6:befb889a-ecce-fb53-061c-126cbe1e0006|>.  
- Risks from profiling and automated decision‑making that affect rights protected under data‑protection law <|71213903-602c-460c-b0e8-ac43d38c41c6:3eadea8d-32dc-93f2-f3b9-1708eada93ac|>.  
- Privacy risks when AI processes special categories of personal data or sensitive information <|71213903-602c-460c-b0e8-ac43d38c41c6:aa70d4ad-2adc-a584-24ad-237ea03b9477|>.  
- Cybersecurity threats specific to AI (e.g., data poisoning, adversarial attacks, membership inference and exploitation of model or data vulnerabilities) <|71213903-602c-460c-b0e8-ac43d38c41c6:d88f1a3b-9a97-f7e9-a870-0a597f91ff90|>.  
- Lack of transparency, traceability or explainability that undermines accountability and remedies for affected persons <|71213903-602c-460c-b0e8-ac43d38c41c6:3eadea8d-32dc-93f2-f3b9-1708eada93ac|>.  
- Misinformation and provenance risks from synthetic audio/visual/text content, which the Act requires to be marked/detectable where feasible <|71213903-602c-460c-b0e8-ac43d38c41c6:edd2f19d-30bd-c990-5ede-1952260547ac|>.  
- Risks to critical infrastructure and public safety when AI is used as safety‑critical components <|71213903-602c-460c-b0e8-ac43d38c41c6:aa70d4ad-2adc-a584-24ad-237ea03b9477|>.  
- Harms amplified by dependence, power imbalances, vulnerability of affected groups, or outcomes that are hard to correct or reverse <|71213903-602c-460c-b0e8-ac43d38c41c6:aa70d4ad-2adc-a584-24ad-237ea03b9477|>.  
- Broader societal risks (including to democracy, the rule of law and environmental protection) if AI is deployed without proper safeguards <|71213903-602c-460c-b0e8-ac43d38c41c6:f657e2b2-44c8-e0d2-d830-e7b499e63d43|>.
The Act addresses these by (among other measures) designating certain uses as “high‑risk,” imposing transparency, documentation and registration obligations, and requiring robustness, cybersecurity and conformity assessments for such systems <|71213903-602c-460c-b0e8-ac43d38c41c6:befb889a-ecce-fb53-061c-126cbe1e0006|>.
```

Please notice that each response has a `<|document-id:chunk:id|>` at the end. These IDs are important since they are the sources used to generate the answers. This is one of the positive outcome of a RAG architecture, the mitigation of [hallucinations](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)) with the evidence of sources.


## Learn more

To learn more about OGX, you can read the [documentation](https://ogx-ai.github.io/docs) page. 

For Elasticsearch, you can visit the reference page [here](https://www.elastic.co/docs/reference/elasticsearch). 



