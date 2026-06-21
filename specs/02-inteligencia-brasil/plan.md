# Plan — Inteligência Brasil

## Princípio

O objetivo não é construir uma plataforma completa de uma vez.

Queremos evoluir em pequenas entregas, validando continuamente com os times que vão consumir o produto.

Cada fase deve gerar valor por si só e reduzir o risco das próximas etapas.

---

## Fase 1 — Primeira versão do produto

### Times envolvidos

- Data Edge
- Acquisition

### Objetivo

Sair do modelo totalmente manual e disponibilizar uma primeira visão consolidada para algumas cidades prioritárias.

### Entregas

- Estrutura Bronze, Silver e Gold.
- Primeiras tabelas de negócio.
- Dashboard interno.
- Atualização semanal.

### Validação

Revenue Management.

### Principais riscos

Baixa confiança nos dados.

### Mitigação

Comparar os resultados com as análises já realizadas manualmente.

---

## Fase 2 — Escala controlada

### Times envolvidos

- Data Edge
- Core

### Objetivo

Expandir a cobertura para mais cidades e aumentar a confiança das métricas.

### Entregas

- Score por região.
- Perfil ideal dos imóveis.
- Indicadores de ROI.
- Evolução das tabelas Gold.

### Validação

Acquisition.

### Principais riscos

Crescimento da complexidade.

### Mitigação

Evoluir os modelos de dados e reforçar contratos entre produtores e consumidores.

---

## Fase 3 — Cobertura nacional

### Times envolvidos

- Data Edge
- Core
- Acquisition

### Objetivo

Permitir que o produto funcione para qualquer cidade do Brasil.

### Entregas

- Granularidade espacial escalável.
- Ranking nacional.
- APIs internas.
- Atualizações mais frequentes.

### Validação

Origination.

### Principais riscos

Custos e crescimento da volumetria.

### Mitigação

Particionamento adequado e revisão constante dos custos.

---

## Fase 4 — Camada de inteligência

### Objetivo

Facilitar o acesso às informações e reduzir análises manuais.

### Entregas

- Assistentes internos.
- APIs para agentes.
- Consultas em linguagem natural.
- Recomendações automáticas.

### Validação

Todos os times consumidores.

### Principais riscos

Adicionar complexidade antes da maturidade do produto.

### Mitigação

Priorizar funcionalidades de acordo com a demanda dos usuários.

---

## Dependências

As evoluções devem seguir uma sequência simples:

Dados brutos

↓

Camada de transformação

↓

Tabelas de negócio

↓

Dashboards

↓

APIs

↓

Assistentes e agentes

---

## Como vamos medir sucesso

Mais importante do que quantidade de dados é a adoção do produto.

Os principais indicadores serão:

- Redução de análises manuais.
- Tempo para responder perguntas de negócio.
- Frequência de utilização pelos times.
- Confiança nas métricas.
- Velocidade para expandir para novas cidades.

