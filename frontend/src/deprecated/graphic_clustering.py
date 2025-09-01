"""
클러스터링 모델 결과처리 관련 메서드 3개
"""

# import os
# import pickle

# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd


# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"


# def extract_corr(df):
#     # 비숫자형 열을 제거 (숫자형 데이터만 선택)
#     df_numeric = df.select_dtypes(include=["number"])

#     # 상관관계 계산 전 NaN 값 제거
#     df_numeric = df_numeric.dropna()

#     x = []
#     columns = []

#     for i in range(len(df_numeric.columns)):
#         for j in range(i + 1, len(df_numeric.columns)):  # i < j만 허용
#             if i != j:
#                 columns.append(df_numeric.columns[i] + " * " + df_numeric.columns[j])  # 피처 이름 결합

#     corr_matrix = df_numeric.corr()  # 상관관계 계산

#     result_df = pd.DataFrame(columns=columns)

#     for i in range(len(df_numeric.columns)):
#         for j in range(i + 1, len(df_numeric.columns)):  # i < j만 허용하여 중복 제거
#             if i != j:
#                 x.append(corr_matrix.iloc[i, j])  # 상관관계 값 추가

#     result_df.loc[len(result_df)] = x

#     return result_df


# def clustering_result(contents_name, contents_level, data):
#     model_name = contents_name + "_" + contents_level
#     with open("src/lib/models/" + model_name + ".pkl", "rb") as f:
#         model = pickle.load(f)

#     # 입력 데이터가 DataFrame이면 numpy 배열로 변환
#     if isinstance(data, pd.DataFrame):
#         data = data.to_numpy()

#     # numpy 배열로 변환된 데이터의 차원 확인
#     data = np.array(data)

#     # 입력 데이터의 특성 수가 모델의 훈련된 특성 수와 일치하는지 확인
#     if data.shape[1] == model.n_features_in_:
#         # 특성 수가 일치할 경우 예측
#         return model.predict(data)
#     else:
#         # 특성 수가 맞지 않을 경우 에러 발생
#         raise ValueError(f"데이터의 특성 수가 일치하지 않습니다. 예상된 특성 수: {model.n_features_in_}, 입력된 특성 수: {data.shape[1]}")

#     # return "models/"+model_name+".pkl"


# def draw_heatmap(df, contents_name, contents_level, cluster):
#     # 상관관계 추출
#     corr = extract_corr(df)

#     # KMeans 모델 로드
#     model_name = contents_name + "_" + contents_level
#     with open("src/lib/models/" + model_name + ".pkl", "rb") as f:
#         kmeans = pickle.load(f)

#     # 클러스터 레이블 및 중심값
#     # cluster_labels = kmeans.labels_
#     centroids = kmeans.cluster_centers_

#     # 서브플롯 생성
#     fig, ax = plt.subplots(figsize=(20, 15), nrows=1, ncols=2)

#     # 1. 클러스터 중심값 히트맵 (변경 없음)
#     ax[0].set_title("Cluster Classification Criteria")
#     cax1 = ax[0].matshow(centroids.T, cmap="coolwarm")
#     fig.colorbar(cax1, ax=ax[0])
#     ax[0].set_xticks(np.arange(centroids.shape[0]))
#     ax[0].set_xticklabels([f"Cluster {i}" for i in range(centroids.shape[0])], rotation=90)
#     ax[0].set_yticks(np.arange(corr.shape[1]))
#     ax[0].set_yticklabels(corr.columns, rotation=0)

#     for (i, j), val in np.ndenumerate(centroids.T):
#         ax[0].text(j, i, f"{val:.2f}", ha="center", va="center", color="black")

#     ytick_labels = ax[0].set_yticklabels(corr.columns, rotation=0)

#     # 클러스터 간 차이에 따른 하이라이팅
#     for i, label in enumerate(ytick_labels):
#         diff = abs(centroids[0][i] - centroids[1][i])
#         if diff >= 0.2:
#             label.set_color("red")  # 또는 다른 색상 코드 사용 가능, 예: '#FFFF00'
#             label.set_fontweight("bold")  # 선택적으로 볼드체 추가

#     ax[1].set_title("Correlation Heatmap")
#     corr_transposed = corr.T  # 데이터 전치
#     cax2 = ax[1].matshow(corr_transposed, cmap="coolwarm")
#     fig.colorbar(cax2, ax=ax[1])

#     # x축 설정
#     ax[1].set_xticks(np.arange(corr_transposed.shape[1]))
#     ax[1].set_xticklabels(cluster, rotation=90)

#     # y축 설정
#     ax[1].set_yticks(np.arange(corr_transposed.shape[0]))
#     ax[1].set_yticklabels(corr_transposed.index, rotation=0)

#     # 상관관계 텍스트 추가
#     for i in range(corr_transposed.shape[0]):
#         for j in range(corr_transposed.shape[1]):
#             ax[1].text(j, i, f"{corr_transposed.iloc[i, j]:.2f}", ha="center", va="center", color="black")

#     plt.tight_layout()
#     return fig
