# Spec — Inteligência Brasil

## Objetivo

O Inteligência Brasil nasce para transformar análises que hoje são feitas manualmente em um produto interno capaz de apoiar decisões em escala nacional.

A ideia não é substituir o conhecimento das pessoas, mas permitir que Revenue Management, Acquisition e Origination tenham acesso às mesmas informações, utilizando critérios consistentes e reproduzíveis.

---

## Quem utiliza

### Revenue Management

Busca entender oferta, demanda e perfil dos imóveis para apoiar decisões de preço e posicionamento.

### Acquisition

Busca identificar regiões com maior potencial de retorno e apoiar decisões de investimento.

### Origination

Busca priorizar cidades e regiões com maior oportunidade de expansão.

---

## O que queremos substituir

Hoje boa parte das análises é feita cidade por cidade e depende de consolidações manuais.

O produto existe para reduzir esse trabalho e permitir que as decisões sejam tomadas com mais velocidade e consistência.

Nosso objetivo é diminuir a dependência de planilhas e análises pontuais, criando uma visão única do mercado.

---

## Como imaginamos a atualização dos dados

No início, uma atualização semanal é suficiente.

Conforme o produto evoluir e aumentar o número de consumidores, a expectativa é chegar a atualizações diárias.

A frequência deve acompanhar a necessidade do negócio, evitando complexidade desnecessária.

---

## Quais informações alimentam o produto

O produto combina diferentes fontes de informação.

Entre elas:

- Dados do Airbnb;
- Informações de mercado vindas de portais imobiliários;
- Dados externos relacionados a sazonalidade e eventos;
- Informações complementares inseridas manualmente quando necessário.

Novas fontes poderão ser incorporadas conforme surgirem novas necessidades.

---

## Como as informações serão consumidas

O principal consumo será através das tabelas gold utilizadas pelos times internos.

Além disso, o produto poderá ser disponibilizado através de:

- Dashboards internos;
- APIs;
- Agentes e assistentes capazes de responder perguntas em linguagem natural.

O objetivo é facilitar o acesso às informações, independentemente da ferramenta utilizada.

---

## Como enxergamos o espaço e o tempo

Queremos uma solução que funcione para qualquer cidade do Brasil.

Por isso, a granularidade espacial precisa ser flexível e escalável, permitindo agregações em diferentes níveis conforme a necessidade.

Da mesma forma, as análises serão construídas a partir de dados diários, permitindo visões semanais, mensais e trimestrais.

---

## Organização dos dados

Os dados brutos serão preservados.

As transformações e enriquecimentos ficarão em uma camada intermediária.

As métricas prontas para consumo ficarão em uma camada de negócio, responsável por atender os usuários do produto.

Essa separação busca facilitar manutenção, auditoria e evolução da plataforma.

---

## Evolução esperada

A primeira versão do produto precisa ser simples e resolver problemas reais.

Conforme o uso aumentar, novas capacidades poderão ser adicionadas.

A evolução deve ser guiada pelas necessidades dos usuários e não pela vontade de adicionar mais tecnologia.

---

## O que não faz parte do escopo inicial

Não pretendemos resolver todos os problemas na primeira versão.

Modelos complexos, processamento em tempo real e funcionalidades avançadas podem fazer sentido no futuro, mas não são prioridade neste momento.

O foco inicial é construir uma base sólida, simples e confiável.
