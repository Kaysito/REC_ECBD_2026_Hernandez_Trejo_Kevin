"""Analisis no supervisado reproducible: escalamiento, PCA y K-means."""

import json
import os

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, silhouette_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

DATA_PATH = os.path.join("data", "processed", "dry_beans_cleaned.csv")
OUTPUTS_DIR = "outputs"
MODELS_DIR = "modelos"
RANDOM_STATE = 42


def ejecutar_modelado_no_supervisado():
    print("=" * 72)
    print("ANALISIS NO SUPERVISADO: STANDARD SCALER + PCA + K-MEANS")
    print("=" * 72)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    variables = [c for c in df.select_dtypes(include="number").columns]
    X = df[variables]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca_completo = PCA().fit(X_scaled)
    var_acum = pca_completo.explained_variance_ratio_.cumsum()
    n_componentes_90 = int((var_acum < 0.90).sum() + 1)
    pca_modelo = PCA(n_components=n_componentes_90, random_state=RANDOM_STATE)
    X_pca = pca_modelo.fit_transform(X_scaled)

    resultados_k = []
    for k in range(2, 11):
        modelo = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE)
        etiquetas = modelo.fit_predict(X_pca)
        silueta = silhouette_score(X_pca, etiquetas, sample_size=5000, random_state=RANDOM_STATE)
        resultados_k.append({"k": k, "inercia": float(modelo.inertia_), "silhouette": float(silueta)})
        print(f"k={k:2d} | Inercia={modelo.inertia_:12.2f} | Silhouette={silueta:.4f}")

    mejor_k = max(resultados_k, key=lambda r: r["silhouette"])["k"]
    kmeans = KMeans(n_clusters=mejor_k, n_init=20, random_state=RANDOM_STATE)
    clusters = kmeans.fit_predict(X_pca)

    # Class no se usa para formar grupos; solo permite una comparacion posterior.
    clases_codificadas = LabelEncoder().fit_transform(df["Class"])
    ari = adjusted_rand_score(clases_codificadas, clusters)
    nmi = normalized_mutual_info_score(clases_codificadas, clusters)

    df_salida = df.copy()
    df_salida["Cluster"] = clusters
    df_salida["PC1"] = X_pca[:, 0]
    df_salida["PC2"] = X_pca[:, 1]
    df_salida.to_csv(os.path.join("data", "processed", "dry_beans_clustered.csv"), index=False)

    tabla_cruzada = pd.crosstab(df_salida["Cluster"], df_salida["Class"])
    tabla_cruzada.to_csv(os.path.join(OUTPUTS_DIR, "clusters_vs_clases.csv"))

    sns.set_theme(style="whitegrid")
    ks = [r["k"] for r in resultados_k]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(ks, [r["inercia"] for r in resultados_k], marker="o", color="#174a73")
    axes[0].set(title="Metodo del codo", xlabel="Numero de clusters (k)", ylabel="Inercia")
    axes[1].plot(ks, [r["silhouette"] for r in resultados_k], marker="o", color="#009688")
    axes[1].axvline(mejor_k, color="#c0392b", linestyle="--", label=f"Mejor k={mejor_k}")
    axes[1].set(title="Coeficiente de silueta", xlabel="Numero de clusters (k)", ylabel="Silhouette")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "seleccion_k_clusters.png"), dpi=180, bbox_inches="tight")
    plt.close(fig)

    muestra = df_salida.sample(min(5000, len(df_salida)), random_state=RANDOM_STATE)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.scatterplot(data=muestra, x="PC1", y="PC2", hue="Cluster", palette="tab10", s=22, alpha=0.65, ax=ax)
    ax.set_title(f"Clusters K-means proyectados en PCA (k={mejor_k})")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "clusters_pca.png"), dpi=180, bbox_inches="tight")
    plt.close(fig)

    resumen = {
        "registros": int(len(df)),
        "variables_numericas": variables,
        "componentes_pca_para_90_por_ciento": n_componentes_90,
        "varianza_explicada_acumulada": float(pca_modelo.explained_variance_ratio_.sum()),
        "evaluacion_k": resultados_k,
        "mejor_k_segun_silhouette": int(mejor_k),
        "silhouette_mejor_k": float(max(r["silhouette"] for r in resultados_k)),
        "comparacion_externa_solo_interpretativa": {"ARI": float(ari), "NMI": float(nmi)},
        "nota": "Class no se utilizo para entrenar K-means; solo para interpretar los grupos obtenidos."
    }
    with open(os.path.join(OUTPUTS_DIR, "evaluacion_modelos_no_supervisados.json"), "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=4, ensure_ascii=False)

    joblib.dump(scaler, os.path.join(MODELS_DIR, "standard_scaler_clustering.joblib"), compress=3)
    joblib.dump(pca_modelo, os.path.join(MODELS_DIR, "pca.joblib"), compress=3)
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans.joblib"), compress=3)

    print(f"\nMejor k segun silhouette: {mejor_k}")
    print(f"Componentes PCA para >=90% de varianza: {n_componentes_90}")
    print(f"ARI={ari:.4f} | NMI={nmi:.4f}")
    print("ANALISIS NO SUPERVISADO FINALIZADO")
    return resumen


if __name__ == "__main__":
    ejecutar_modelado_no_supervisado()
