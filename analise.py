import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_squared_error
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import random

# Geração do dataset com dados distintos
n_linhas = 1000
ids = list(range(101, 101 + n_linhas))
idades = [random.randint(18, 75) for _ in range(n_linhas)]
generos = [random.choices(["Feminino", "Masculino"], weights=[0.6, 0.4])[0] for _ in range(n_linhas)]
cidades = [random.choice(["Fortaleza", "São Paulo", "Rio de Janeiro", "Salvador", "Belo Horizonte"]) for _ in range(n_linhas)]
estados = {
    "Fortaleza": "Ceará",
    "São Paulo": "São Paulo",
    "Rio de Janeiro": "Rio de Janeiro",
    "Salvador": "Bahia",
    "Belo Horizonte": "Minas Gerais",
}
produtos_variados = [
    "Tênis", "Meia", "Camiseta", "Assinatura", "Transporte", "Jaqueta",
    "Relógio", "Calça", "Boné", "Chinelo", "Óculos", "Mochila", "Carteira"
]
avaliacoes = ["Excelente", "Boa", "Neutra", "Ruim", "Péssimo"]
pagamentos = ["Pix", "Crédito", "Débito", "Dinheiro"]
pagamento_pesos = [0.5, 0.3, 0.15, 0.05]  # Pix como o método preferido

expanded_data = []
for i in range(n_linhas):
    cliente_id = ids[i]
    idade = idades[i]
    genero = generos[i]
    cidade = cidades[i]
    estado = estados[cidade]
    num_produtos = random.randint(1, min(6, len(produtos_variados)))
    produtos_comprados = random.sample(produtos_variados, num_produtos)
    valores = [round(random.uniform(10, 500), 2) for _ in produtos_comprados]
    data_inicial = datetime(2023, 1, 1)
    datas_compras = [data_inicial + timedelta(days=random.randint(0, 365)) for _ in produtos_comprados]
    avaliacoes_aleatorias = random.sample(avaliacoes, min(len(produtos_comprados), len(avaliacoes)))
    pagamentos_aleatorios = random.choices(pagamentos, weights=pagamento_pesos, k=len(produtos_comprados))

    for produto, valor, data_compra, avaliacao, pagamento in zip(
            produtos_comprados, valores, datas_compras, avaliacoes_aleatorias, pagamentos_aleatorios
    ):
        expanded_data.append({
            "ID_Cliente": cliente_id,
            "Idade": idade,
            "Gênero": genero,
            "Cidade": cidade,
            "Estado": estado,
            "Produto": produto,
            "Valor": valor,
            "Data_Compra": data_compra.strftime("%Y-%m-%d"),
            "Avaliacao": avaliacao,
            "Pagamento": pagamento
        })

# Criar o dataset e salvar em uma variável
dataset = pd.DataFrame(expanded_data)

# Análise Exploratória de Dados (EDA)
print("Resumo do Dataset:\n", dataset.head())
print("\nInformações Gerais:\n")
dataset.info()

# Produtos mais vendidos
plt.figure(figsize=(12, 6))
sns.countplot(data=dataset, x='Produto', order=dataset['Produto'].value_counts().index)
plt.title("Distribuição de Produtos Mais Comprados")
plt.xlabel("Produto")
plt.ylabel("Quantidade de Compras")
plt.xticks(rotation=45)
plt.show()

# Distribuição de avaliações
plt.figure(figsize=(8, 4))
sns.countplot(data=dataset, x='Avaliacao', palette="viridis")
plt.title("Distribuição de Avaliações")
plt.xlabel("Avaliação")
plt.ylabel("Frequência")
plt.show()

# Distribuição por métodos de pagamento
plt.figure(figsize=(8, 4))
sns.countplot(data=dataset, x='Pagamento', palette="muted", order=dataset['Pagamento'].value_counts().index)
plt.title("Distribuição dos Métodos de Pagamento")
plt.xlabel("Método de Pagamento")
plt.ylabel("Frequência")
plt.show()

# Distribuição de valores de compra
plt.figure(figsize=(10, 5))
sns.histplot(dataset['Valor'], kde=True, bins=30, color="blue")
plt.title("Distribuição de Valores das Compras")
plt.xlabel("Valor (R$)")
plt.ylabel("Frequência")
plt.show()

# Análise por gênero
plt.figure(figsize=(10, 5))
sns.countplot(data=dataset, x='Gênero', palette="pastel")
plt.title("Distribuição por Gênero")
plt.xlabel("Gênero")
plt.ylabel("Frequência")
plt.show()

# Preparação dos Dados
encoder = LabelEncoder()
dataset['Produto_Encoded'] = encoder.fit_transform(dataset['Produto'])
dataset['Pagamento_Encoded'] = encoder.fit_transform(dataset['Pagamento'])
dataset['Gênero_Encoded'] = encoder.fit_transform(dataset['Gênero'])
scaler = StandardScaler()
dataset['Valor_Scaled'] = scaler.fit_transform(dataset[['Valor']])

X = dataset[['Idade', 'Gênero_Encoded', 'Produto_Encoded', 'Pagamento_Encoded']]
y_sentimento = encoder.fit_transform(dataset['Avaliacao'])
y_valor = dataset['Valor_Scaled']

# Classificação (Previsão de Sentimento)
X_train, X_test, y_train, y_test = train_test_split(X, y_sentimento, test_size=0.2, random_state=42)
model_sentimento = RandomForestClassifier(random_state=42)
model_sentimento.fit(X_train, y_train)
y_pred = model_sentimento.predict(X_test)
print("Relatório de Classificação (Sentimento):\n", classification_report(y_test, y_pred))

# Regressão (Previsão de Valor)
X_train, X_test, y_train, y_test = train_test_split(X, y_valor, test_size=0.2, random_state=42)
model_valor = RandomForestRegressor(random_state=42)
model_valor.fit(X_train, y_train)
y_pred = model_valor.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Erro Quadrático Médio (Valor): {mse}")

# Clusterização (Segmentação de Clientes)
kmeans = KMeans(n_clusters=3, random_state=42)
dataset['Cluster'] = kmeans.fit_predict(X)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=dataset, x='Idade', y='Valor_Scaled', hue='Cluster', palette='viridis')
plt.title("Segmentação de Clientes por Idade e Valor de Compra")
plt.xlabel("Idade")
plt.ylabel("Valor (Normalizado)")
plt.show()

# Insights Detalhados
# Produtos mais vendidos
print("Top 5 produtos mais vendidos:\n", dataset['Produto'].value_counts().head())

# Análise de avaliações
print("Distribuição de avaliações:\n", dataset['Avaliacao'].value_counts())

# Métodos de pagamento mais utilizados
print("Métodos de pagamento mais utilizados:\n", dataset['Pagamento'].value_counts())

# Segmentação de clientes
print("Distribuição de clientes por cluster:\n", dataset['Cluster'].value_counts())

# Potenciais Insights:
# - Produtos mais populares: Oferecer promoções nos produtos mais vendidos.
# - Avaliações negativas: Melhorar os produtos que recebem "Ruim" ou "Péssimo".
# - Gêneros e idades predominantes: Criar produtos ou promoções direcionadas para o público principal.
# - Métodos de pagamento mais usados: Investir em infraestrutura para os métodos preferidos pelos clientes.
# - Segmentos: Personalizar ofertas para cada cluster identificado nos dados.
