# Knowledge Base Interpreter
from .interpreter import Interpreter
from GeneralAgent.llamaindex import create_llamaindex, load_llamaindex, query_llamaindex

import os
import json
import shutil

class KnowledgeInterpreter(Interpreter):
    """
    Knowledge Base Interpreter, for parsing knowledge base queries
    """
    def __init__(self, workspace, knowledge_files=[], rag_function=None) -> None:
        """
        @param workspace: Working directory
        @param knowledge_files: List of knowledge base files, can be local or network files, e.g. ['http://xxx.txt', './xxx.pdf'], supports formats supported by llama library
        @param rag_function: Query function, takes a question as input, returns list of answers
        """
        self.workspace = workspace
        self.knowledge_files = knowledge_files
        self.rag_function = rag_function
        self.work = len(knowledge_files) > 0 or (rag_function is not None)

        if len(knowledge_files) > 0:
            self._create_index()
        else:
            self.index = None

    def _create_index(self):
        """
        Build index
        """
        llama_dir = os.path.join(self.workspace, 'llama')
        meta_path = os.path.join(llama_dir, 'meta.json')
        data_dir = os.path.join(llama_dir, 'data')
        storage_dir = os.path.join(llama_dir, 'storage')

        if not os.path.exists(llama_dir):
            os.makedirs(llama_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        # Check if index needs to be rebuilt
        files_change = False
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            # Use set to compare if two lists are equal
            if set(meta['knowledge_files']) != set(self.knowledge_files):
                files_change = True
        else:
            files_change = True

        # If files have changed, rebuild index
        if files_change:
            # Delete all files in data directory & use shutil library to copy knowledge_files to data directory
            for file in os.listdir(data_dir):
                os.remove(os.path.join(data_dir, file))
            for file in self.knowledge_files:
                # If file is a network file, download to data directory
                if file.startswith('http'):
                    import requests
                    res = requests.get(file)
                    file_name = file.split('/')[-1]
                    with open(os.path.join(data_dir, file_name), 'wb') as f:
                        f.write(res.content)
                else:
                    file_name = os.path.basename(file)
                    shutil.copy(file, os.path.join(data_dir, file_name))
            self.index = create_llamaindex(data_dir, storage_dir)
            with open(meta_path, 'w') as f:
                json.dump({'knowledge_files': self.knowledge_files}, f)
        else:
            self.index = load_llamaindex(storage_dir)

    def prompt(self, messages) -> str:
        if len(messages) == 0:
            return ''
        if len(self.knowledge_files) == 0 and self.rag_function is None:
            return ''
        background = 'Background:'
        if len(self.knowledge_files) > 0:
            background += query_llamaindex(self.index, messages)
        if self.rag_function is not None:
            background += '\n' + self.rag_function(messages)
        return background
