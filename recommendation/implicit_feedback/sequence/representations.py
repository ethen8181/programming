import torch.nn as nn
import torch.nn.functional as F
from spotlight.layers import ScaledEmbedding, ZeroEmbedding


PADDING_IDX = 0


class LSTMNet(nn.Module):

    def __init__(self, num_items, embedding_dim=32, item_embedding_layer=None):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.item_biases = ZeroEmbedding(num_items, 1, padding_idx=PADDING_IDX)
        if item_embedding_layer is not None:
            self.item_embedding = item_embedding_layer
        else:
            self.item_embedding = ScaledEmbedding(
                num_items, embedding_dim, padding_idx=PADDING_IDX)

        # why input_size and hidden_size needs to be both embedding_dim ??
        self.lstm = nn.LSTM(
            input_size=embedding_dim, hidden_size=embedding_dim, batch_first=True)

    def user_representation(self, item_sequences):
        # after padding it will become
        # size of [batch_size, max_sequence_length + 1, embedding_dim]
        sequence_embeddings = self.item_embedding(item_sequences)
        sequence_embeddings = F.pad(sequence_embeddings, (0, 0, 1, 0))

        # convert the output of lstm layer to place max_sequence_length as last channel, i.e.
        # size of [batch_size, hidden_size, max_sequence_length + 1]
        user_representations, _ = self.lstm(sequence_embeddings).permute(0, 2, 1)
        return user_representations[:, :, :-1], user_representations[:, :, -1]

    def forward(self, user_representation, targets):
        pass