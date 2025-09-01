# # import torch.nn as nn
# class CNNLSTMClassifier(nn.Module):
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
