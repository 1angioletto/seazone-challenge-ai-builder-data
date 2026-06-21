# Review — System Price v2

## Veredito

**Changes requested**

O PR não deve ser mergeado no estado atual. A intenção do pipeline está alinhada com o problema de negócio, mas a implementação tem problemas críticos que comprometem segurança, reprodutibilidade e correção da métrica gold.

## Top 3 problemas críticos

### 1. O filtro de "últimos 90 dias" usa a data atual do sistema

O código usa `datetime.now()` para calcular o cutoff do trimestre. Como os dados são snapshots históricos, o resultado depende do dia em que o pipeline é executado. Em uma execução futura, o filtro pode retornar zero linhas, mesmo com dados válidos no CSV.

O correto seria usar a maior data disponível no próprio dataset como referência, separando claramente data de aquisição e data de estadia.

### 2. A métrica System Price está contaminada com VivaReal

O PR concatena preços do Airbnb com `rental_price / 30` do VivaReal e calcula uma média única. Isso mistura fontes com naturezas diferentes: preço resolvido de short stay e aluguel/venda imobiliária. A gold deixa de representar o System Price do Airbnb.

VivaReal pode ser usado como contexto ou feature auxiliar, mas não deve entrar na média do System Price sem especificação explícita e validação estatística.

### 3. O pipeline não é idempotente

O SQL usa `CREATE TABLE IF NOT EXISTS` seguido de `INSERT INTO`. Cada execução duplica os resultados na tabela gold, alterando `n_amostras` e contaminando o dashboard.

A gold deveria ser recriada de forma determinística com `CREATE OR REPLACE TABLE` ou usar particionamento/chave de upsert.

## Outros problemas relevantes

- Credenciais hardcoded no código: `DB_USER` e `DB_PASSWORD`.
- Uso de `pandas` e `requirements.txt`, desalinhado com o padrão do desafio de `uv + pyproject.toml`.
- `try/except: pass` no carregamento dos CSVs silencia erro e dificulta diagnóstico.
- Risco de duplicidade no join com Mesh, pois `Mesh_Ids_Data_Itapema.csv` é incremental e pode conter múltiplos registros por listing.
- `cleaning_fee` é somado diretamente à diária, inflando o preço por noite sem amortização por duração da estadia.
- O SQL agrupa `suburb` sem tratar nulos.
- O SQL não arredonda nem documenta unidade monetária.
- O código cria `bairro_lower` com `iterrows()`, mas a coluna nunca é usada.
- Logs imprimem nomes de hosts, o que é desnecessário e pode expor informação sensível.
- A validação descrita no PR ("bati o olho no count") é insuficiente para uma tabela gold consumida por RM.

## O que falhou upstream

Esse PR não deveria ter chegado ao review humano nesse estado. O processo falhou em três pontos:

1. **Ausência de contrato claro da métrica gold**  
   A definição de System Price deveria explicitar fonte, granularidade, janela temporal, tratamento de snapshots, cleaning fee e regras de deduplicação.

2. **Falta de checklist automático antes do review**  
   Um pre-review automatizado deveria barrar credenciais hardcoded, uso de `requirements.txt`, ausência de idempotência e `try/except: pass`.

3. **Validação fraca da saída**  
   Para tabela gold, o PR deveria trazer asserts mínimos: número de bairros, ausência de nulos em bairro, não duplicação entre execuções, janela temporal efetiva e comparação com agregados esperados.

## Como eu conduziria o 1:1 com o Júnior

Eu começaria reconhecendo os pontos positivos do PR. A intenção de construir uma tabela gold para o time de Revenue Management está alinhada com a necessidade do negócio, e achei positivo o fato de já pensar em enriquecimentos futuros e em possíveis segmentações para o dashboard.

Em seguida, eu explicaria que os pontos levantados no review não são problemas de estilo de código ou preferência pessoal, mas sim questões relacionadas à confiança da métrica. Como essa tabela será consumida por outros times, é importante que ela seja determinística, reproduzível e tenha um contrato claro sobre o que representa.

Eu procuraria dividir a correção em pequenas etapas para não transformar o PR em algo muito grande ou desmotivador. Minha sugestão seria simplificar a primeira versão e evoluir gradualmente:

1. Começar utilizando apenas Price_AV_Itapema e o bairro vindo do Mesh.
2. Garantir que o Mesh esteja deduplicado utilizando o snapshot mais recente.
3. Basear a janela temporal na maior data disponível nos dados e não na data atual da máquina.
4. Tornar a tabela gold idempotente para garantir reprodutibilidade.
5. Adicionar algumas validações simples de qualidade para aumentar a confiança da saída.
6. Alinhar a implementação ao padrão do projeto (uv + pyproject.toml), removendo credenciais do código.

Também proporia uma sessão rápida de pareamento para revisar juntos a definição da métrica antes da reimplementação. Acredito que isso reduz retrabalho e ajuda a construir entendimento sobre o problema de negócio, em vez de apenas corrigir sintomas no código.

Meu objetivo seria que ele saísse da conversa entendendo não apenas o que mudar, mas principalmente por que essas mudanças são importantes, para que consiga aplicar esses princípios nos próximos pipelines de forma mais autônoma.

## Sugestão de comentários inline

### `pipelines/system_price_v2.py` — credenciais hardcoded

`DB_USER` e `DB_PASSWORD` não podem estar versionados. Mesmo não sendo usados no fluxo atual, credenciais em código são um risco de segurança e devem ser removidas. Use variáveis de ambiente ou secret manager quando houver conexão real.

### `load_csvs()` — `except Exception: pass`

Esse bloco silencia qualquer falha de leitura e deixa o pipeline quebrar depois com erro indireto. Para pipeline de dados, prefira falhar cedo com mensagem clara indicando qual arquivo não foi carregado.

### `filter_last_quarter()` — uso de `datetime.now()`

O filtro de trimestre não deve depender da data atual do sistema. Como a base é snapshot histórico, a janela precisa ser calculada a partir da maior data disponível no dataset. Além disso, precisamos separar data de aquisição e data de estadia.

### `enrich_with_bairro()` — join com Mesh

`Mesh_Ids_Data_Itapema` é incremental e pode ter múltiplas linhas por listing. Sem deduplicar pelo snapshot mais recente, esse join pode multiplicar linhas e distorcer a média por bairro.

### `build_stage()` — cleaning fee somado à diária

Somar `cleaning_fee` diretamente ao preço da diária infla o System Price. Se a taxa de limpeza for considerada, precisa ser amortizada por duração média da estadia ou analisada separadamente.

### `normalize_vivareal()` / `pd.concat`

Misturar `Price_AV` com `VivaReal.rental_price / 30` contamina a métrica. VivaReal é uma fonte complementar de mercado, não o System Price resolvido de short stay. Eu manteria VivaReal fora da gold principal ou em coluna separada com contrato explícito.

### `gold_system_price_itapema.sql` — `INSERT INTO`

O pipeline não é idempotente. Cada execução insere novamente os mesmos agregados na gold. Para tabela derivada, use `CREATE OR REPLACE TABLE` ou uma estratégia de upsert com chave de partição.

### `gold_system_price_itapema.sql` — nulos em bairro

A gold agrupa `suburb` sem tratar nulos. Isso cria bairro nulo no dashboard ou esconde problema de join. Devemos filtrar/rotular explicitamente e reportar taxa de cobertura de bairro.

