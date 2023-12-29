import pathway as pw
import os
from dotenv import load_dotenv
from common.embedder import index_embeddings,embeddings
from common.prompt_gen import prompt
from llm_app import chunk_texts, extract_texts
load_dotenv()

data_path=os.environ.get("LOCAL_PATH","/usr/local/documents")

def run(host,port):
    #User gives a query
    query,response_to_user=pw.io.http.rest_connector(host=host,
    port=port,
    schema=QueryInputSchema,
    autocommit_duration_ms=50)

    #realtime data coming from unstructured data source
    input_datasource=pw.io.fs.read(
        data_path,
        format="binary",
        autocommit_duration_ms=50
    )

    #Processing unstructured data from source

    #making input data into smaller documents
    documents=input_datasource.select(texts=extract_texts(pw.this.data))
    documents = documents.select(chunks=chunk_texts(pw.this.texts))
    documents=documents.flatten(pw.this.chunks).rename_columns(chunk=pw.this.chunks)


    #embedding the chunks
    embedded_data=embeddings(context=documents,data_to_embed=pw.this.chunk)

    #constructing index in realtime
    index_data=index_embeddings(embedded_data=embedded_data)

    #Generate embeding for user query
    embedded_query=embeddings(context=query,data_to_embed=pw.this.query)

    responses=prompt(index_data,embedded_query,pw.this.query)

    response_to_user(responses)
    
    #run the data pipeline

    pw.run()





class QueryInputSchema(pw.Schema):
    query: str