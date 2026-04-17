# Contribuindo para Video Dublagem Automática

Obrigado por considerar contribuir para nosso projeto! 🎉

## Como Começar

1. **Faça um fork** do repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/video-dublagem-automatica.git`
3. **Crie uma branch** para sua feature: `git checkout -b feature/minha-feature`
4. **Faça suas mudanças**
5. **Commit** suas mudanças: `git commit -am 'Add nova feature'`
6. **Push** para a branch: `git push origin feature/minha-feature`
7. **Abra um Pull Request**

## Código de Conduta

- Seja respeitoso com todos os contribuidores
- Respeite diferenças de opinião e experiência
- Forneça feedback construtivo
- Foco em problemas, não em pessoas

## Diretrizes de Contribuição

### Antes de Começar

- Verifique se sua issue/feature já não existe
- Leia a documentação (README, API docs, etc)
- Verifique o ROADMAP para prioridades

### Processo de Desenvolvimento

1. **Crie uma issue** descrevendo: problema, solução proposta, contexto
2. **Aguarde feedback** antes de começar a programar
3. **Desenvolvedor o código** seguindo as convenções
4. **Escreva testes** para sua feature
5. **Atualize documentação** se necessário
6. **Envie PR** com descrição clara

### Padrões de Código

#### Python
```python
# Use type hints
def my_function(param: str, number: int = 10) -> bool:
    """
    Descrição clara da função.
    
    Args:
        param: Descrição do parâmetro
        number: Outro parâmetro
        
    Returns:
        Descrição do retorno
    """
    pass

# Nomes convenientes
my_variable = "value"  # snake_case para variáveis
MyClass = object  # PascalCase para classes
MY_CONSTANT = 100  # UPPER_CASE para constantes

# Docstrings em português
class MyClass:
    """Descrição clara da classe"""
    pass
```

#### Imports
```python
# Ordem correta
import os
import sys

from typing import Dict, List

import requests
from fastapi import FastAPI

from app.config import settings
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Informação geral")
logger.warning("Aviso importante")
logger.error("Erro encontrado", exc_info=True)
```

### Commit Messages

```
[Tipo] Descrição concisa em português

Descrição detalhada se necessário
- Ponto 1
- Ponto 2

Fixes: #123
```

Tipos válidos:
- `feat:` - Nova feature
- `fix:` - Correção de bug
- `docs:` - Documentação
- `refactor:` - Refatoração
- `perf:` - Melhoria de performance
- `test:` - Testes
- `chore:` - Tarefas de manutenção

### Pull Requests

#### Template PR

```markdown
## Descrição
Descreva as mudanças neste PR

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Atualização de documentação

## Como Testar
Instruções para testar as mudanças

## Checklist
- [ ] Code segue o style do projeto
- [ ] Executou `test_setup.py`
- [ ] Atualizou documentação
- [ ] Não há erros de lint
- [ ] Adicionou testes se necessário
```

### Testes

```python
# Use pytest
def test_my_function():
    """Teste a função my_function"""
    result = my_function("input")
    assert result == expected_value
```

Executar testes:
```bash
pytest tests/ -v
```

### Documentação

Atualize:
- README.md se adicionar features
- API_DOCUMENTATION.md para endpoints
- ROADMAP.md se planejam próximas versões
- Docstrings nas funções

## Áreas para Contribuir

### 🚨 Prioridade Alta
- [ ] Performance improvements
- [ ] Bug fixes críticos
- [ ] Documentação
- [ ] Testes

### 📊 Prioridade Média
- [ ] Novas features (verificar ROADMAP)
- [ ] Refatoração de código
- [ ] Otimizações
- [ ] Exemplos de código

### 🎨 Prioridade Baixa
- [ ] Melhorias estéticas
- [ ] Comentários adicionais
- [ ] Reorganização

## Problemas Comuns

### "Não sei por onde começar"
1. Procure issues com tag `good-first-issue`
2. Leia o ROADMAP
3. Veja o código existente

### "Meu PR foi rejeitado"
1. Leia atentamente o feedback
2. Pergunte dúvidas nos comentários
3. Faça as mudanças solicitadas
4. Re-submit o PR

### "Conflito de merge"
```bash
git fetch upstream
git rebase upstream/main
# Resolva conflitos
git push -f origin seu-branch
```

## Recursos

- 📚 [Documentação completa](README.md)
- 🔧 [Setup local](CHECKLIST.md)
- 📖 [API Docs](API_DOCUMENTATION.md)
- 🗺️ [Roadmap](ROADMAP.md)

## Fazer uma Pergunta

- **Issues**: Para bugs e features
- **Discussions**: Para perguntas gerais
- **Email**: seu-email@example.com

## Reconhecimento

Todos os contribuidores serão mencionados em:
- README.md
- Releases notes
- Website (futuro)

---

**Obrigado por contribuir!** 🚀
