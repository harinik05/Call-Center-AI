import json
import logging
import uuid
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

logger = logging.getLogger()

'''
RedisExtended inherits from the base class Redis. Extends and customizes the 
functionality of the base redis class
'''
class RedisExtended(Redis):

    '''
    Constructor of the RedisExtended class is defined with some of these params
    '''
    def __init__(
        self,
        redis_url: str,
        index_name: str,
        embedding_function: Callable,
        **kwargs: Any,
    ):
        
        '''
        constructor of the base class to initialize the common attributes 
        '''
        super().__init__(redis_url, index_name, embedding_function)
        
        '''
        checks if certain redis prompt indexes and specified index name exists
        '''
        try:
            self.client.ft("prompt-index").info()
        except: 
            '''
            creates the index if it doesnt already exist
            '''
            self.create_prompt_index()

        try:
            self.client.ft(self.index_name).info()
        except:
            # Create Redis Index
            self.create_index()

    '''
    checks if the specified index exists in redis
    '''
    def check_existing_index(self, index_name: str = None):
        try:
            self.client.ft(index_name if index_name else self.index_name).info()
            return True
        except:
            return False

    '''
    Deletes the keys (data) from Redis either specified individually or based on 
    some kind of a pattern
    '''
    def delete_keys(self, keys: List[str]) -> None:
        for key in keys:
            self.client.delete(key)
    
    def delete_keys_pattern(self, pattern: str) -> None:
        keys = self.client.keys(pattern)
        self.delete_keys(keys)

    '''
    creates index
    '''
    def create_index(self, prefix = "doc", distance_metric:str="COSINE"):
        content = TextField(name="content")
        metadata = TextField(name="metadata")
        content_vector = VectorField("content_vector",
                    "HNSW", {
                        "TYPE": "FLOAT32",
                        "DIM": 1536,
                        "DISTANCE_METRIC": distance_metric,
                        "INITIAL_CAP": 1000,
                    })
        # Create index
        self.client.ft(self.index_name).create_index(
            fields = [content, metadata, content_vector],
            definition = IndexDefinition(prefix=[prefix], index_type=IndexType.HASH)
        )

    # Prompt management
    def create_prompt_index(self, index_name="prompt-index", prefix = "prompt"):
        result = TextField(name="result")
        filename = TextField(name="filename")
        prompt = TextField(name="prompt")
        # Create index
        self.client.ft(index_name).create_index(
            fields = [result, filename, prompt],
            definition = IndexDefinition(prefix=[prefix], index_type=IndexType.HASH)
        )

    '''
    adds data to the related prompt result in redis
    '''
    def add_prompt_result(self, id, result, filename="", prompt=""):
        self.client.hset(
            f"prompt:{id}",
            mapping={
                "result": result,
                "filename": filename,
                "prompt": prompt
            }
        )

    '''
    gets the prompt results depending on whatever prompt index you give and returns it 
    as a pandas dataframe
    '''
    def get_prompt_results(self, prompt_index_name="prompt-index", number_of_results: int=3155):
        base_query = f'*'
        return_fields = ['id','result','filename','prompt']
        query = Query(base_query)\
            .paging(0, number_of_results)\
            .return_fields(*return_fields)\
            .dialect(2)
        results = self.client.ft(prompt_index_name).search(query)
        if results.docs:
            return pd.DataFrame(list(map(lambda x: {'id' : x.id, 'filename': x.filename, 'prompt': x.prompt, 'result': x.result.replace('\n',' ').replace('\r',' '),}, results.docs))).sort_values(by='id')
        else:
            return pd.DataFrame()

    '''
    deletes the results from the prompt
    '''
    def delete_prompt_results(self, prefix="prompt*"):
        self.delete_keys_pattern(pattern=prefix)