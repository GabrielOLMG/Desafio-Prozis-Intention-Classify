# Desafio Prozis

## 📌 Objetivo

O desafio tem como objetivo desenvolver uma **API REST** que recebe uma frase de texto do utilizador e que classifique em uma das seguintes classes:

- unknown_intention
- confirm_order
- go_to_shopping_cart
- add_to_cart
- product_info
- search_product

---

## 🧠 Arquitetura e Solução

A arquitetura escolhida foi baseada no framework Django, por ser uma tecnologia com a qual tenho mais prática e também por estar alinhada com minha linguagem de maior domínio: Python.

O projeto foi dividido em dois grandes processos:

1. **Filtragem de Labels via Clustering**
   Neste processo, o objetivo foi reduzir o conjunto total de labels (seis, conforme definido no desafio) para um subconjunto mais relevante — geralmente com até quatro opções.
   Essa filtragem ajuda a minimizar erros de ambiguidade que podem ocorrer no modelo zero-shot. Para isso, foram utilizadas:

   - **Embeddings de texto** com SentenceTransformers
   - **LDA** (Linear Discriminant Analysis) para projeção em dimensões menores com maior separação entre classes
   - **KNN** para identificar as labels mais próximas com base nas intenções já conhecidas

2. **Classificação com Zero-Shot**
   Após a filtragem, o modelo `xlm-roberta-large-xnli` (pré-treinado para tarefas de inferência textual) é utilizado para realizar a classificação final.
   Ele avalia as opções filtradas e retorna a label mais provável, junto com um score de confiança.

---

## ⚙️ Tecnologias e Bibliotecas

- **Django + Django REST Framework**: estrutura base da API e organização do backend

  - `django-constance`: facilita a definição de constantes via painel administrativo, permitindo ajustes rápidos de parâmetros
  - `django-modeladmin-reorder`: reorganiza o menu do Django Admin, melhorando a usabilidade e escondendo seções irrelevantes
  - `django-filebrowser-no-grappelli`: permite visualizar facilmente os arquivos gerados, como modelos `.pkl` salvos
  - `django-import-export`: permite importar/exportar dados diretamente pelo admin — aplicado em modelos específicos

- **HuggingFace Transformers** (`pipeline`): utilizado com o modelo `xlm-roberta-large-xnli` para classificação zero-shot
- **SentenceTransformers**: geração de embeddings semânticos das frases dos usuários
- **Scikit-learn**:

  - `KNN`: aplicado para clusterização e filtragem de labels com base em vizinhança semântica
  - `LDA`: projeção dos embeddings para aumentar a separação entre classes

- **Pickle**: utilizado para persistir modelos e componentes treinados, evitando retrabalho e otimizando o tempo de resposta

---

## 🧠 Decisões Técnicas e Justificativas

### 1. Divisão em dois processos: Cluster de Labels + Zero-Shot

A decisão de dividir a solução em dois processos teve como principal objetivo reduzir o custo
computacional do modelo zero-shot.

Imagine, por exemplo, que no futuro o modelo seja substituído por um mais robusto
(e possivelmente pago). Ao reduzir a quantidade de labels enviadas para ele, diminuímos o
número de comparações necessárias — e, consequentemente, o custo de inferência.

Além disso, essa divisão permite evitar ambiguidades quando um sistema de clusterização eficaz
é utilizado. Em casos ideais, o próprio cluster já pode indicar com segurança a intenção do
usuário, tornando desnecessário acionar o modelo zero-shot — uma melhoria futura ainda não
implementada, mas considerada durante o design da arquitetura.

### 2. Uso de LDA na filtragem

O uso do LDA (Linear Discriminant Analysis) teve como principal objetivo aumentar a separação
entre as classes conhecidas.

Com isso, ao aplicar o KNN sobre os embeddings projetados, os textos ficam mais bem agrupados
de acordo com seus respectivos clusters, melhorando a qualidade da vizinhança.

Além disso, a projeção ajuda a reduzir ruídos e sobreposição entre classes, sem comprometer
o significado semântico original das frases.

### 3. Aplicação de KNN com distância ponderada

O KNN foi utilizado para identificar as labels mais próximas com base nos embeddings projetados.

Além de facilitar a adaptação a novos dados sem re-treinamento, ele fornece uma métrica de
relevância natural por meio da distância entre os pontos.

