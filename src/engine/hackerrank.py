import os

from llama_index.core import (SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex, load_index_from_storage)

data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def get_index(documents, index_name):
    index = None
    if not os.path.exists(index_name):
        print("building index", index_name)
        index = VectorStoreIndex.from_documents(documents=documents, show_progress=True)
        index.storage_context.persist(persist_dir=index_name)
    else:
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_name)
        )

    return index


data = SimpleDirectoryReader(data_path, required_exts=[".pdf"]).load_data()
hackerrank_engine = get_index(data, "skills_report").as_query_engine()
