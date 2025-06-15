import torch.nn as nn


# RNN分类器模型
class RNNClassifier(nn.Module):
    def __init__(self, vocab_size, embedding_dim=100, hidden_dim=256, num_layers=2, dropout=0.5):
        super(RNNClassifier, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
        # RNN层（可以替换为LSTM或GRU以获得更好性能）
        self.rnn = nn.GRU(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # 输出层
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 10),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(10, 1)
        )
        
    def forward(self, text, lengths):
        # text: [batch_size, seq_len]
        # lengths: [batch_size]
        
        # 嵌入
        embedded = self.embedding(text)  # [batch_size, seq_len, embedding_dim]
        
        # 打包序列以处理变长输入
        packed_embedded = nn.utils.rnn.pack_padded_sequence(
            embedded, lengths, batch_first=True
        )
        packed_output, hidden = self.rnn(packed_embedded)
        
        # hidden: [num_layers, batch_size, hidden_dim]
        # 我们只需要最后一层的隐藏状态
        last_hidden = hidden[-1]  # [batch_size, hidden_dim]
        logits = self.fc(last_hidden).squeeze(1)  # [batch_size]
        
        return logits