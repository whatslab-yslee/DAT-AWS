"""
시계열 데이터 다룬 딥러닝 모델 결과 처리 관련 클래스 및 메서드
"""

# import os

# import numpy as np
# import pandas as pd
# from sklearn.preprocessing import StandardScaler
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torch.utils.data import DataLoader


# class TBCNNLSTM(nn.Module):
#     def __init__(self, input_size, hidden_size=64):
#         super().__init__()

#         self.position_conv = nn.Sequential(
#             nn.Conv1d(6, 32, kernel_size=3, padding=1),  # Position_X,Y,Z + Scaled_Position_X,Y,Z
#             nn.BatchNorm1d(32),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         self.rotation_conv = nn.Sequential(
#             nn.Conv1d(3, 16, kernel_size=3, padding=1),  # Rotation_X,Y,Z
#             nn.BatchNorm1d(16),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         self.other_conv = nn.Sequential(
#             nn.Conv1d(2, 16, kernel_size=3, padding=1),  # Gap, Score
#             nn.BatchNorm1d(16),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         total_cnn_output = 64  # 32 + 16 + 16

#         self.lstm = nn.LSTM(input_size=total_cnn_output, hidden_size=hidden_size, num_layers=2, batch_first=True, dropout=0.3, bidirectional=True)

#         self.attention = nn.Sequential(nn.Linear(hidden_size * 2, hidden_size), nn.Tanh(), nn.Linear(hidden_size, 1))

#         self.classifier = nn.Sequential(
#             nn.Linear(hidden_size * 2, hidden_size),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(hidden_size, hidden_size // 2),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(hidden_size // 2, 1),
#             nn.Sigmoid(),
#         )

#     def forward(self, x):
#         # 입력 데이터 분리
#         positions = x[:, :, [1, 2, 3, 7, 8, 9]]  # Position_X,Y,Z + Scaled_Position_X,Y,Z
#         rotations = x[:, :, [4, 5, 6]]  # Rotation_X,Y,Z
#         others = x[:, :, [0, 10]]  # Gap, Score

#         # CNN 처리
#         positions = positions.transpose(1, 2)
#         rotations = rotations.transpose(1, 2)
#         others = others.transpose(1, 2)

#         pos_features = self.position_conv(positions)
#         rot_features = self.rotation_conv(rotations)
#         other_features = self.other_conv(others)

#         combined = torch.cat([pos_features, rot_features, other_features], dim=1)
#         combined = combined.transpose(1, 2)  # (batch, seq_len, features)

#         lstm_out, _ = self.lstm(combined)

#         attention_weights = F.softmax(self.attention(lstm_out), dim=1)
#         context = torch.sum(attention_weights * lstm_out, dim=1)

#         output = self.classifier(context)
#         return output.squeeze()


# class EnhancedCNNLSTM(nn.Module):
#     def __init__(self, input_size, hidden_size=64):
#         super().__init__()

#         # 위치와 회전 데이터를 위한 별도의 CNN 레이어
#         self.position_conv = nn.Sequential(
#             nn.Conv1d(6, 32, kernel_size=3, padding=1),  # Position_X,Y,Z + Scaled_Position_X,Y,Z
#             nn.BatchNorm1d(32),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         self.rotation_conv = nn.Sequential(
#             nn.Conv1d(3, 16, kernel_size=3, padding=1),  # Rotation_X,Y,Z
#             nn.BatchNorm1d(16),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         # 나머지 특성을 위한 CNN 레이어
#         self.other_conv = nn.Sequential(
#             nn.Conv1d(2, 16, kernel_size=3, padding=1),  # Gap, Score
#             nn.BatchNorm1d(16),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#         )

#         # 모든 CNN 출력을 합친 후의 차원
#         total_cnn_output = 64  # 32 + 16 + 16

#         # LSTM 레이어
#         self.lstm = nn.LSTM(input_size=total_cnn_output, hidden_size=hidden_size, num_layers=2, batch_first=True, dropout=0.3, bidirectional=True)

#         # Attention 메커니즘
#         self.attention = nn.Sequential(nn.Linear(hidden_size * 2, hidden_size), nn.Tanh(), nn.Linear(hidden_size, 1))

#         # 최종 분류기
#         self.classifier = nn.Sequential(
#             nn.Linear(hidden_size * 2, hidden_size),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(hidden_size, hidden_size // 2),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(hidden_size // 2, 1),
#             nn.Sigmoid(),
#         )

#     def forward(self, x):
#         # 입력 데이터 분리
#         positions = x[:, :, [1, 2, 3, 7, 8, 9]]  # Position_X,Y,Z + Scaled_Position_X,Y,Z
#         rotations = x[:, :, [4, 5, 6]]  # Rotation_X,Y,Z
#         others = x[:, :, [0, 10]]  # Gap, Score

