import torch
import torch.nn as nn

class GRUTransformer(nn.Module):
    def __init__(self, input_dim, hidden_dim, gru_layers, nhead, ff_dim, transformer_layers, output_dim):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=gru_layers, batch_first=True)
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=nhead, dim_feedforward=ff_dim, dropout=0.1, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=transformer_layers)
        self.fc = nn.Linear(hidden_dim, output_dim)
    def forward(self, x):
        gru_out, _ = self.gru(x)
        trans_out = self.transformer(gru_out)
        out = self.fc(trans_out[:, -1, :])
        return out

def example_usage():
    batch_size = 8
    seq_len = 10
    input_dim = 16
    hidden_dim = 32
    gru_layers = 2
    nhead = 4
    ff_dim = 64
    transformer_layers = 2
    output_dim = 5
    model = GRUTransformer(input_dim, hidden_dim, gru_layers, nhead, ff_dim, transformer_layers, output_dim)
    x = torch.randn(batch_size, seq_len, input_dim)
    y = model(x)
    return y
