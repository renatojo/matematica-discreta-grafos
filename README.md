
# Algorito de Yen na busca de passagens aéreas

## Sobre o Projeto

Implementação do algoritmo de Yen para buscar as k passagens aéreas mais baratas que ligam um destino a uma origem, que podem haver conxões em vários aeroportos ou não.

## Instalação

```bash
# Clone o repositório
git clone https://github.com/renatojo/matematica-discreta-grafos.git

# Entre no diretório
cd matematica-discreta-grafos

# Instale as dependências
pip install -r requirements.txt
```

## ▶️ Como Executar

```bash
python -m web.servidor
```

## Como Utilizar

Será aberta uma guia em seu navegador com a interface visual do projeto. Escolha um destino, uma origem e determine k=número de rotas (quantidades de caminhos mínimos que o algorítmo encontrará).

## Estrutura do Projeto

```text
matematica-discreta-grafos/
├── algoritmo_de_yen/ # Implementação do algoritmo de yen em Python
├── dados_brutos/ # Tabelas da ANAC utilizadas para extrair preços de passagens aéreas que conectam aeroportos.
├── dados_processados/ # Tabelas criadas utilizando pandas, que são utilizadas ao longo do trabalho 
├── processamento/ # Scripts em python utilizados para criar as tabelas de dados_processados/
├── utilidades/ # Scripts em python úteis para a implementação do algoritmo de Yen no buscador de passagens
├── web/ # Implementação do servidor web, a interface visual do projeto, que mostra o algoritmo sendo aplicado a um buscador de passagens
├── README.md # Detalhamento da estrutura do projeto
└── requirements.txt # Bibliotecas que devem ser importadas
```

