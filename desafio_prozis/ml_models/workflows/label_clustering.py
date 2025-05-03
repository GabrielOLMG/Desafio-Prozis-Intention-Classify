from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from desafio_prozis.ml_models.workflows.general_functions import load_pickle_file
from desafio_prozis.ml_models.workflows.general_functions import save_pickle_file


def train_clustering_model(
    model_name: str,
    labels: list,
    texts: list,
    model_path: Path,
) -> dict:
    model_llm = SentenceTransformer(model_name)

    # Carrega os embeddings
    x_embed = model_llm.encode(texts)

    # Normaliza embeddings
    scaler_model = StandardScaler()
    x_scaled = scaler_model.fit_transform(x_embed)

    # Encode dos labels em números
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels)

    # Aplicação de LDA para aumentar a separação entre os clusters
    new_dimension = len(set(labels)) - 1
    lda_model = LinearDiscriminantAnalysis(n_components=new_dimension)
    x_lda = lda_model.fit_transform(x_scaled, labels_encoded)

    # Aplicando KNN
    knn = KNeighborsClassifier(n_neighbors=3, weights="distance")
    knn.fit(x_lda, labels_encoded)

    # Salvando Modelos e Dados
    model_data = {
        "model_llm": model_llm,
        "scaler_model": scaler_model,
        "lda_model": lda_model,
        "model_knn": knn,
        "label_encoder": label_encoder,
        "labels_encoded": labels_encoded,
    }

    save_pickle_file(model_path, model_data)

    return model_data


def get_or_train_model(
    texts: list,
    labels: list,
    model_name: str,
    model_path: Path,
    *,
    train_again: bool,
) -> tuple[dict, bool]:
    created = False

    if not train_again and model_path.exists():
        model_data = load_pickle_file(model_path)
    else:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        model_data = train_clustering_model(
            model_name,
            labels,
            texts,
            model_path,
        )
        created = True

    return model_data, created


def get_cluster_labels(text: str, model_data: dict, *, n_best: int) -> list:
    model_llm = model_data["model_llm"]
    scaler_model = model_data["scaler_model"]
    lda_model = model_data["lda_model"]
    model_knn = model_data["model_knn"]
    label_encoder = model_data["label_encoder"]
    labels_encoded = model_data["labels_encoded"]

    # Aplica mesmo embeddings a frase desejada
    text_embeddings = model_llm.encode([text])

    # Aplica mesma normalização ao embedding
    text_embeddings_scaled = scaler_model.transform(text_embeddings)

    # Aplica mesma projeção LDA
    text_embeddings_lda = lda_model.transform(text_embeddings_scaled)

    # Calcula vizinhos, com uma maior distancia que original (3 para 20)
    distances, index = model_knn.kneighbors(text_embeddings_lda, n_neighbors=20)

    neighbors = labels_encoded[index[0]]

    # calcula Score com base na distancia(+1e-5 para evitar divisões por 0)
    scores = {}
    for i, label in enumerate(neighbors):
        score = 1 / (distances[0][i] + 1e-5)
        scores[label] = scores.get(label, 0) + score

    # Ordena pelo Score(maior para o menor)
    top_labels = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Pega valores originais
    top_labels = [
        (label_encoder.inverse_transform([label])[0], round(score, 3))
        for label, score in top_labels
    ]

    return top_labels[:n_best]
