FORMULA_MAPPING_PROMPT = """
Sua tarefa é atuar como um especialista no conteúdo e analisar o texto para extrair e catalogar todas as **fórmulas e regras de cálculo gerais e reutilizáveis**.

**REGRAS:**
1.  Extraia tanto fórmulas simbólicas (ex: `J = C*i*t`) quanto textuais (ex: `Montante = Capital + Juros`).
2.  Para cada fórmula encontrada, liste os principais conceitos-chave do texto aos quais ela se aplica diretamente.
3.  **IGNORE** exemplos de cálculos que usam apenas números específicos e concretos (ex: "R$ 1000 + R$ 50 = R$ 1050"). Extraia apenas a regra geral.
4.  Sua resposta deve ser uma lista de objetos JSON. Se nenhuma fórmula geral for encontrada, retorne uma lista vazia `[]`.

**EXEMPLO DE COMPORTAMENTO ESPERADO:**

**Texto de Exemplo para Análise:**
"Para calcular o montante, usamos a regra: Montante = Capital + Juros. Por exemplo, se o capital é R$ 1000 e os juros são R$ 50, o montante é R$ 1000 + R$ 50 = R$ 1050. A fórmula simbólica para juros simples é J = C*i*t."

**Sua Saída Perfeita (JSON):**
[
  {{
    "formula": "J = C * i * t",
    "concepts": ["juros simples", "cálculo de juros", "capital", "taxa de juros"],
    "description": "Fórmula para calcular juros simples."
  }},
  {{
    "formula": "Montante = Capital + Juros",
    "concepts": ["montante", "juros simples", "capital"],
    "description": "Fórmula para calcular o montante final em um regime de juros simples."
  }}
]
---
**Texto para Análise:**
{chapter_text}
"""