#         # CNN 처리
#         positions = positions.transpose(1, 2)
#         rotations = rotations.transpose(1, 2)
#         others = others.transpose(1, 2)

#         pos_features = self.position_conv(positions)
#         rot_features = self.rotation_conv(rotations)
#         other_features = self.other_conv(others)

#         # 모든 특성 합치기
#         combined = torch.cat([pos_features, rot_features, other_features], dim=1)
#         combined = combined.transpose(1, 2)  # (batch, seq_len, features)

#         # LSTM 처리
#         lstm_out, _ = self.lstm(combined)

#         # Attention 메커니즘
#         attention_weights = F.softmax(self.attention(lstm_out), dim=1)
#         context = torch.sum(attention_weights * lstm_out, dim=1)

#         # 분류
#         output = self.classifier(context)
#         return output


# class CNNLSTMModel(nn.Module):
#     def __init__(self, input_size, hidden_size=32):  # hidden size 감소
#         super().__init__()
#         self.conv1 = nn.Conv1d(input_size, 32, kernel_size=3, padding=1)
#         self.bn1 = nn.BatchNorm1d(32)
#         self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
#         self.dropout1 = nn.Dropout(0.5)

#         self.lstm = nn.LSTM(32, hidden_size, batch_first=True)
#         self.bn2 = nn.BatchNorm1d(hidden_size)
#         self.dropout2 = nn.Dropout(0.5)

#         self.linear = nn.Linear(hidden_size, 1)
#         self.sigmoid = nn.Sigmoid()

#     def forward(self, x):
#         x = x.transpose(1, 2)
#         x = self.conv1(x)
#         x = self.bn1(x)
#         x = F.relu(x)
#         x = self.pool(x)
#         x = self.dropout1(x)

#         x = x.transpose(1, 2)
#         lstm_out, _ = self.lstm(x)
#         lstm_out = self.bn2(lstm_out[:, -1, :])
#         lstm_out = self.dropout2(lstm_out)

#         output = self.linear(lstm_out)
#         return self.sigmoid(output)


# class VRPredictor:
#     def __init__(self, model_path, content_name, content_level):
#         self.device = torch.device("cpu")
#         self.content_name = content_name
#         self.content_level = content_level
#         self.model_path = model_path
#         self.sequence_length = 10

#         # 컨텐츠별 특성 컬럼 정의
#         self.feature_columns = self._get_feature_columns()
#         self.model = self._load_appropriate_model()
#         self.scaler = StandardScaler()

#     def _get_feature_columns(self):
#         """컨텐츠별 특성 컬럼 반환"""
#         if self.content_name != "TennisBall":
#             return ["Rotation_X", "Rotation_Y", "Rotation_Z", "Score", "time (second)", "spend_time_seconds"]
#         else:  # BalanceBall, FitBox
#             return [
#                 "Gap",
#                 "Position_X",
#                 "Position_Y",
#                 "Position_Z",
#                 "Rotation_X",
#                 "Rotation_Y",
#                 "Rotation_Z",
#                 "Scaled_Position_X",
#                 "Scaled_Position_Y",
#                 "Scaled_Position_Z",
#                 "Score",
#             ]

#     def _load_appropriate_model(self):
#         """컨텐츠에 맞는 모델 로드"""
#         try:
#             if self.content_name != "TennisBall":
#                 model = CNNLSTMModel(input_size=len(self.feature_columns))
#             else:
#                 model = EnhancedCNNLSTM(input_size=len(self.feature_columns))

#             model_file = os.path.join(self.model_path, f"{self.content_name}{self.content_level}", "model.pth")

#             # CPU에서 모델 로드
#             state_dict = torch.load(model_file, map_location=self.device)
#             model.load_state_dict(state_dict)
#             model.eval()

#             return model

#         except Exception as e:
#             print(f"Error loading model for {self.content_name}: {str(e)}")
#             return None

#     def prepare_data(self, df):
#         """데이터 전처리"""
#         df_processed = df.copy()

#         # 공통 전처리
#         df_processed["event"] = df_processed["event"].fillna("no_event")
#         df_processed["spend_time_seconds"] = pd.to_numeric(df_processed["spend_time"], errors="coerce").fillna(0) / 1000.0

#         # 컨텐츠별 전처리
#         if self.content_name == "TennisBall":
#             # TennisBall 특화 전처리
#             df_processed = df_processed.drop(["current_time", "spend_time"], axis=1)
#             df_processed = pd.get_dummies(df_processed, columns=["event", "State"])

