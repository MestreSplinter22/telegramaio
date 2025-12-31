# Estrutura Modular do Flow Editor

## Visão Geral
O código do flow_editor.py foi modularizado em componentes menores e mais gerenciáveis, seguindo boas práticas de arquitetura de software.

## Estrutura de Arquivos

```
dashboard/components/flow_editor_components/
├── __init__.py                 # Módulo inicial
├── theme.py                   # Constantes de tema e estilos
├── button_item.py             # Componente de botão individual
├── media_section.py           # Seção de mídia (imagem/vídeo)
├── payment_section.py         # Seção de configuração de pagamento
├── text_section.py            # Seção de conteúdo textual
├── buttons_section.py         # Seção de botões de interação
└── block_component.py         # Componente principal do bloco
```

## Descrição dos Componentes

### 1. `theme.py`
- Contém todas as constantes de estilo e cores
- Define o sistema de design consistente
- Exporta função `section_header()` para cabeçalhos padronizados

### 2. `button_item.py`
- Componente responsável por renderizar botões individuais
- Gerencia edição de texto, tipo (callback/url) e destino
- Inclui lógica de remoção de botões

### 3. `media_section.py`
- Gerencia a seção de mídia (imagens e vídeos)
- Permite seleção de tipo de mídia e entrada de URL
- Apenas visível em blocos não-pagamento

### 4. `payment_section.py`
- Configura parâmetros de transação de pagamento
- Seleção de gateway (suitpay, efibank, openpix)
- Configuração de valor monetário

### 5. `text_section.py`
- Seção de conteúdo textual principal
- Área de texto expansível para mensagens
- Inclui funcionalidade de adição de badges (exceto em pagamentos)

### 6. `buttons_section.py`
- Gerencia linhas e colunas de botões
- Funcionalidade de adicionar novas linhas
- Scroll horizontal para múltiplos botões
- Importa e utiliza `button_item.py`

### 7. `block_component.py`
- Componente principal que orquestra todas as seções
- Determina se é bloco de pagamento ou mensagem normal
- Monta o layout completo do card
- Importa todos os outros componentes

### 8. `flow_editor.py` (atualizado)
- Arquivo principal reduzido e simplificado
- Importa apenas o componente principal `render_block`
- Mantém a lógica de container e controle de fluxo

## Benefícios da Modularização

1. **Manutenibilidade**: Cada componente tem responsabilidade única
2. **Reusabilidade**: Componentes podem ser usados em outras partes
3. **Testabilidade**: Mais fácil escrever testes unitários
4. **Legibilidade**: Código mais organizado e compreensível
5. **Escalabilidade**: Fácil adicionar novas funcionalidades

## Como Usar

O uso permanece o mesmo na aplicação principal:

```python
from dashboard.components.flow_editor import flow_editor_component

# Em sua página Reflex
rx.box(
    flow_editor_component(),
    width="100%",
    height="100vh"
)
```

## Próximos Passos Sugeridos

1. Criar testes unitários para cada componente
2. Adicionar documentação específica para cada módulo
3. Considerar extrair estilos para arquivos CSS separados
4. Implementar sistema de validação de dados nos componentes