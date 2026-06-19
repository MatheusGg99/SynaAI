# core/router.py
import re
from typing import List, Tuple

# Camada 1: Sistema (arquivos, apps, pastas, comandos do SO)
SYSTEM_PATTERNS = [
    (re.compile(r'\b(abrir?|iniciar?|executar?|rodar?)\s+(o\s+)?(terminal|console|bash|shell)\b', re.I), 0.9),
    (re.compile(r'\b(abrir?|iniciar?)\s+(o\s+)?(navegador|firefox|chrome|brave|edge)\b', re.I), 0.9),
    (re.compile(r'\b(mostrar?|listar?|exibir?)\s+(arquivos|pastas|diretórios?|documentos)\b', re.I), 0.8),
    (re.compile(r'\b(criar?|fazer)\s+(uma?\s+)?pasta\b', re.I), 0.8),
    (re.compile(r'\b(renomear|mover|copiar|apagar|deletar)\s+(arquivo|pasta)\b', re.I), 0.8),
    (re.compile(r'\b(uso|status)\s+(de|do)\s+(sistema|cpu|memória|ram|disco)\b', re.I), 0.7),
    # adicionar mais padrões conforme necessário
]

# Camada 2: Pesquisa WEB
WEB_PATTERNS = [
    (re.compile(r'\b(pesquisar?|buscar?|procurar?|google|internet?)\s+(sobre\s+)?', re.I), 0.9),
    (re.compile(r'\b(o\s+que\s+é|quem\s+é|defina|significado\s+de)\b', re.I), 0.6),
    (re.compile(r'\bnotícias?\s+(sobre|de)\b', re.I), 0.8),
    (re.compile(r'https://\S+', re.I), 0.95),
]

# Camada 3: Automation
AUTOMATION_PATTERNS = [
    (re.compile(r'\b(criar|fazer)\s+(um|uma)\s+(script|automação|rotina)\b', re.I), 0.9),
    (re.compile(r'\b(sequência|passo a passo|primeiro\s+depois)\b', re.I), 0.7),
    (re.compile(r'Traceback\s*\(most recent call last\)\s*:', re.I), 0.8),
    # Exemplos futuros: "compila o projeto e depois roda os testes"
]

# Camada 4: COnversa (fallback implicito, não precisa de padrões)

def classify_intent(user_input: str) -> List[Tuple[str, float]]:
    """
    Analisa a entrada do usuario e retorna uma lista de camadas candidatas com seus scores de confiança (0.0 a 1.0), ordenadas do maior para o menor.
    """
    candidates = []

    # Verifica cada padrão de cada camada
    for layer_name, patterns_list in [
        ("system", SYSTEM_PATTERNS),
        ("web", WEB_PATTERNS),
        ("automation", AUTOMATION_PATTERNS), 
    ]:
        max_score = 0.0
        for pattern, weight in patterns_list:
            if pattern.search(user_input):
                max_score = max(max_score, weight)
        if max_score > 0:
            candidates.append((layer_name , max_score))

    # Ordena por score decrescente
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates