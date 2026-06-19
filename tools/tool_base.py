from abc import ABC, abstractmethod

class BaseTool(ABC):
    """Interface que todas as ferramentas da Syna devem implementar."""

    @abstractmethod
    def can_handle(self, user_input: str) -> bool:
        """
        Retorna True se esta ferramenta consegue lidar com a entrada do usuário.
        Este método deve ser rápido e, idealmente, usar apenas regras locais (regex, plavras-chave).
        """
        pass

    @abstractmethod
    def execute(self, user_input: str) -> str:
        """
        Executa a ação da ferramenta e retorna a resposta que será exibida ao usuário.
        Pode envolver chamadas de API, acesso ao sistema, etc.
        """
        pass