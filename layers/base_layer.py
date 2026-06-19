from abc import ABC, abstractmethod
from typing import Optional

class BaseLayer(ABC):
    """
    Classe base abstrata para todas as camadas da arquitetura.
    Cada camada deve implementar o metodo handle()
    """

    @abstractmethod
    def handle(self, user_input: str) -> Optional[str]:
        """
        Processa a entrada do usuario e retorna uma resposta em texto.
        Se a camada não souber lidar, deve retornar None (para permitir fallback).
        """

    def can_handle(self, user_input: str) -> bool:
        """
        Verifica rapidamente se esta camada tem chance de lidar com a entrada.
        Pode ser sobrescrito pelas subclasses para otimização.
        Por padrão, retorna True, delegando a decisão ao handle().
        """
        return True