import os
import os.path
import logging
from typing import Any, List
from llama_index.core import Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core import (VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage)


# Use: https://github.com/run-llama/llama_index library to build knowledge base index
# By default, use the embedding_texts function in GeneralAgent.skills for embedding, you can override the embedding_texts function

# def new_embedding_texts(texts) -> [[float]]:
#     """
#     Perform embedding on text array
#     """
#     import os
#     client = _get_openai_client()
#     model = os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-small')
#     resp = client.embeddings.create(input=texts, model=model)
#     result = [x.embedding for x in resp.data]
#     return result
# from GeneralAgent import skills
# skills.embedding_texts = new_embedding_texts

class CustomEmbeddings(BaseEmbedding):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "CustomEmbeddings"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        from GeneralAgent import skills
        return skills.embedding_texts([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        from GeneralAgent import skills
        return skills.embedding_texts([text])[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        from GeneralAgent import skills
        return skills.embedding_texts(texts)

embed_model = CustomEmbeddings(embed_batch_size=16)
Settings.embed_model = embed_model


def create_llamaindex(data_dir, storage_dir, limit_count=1000000):
    """
    Create llamaindex index
    @param data_dir: Data directory
    @param storage_dir: Storage directory
    @param limit_count: Token count limit
    """
    documents = SimpleDirectoryReader(data_dir).load_data()
    # Limit token count
    total_count = 0
    for doc in documents:
        total_count += len(doc.get_content())
    # In English, one word has multiple letters, so multiply by 4
    if total_count > limit_count * 4:
        return None
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=storage_dir)
    return index


def load_llamaindex(storage_dir):
    """
    Load index from storage
    """
    storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
    index = load_index_from_storage(storage_context)
    return index


def _get_last_text_query(messages):
    if len(messages) == 0:
        return ''
    for index in range(len(messages) - 1, -1, -1):
        content = messages[index]['content']
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            for item in content:
                if item['type'] == 'text':
                    return item['text']
    return ''


def query_llamaindex(index, messages):
    query = _get_last_text_query(messages)
    nodes = index.as_retriever().retrieve(query)
    return '\n\n'.join([node.get_text() for node in nodes])


def retrieve_knowlege(storage_dir, messages) -> list:
    """
    Retrieve from knowledge base, return search results
    @param query_str: Query string
    @return: Search results, list of string
    """
    if len(messages) == 0:
        logging.info('messages is empty')
        return ''
    if not os.path.exists(storage_dir):
        logging.info(f'storage_dir {storage_dir} not exists')
        return ''
    query = _get_last_text_query(messages)
    index = load_llamaindex(storage_dir)
    return query_llamaindex(index, query)