#             # 추가 특성 생성
#             rotation_cols = ["Rotation_X", "Rotation_Y", "Rotation_Z"]
#             df_processed["rotation_std"] = df_processed[rotation_cols].std(axis=1)
#             df_processed["rotation_range"] = df_processed[rotation_cols].max(axis=1) - df_processed[rotation_cols].min(axis=1)

#             # 이동 평균 및 표준편차 계산
#             window = 5
#             for col in rotation_cols:
#                 df_processed[f"{col}_ma"] = df_processed[col].rolling(window=window).mean()
#                 df_processed[f"{col}_std"] = df_processed[col].rolling(window=window).std()

#         else:
#             # BalanceBall, FitBox 전처리
#             df_processed = df_processed.drop(["current_time", "spend_time", "State"], axis=1)

#         # NaN 처리
#         df_processed = df_processed.fillna(method="ffill").fillna(method="bfill")

#         return df_processed

#     def prepare_sequence(self, df):
#         """시퀀스 데이터 준비"""
#         sequences = []

#         for i in range(len(df) - self.sequence_length + 1):
#             seq = df[self.feature_columns].iloc[i : i + self.sequence_length].values
#             sequences.append(seq)

#         return np.array(sequences)

#     def predict(self, df, batch_size=32):
#         """예측 수행"""
#         try:
#             if self.model is None:
#                 raise ValueError(f"Model for {self.content_name} is not properly loaded")

#             # 데이터 전처리
#             df_processed = self.prepare_data(df)
#             sequences = self.prepare_sequence(df_processed)

#             # 텐서 변환
#             sequences_tensor = torch.FloatTensor(sequences)
#             dataset = torch.utils.data.TensorDataset(sequences_tensor)
#             dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

#             # 예측 수행
#             all_probabilities = []

#             with torch.no_grad():
#                 for batch in dataloader:
#                     batch_sequences = batch[0]
#                     outputs = self.model(batch_sequences)
#                     all_probabilities.extend(outputs.cpu().numpy())

#             # 결과 계산
#             mean_probability = np.mean(all_probabilities)
#             final_prediction = 1 if mean_probability > 0.5 else 0

#             result = {
#                 "final_prediction": final_prediction,
#                 "mean_probability": float(mean_probability),
#                 "prediction_details": {
#                     "total_sequences": len(all_probabilities),
#                     "positive_ratio": np.mean([1 if p > 0.5 else 0 for p in all_probabilities]),
#                     "std_probability": float(np.std(all_probabilities)),
#                 },
#             }

#             return result

#         except Exception as e:
#             print(f"Prediction error for {self.content_name}: {str(e)}")
#             return {
#                 "final_prediction": 0,
#                 "mean_probability": 0.0,
#                 "prediction_details": {"total_sequences": 0, "positive_ratio": 0.0, "std_probability": 0.0},
#             }


# def load_cnn_lstm_model(model_class, load_path, model_name="cnn_lstm_model", input_size=6):
#     # 항상 CPU를 사용하도록 강제
#     # device = torch.device('cpu')

#     try:
#         state_dict_path = os.path.join(load_path, model_name)

#         # 모델 초기화
#         state_dict_model = model_class(input_size=input_size)

#         # 에러 처리를 위한 예외 처리 추가
#         try:
#             # CPU에서만 로드하도록 수정
#             state_dict = torch.load(state_dict_path, map_location="cpu")
#             state_dict_model.load_state_dict(state_dict)
#         except Exception as e:
#             print(f"Model state dict loading error: {e}")
#             return None, None

#         try:
#             # CPU에서만 로드하도록 수정
#             full_model = torch.load(state_dict_path, map_location="cpu")
#         except Exception as e:
#             print(f"Full model loading error: {e}")
#             return state_dict_model, None

#         # 모델을 평가 모드로 설정
#         state_dict_model.eval()

#         return state_dict_model, full_model

#     except Exception as e:
#         print(f"General model loading error: {e}")
#         return None, None


# def CNN_LSTM_Result(contents_name, contents_level, df):
#     """예측 결과 문자열 반환"""
#     try:
#         model_path = "src/lib/models/"
#         predictor = VRPredictor(model_path=model_path, content_name=contents_name, content_level=contents_level)

#         result = predictor.predict(df)

#         result_text = f"""{"비정상" if result["final_prediction"] == 1 else "정상"}
#         신뢰도: {result["mean_probability"]:.2%}
#         (전체 시퀀스 수: {result["prediction_details"]["total_sequences"]},
#          비정상 비율: {result["prediction_details"]["positive_ratio"]:.2%})"""

#         return result_text

#     except Exception as e:
#         print(f"Error in CNN_LSTM_Result: {str(e)}")
#         return "예측 오류 발생"