### 4. Uso de Zero-Shot ao final

Durante os testes, considerei usar modelos conversacionais e classificadores diretos,
mas o que apresentou melhor desempenho geral foi o modelo zero-shot. Esse tipo de modelo
já é projetado para classificar textos com base nas labels fornecidas.

Foram testados diversos modelos disponíveis na Hugging Face, priorizando aqueles voltados
para zero-shot classification e com maior número de downloads. Entre eles, o que apresentou
os melhores resultados foi o `xlm-roberta-large-xnli`.

Além disso, ele fornece um score para cada label avaliada, permitindo calcular
a confiança. No meu caso, uso a label com o score mais alto como resultado final.

O modelo zero-shot também depende de um parâmetro chamado `hypothesis_template`,
que serve como base textual para formular a hipótese da classificação. Esse foi um dos
elementos mais ajustados durante os testes, e explico mais sobre ele na próxima seção.

### 5. Escolha da hipótese no zero-shot

A _hypothesis_ no modelo zero-shot serve para contextualizar a frase do usuário.
Por exemplo, se o texto for `"comprar creatina"`, e a hipótese for `"O usuário está tentando {}"`, o modelo irá avaliar:
`"O usuário está tentando comprar creatina"`.

A hipótese escolhida foi exatamente essa: `"O usuário está tentando {}"`.
Para chegar a essa formulação, testei diferentes variações de hipóteses em conjunto com
o mesmo modelo, comparando os resultados e optando por aquela que gerava maior coerência
e confiança na classificação final.

---

## 🧩 Limitações e Possíveis Melhorias

### 🔸 Limitações e Problemas Conhecidos

- As labels precisam estar previamente cadastradas no sistema (modelo Django `UserIntention`), junto com a sua tradução em português (`ml_text`).
  Essa tradução é necessária para que o modelo zero-shot possa comparar corretamente, evitando inconsistências entre rótulos em inglês e textos em português.

- O modelo zero-shot é altamente sensível tanto às labels quanto ao `hypothesis_template`.
  Isso faz com que algumas frases sejam interpretadas de forma diferente do esperado, mesmo que semanticamente corretas.

- Há uma confusão frequente entre as intenções `"add_to_cart"` e `"go_to_shopping_cart"`, mesmo com filtragem.
  Isso se deve à semelhança contextual entre essas intenções em frases curtas e diretas.

- Frases ambíguas continuam sendo um desafio.
  Mesmo com o uso de KNN para filtragem, ainda existem casos em que a intenção correta é subjetiva.

- Certos produtos não são bem interpretados dependendo da formulação da pergunta.
  Por exemplo:
  - `"como devo tomar whey"` → classificado como `"unknown_intention"`
  - `"como devo tomar creatina"` → corretamente classificado como `"product_info"`

### 🔧 Possíveis Melhorias

- **Hypothesis dinâmica por contexto**
  O ideal seria adaptar o `hypothesis_template` dinamicamente de acordo com as labels filtradas.
  Exemplo: se as labels forem `"search_product"` e `"product_info"`, o template pode usar algo como `"O usuário quer saber sobre {}"`,
  ao invés de manter uma frase genérica para todos os casos, incluindo ações como `"add_to_cart"`.

- **Fallback com base no cluster**
  Em situações de baixa confiança no zero-shot, a resposta poderia vir diretamente do cluster (KNN), desde que a similaridade fosse suficientemente alta.
  Hoje, o modelo zero-shot é sempre o responsável final pela decisão, mesmo quando sua confiança é baixa.

- **Aprimorar o processo de treino do KNN**
  Criar um endpoint para enviar novos exemplos que atualizariam o modelo de KNN, mas **apenas se ele superasse a versão anterior** nos testes definidos em `UnitTest`.

- **Exploração do sistema de KNN em múltiplos contextos**
  Mesmo quando o score de similaridade não é muito alto, o processo de clustering frequentemente retorna o cluster correto entre as opções disponíveis.
  Em uma aplicação real, como um sistema de chat, seria possível exibir ao usuário as 2 ou 3 intenções mais prováveis quando os scores estiverem muito próximos.

  Isso traria vantagens em dois aspectos:

  1. **Experiência do usuário**: o usuário poderia escolher rapidamente a intenção correta clicando em uma sugestão, acelerando o fluxo da conversa.
  2. **Coleta de dados supervisionados**: ao registrar as escolhas do usuário, o sistema pode gerar novos exemplos reais de texto vs intenção, enriquecendo automaticamente o conjunto de treino para o modelo de KNN.

  Com isso, o sistema evoluiria de forma assistida no início, mas com potencial de se tornar 100% automático no futuro com base nos dados coletados.

