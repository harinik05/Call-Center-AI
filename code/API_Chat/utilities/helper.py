class LLMHelper:
    def __init__(self, custom_prompt="", temperature=0.7):
        self.custom_prompt = custom_prompt
        self.temperature = temperature

    def get_semantic_answer_lang_chain(self, question, history):
        # Simulated function for generating a response
        response = "This is a sample response."

        # Simulated function for processing history
        context = "This is the context based on history."
        
        # Simulated function for sourcing information
        sources = ["Source 1", "Source 2"]

        return question, response, context, sources
