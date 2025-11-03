from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
import config 

def _call_llm_with_tracking(prompt_template: str, input_variables: dict, temperature: float = 0.2) -> tuple[str, dict]:
    """
    Função auxiliar que chama o LLM, rastrei o uso de tokens e aceita
    um dicionário de variáveis para o prompt.
    """

    prompt = PromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(api_key=config.OPEN_AI_API_KEY, model=config.GENERATION_MODEL, temperature=temperature)
    chain = prompt | llm | StrOutputParser()

    with get_openai_callback() as cb:
        result = chain.invoke(input_variables)
        token_info = {
            "prompt": cb.prompt_tokens,
            "completion": cb.completion_tokens,
            "total": cb.total_tokens,
            "cost_usf": cb.total_cost
        }

    return result, token_info