---

## 📁 Estrutura do Projeto

### Estrutura Geral

A pasta principal é `desafio_prozis`, que contém os apps principais e o diretório `media/` (onde os modelos `.pkl` são salvos).

Cada app criada, `core` e `ml_models`, segue a estrutura a seguir:

1. **admin/**: Registro dos modelos no Django Admin.
2. **migrations/**: Arquivos de migração, responsáveis por refletir alterações nos modelos no banco de dados.
3. **models/**: Contém os modelos Django. Cada modelo está separado em arquivos diferentes para melhor organização.
4. **views/**: Views do Django (não utilizadas neste projeto, mas mantidas por padrão).
5. **apps.py**: Definição da app.
6. **urls.py**: Registro das URLs da app. Não utilizado diretamente aqui, mas importante caso a app tenha rotas próprias.

#### 🔸 Pastas exclusivas da app `ml_models`:

1. **workflows/**: Contém toda a lógica de machine learning (ex: clusterização, embeddings, classificação zero-shot).
2. **tests/**: Testes unitários da API REST.
3. **api/**: Implementação da API REST (views, serializers, URLs).

#### 🔸 Outros arquivos importantes do projeto:

1. **config/settings/base.py**: Configurações globais do Django. Apps são registrados aqui via `LOCAL_APPS`.
2. **config/urls.py**: Registro das URLs globais do projeto, incluindo as da API.
3. **compose/local/django/Dockerfile**: Dockerfile para criação do ambiente.
4. **requirements/**: Contém os arquivos de dependências. O principal é `base.txt`.
5. **docker-compose.docs.yml**: Configuração adicional para serviços (por exemplo, documentação, docs preview, etc).

---

### Estrutura dos Apps

#### 1. `core/`

App responsável por armazenar os modelos diretamente ligados à lógica do site.

##### 📌 Modelos Django:

- **UserIntention**: Guarda as intenções que o sistema precisa reconhecer. Cada label deve ter uma versão em inglês (`text`) e uma versão em português (`ml_text`), que é usada na classificação.

No futuro, essa app poderá incluir modelos como: histórico do usuário, produtos, detalhes do produto, entre outros.

#### 2. `ml_models/`

App voltada para toda a lógica de classificação e workflows de machine learning.

- **`label_clustering.py`**: Contém funções para agrupar e filtrar labels com base em embeddings + KNN.
- **`zero_shot_classifier.py`**: Contém a lógica de classificação com modelos zero-shot.
- **`user_intention_classifier.py`**: Ponto central que une o clustering com o modelo zero-shot para decidir a intenção final.

##### 📌 Modelos Django:

- **UnitTest**: Permite armazenar casos de teste para avaliar o desempenho do modelo.
  O campo `custom_test` diferencia se o exemplo é de treino (usado para KNN) ou de teste (fornecido pelo desafio).
  A ideia é expandir continuamente os exemplos de treino, melhorando a generalização do modelo de KNN ao longo do tempo.

---

## 🔍 Como Executar Testes Automatizados e endpoinnt

### API REST

Como pedido no desafio, foi feito um endpoint chamado `/classify`. É possivel testar esse end point ou atravez do localhot, indo até a url:

    http://localhost:8001/api/classify

Ou tambem pode ser feito via curl, no terminal:

```bash
 curl -X POST http://localhost:8001/api/classify  -H "Content-Type: application/json"  -d '{"text": "como devo tomar  creatina"}'
```

### Tests

Para aplicar testes basta fazer no terminal:

```bash
 just manage test

```

qualquer outro teste deve ser implementado em:

    desafio_prozis/ml_models/tests/test_api_classify.py

### Admin

Para

---

## 🧪 Como Rodar Localmente

### 1. Clone o projeto

```bash
git clone git@github.com:GabrielOLMG/desafio_prozis.git
cd nome-do-projeto
```
