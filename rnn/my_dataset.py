import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import jieba


# 自定义文本数据集类
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, vocab=None, max_len=512):
        """
        初始化文本数据集
        
        参数:
            texts: 文本列表
            labels: 标签列表
            tokenizer: 分词函数
            vocab: 词汇表字典，默认为None（会自动构建）
            max_len: 文本最大长度，用于填充或截断
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        
        # 如果没有提供词汇表，则构建一个
        if vocab is None:
            self.build_vocab()
        else:
            self.vocab = vocab
        
        # 将文本转换为索引
        self.text_indices = [self.text_to_indices(text) for text in texts]
    
    def build_vocab(self, min_freq=2):
        """构建词汇表"""
        word_freq = {}
        for text in self.texts:
            tokens = self.tokenizer(text)
            for token in tokens:
                word_freq[token] = word_freq.get(token, 0) + 1
        
        # 过滤低频词并构建词汇表
        vocab = {'<PAD>': 0, '<UNK>': 1}  # 填充标记和未知标记
        for word, freq in word_freq.items():
            if freq >= min_freq:
                vocab[word] = len(vocab)
        
        self.vocab = vocab
        self.vocab_size = len(vocab)
    
    def text_to_indices(self, text):
        """将文本转换为索引序列"""
        tokens = self.tokenizer(text)
        # 截断或填充到固定长度
        if len(tokens) > self.max_len:
            tokens = tokens[:self.max_len]
        else:
            tokens = tokens + ['<PAD>'] * (self.max_len - len(tokens))
        
        # 转换为索引
        indices = [self.vocab.get(token, self.vocab['<UNK>']) for token in tokens]
        return indices
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        # 返回文本索引、标签和实际长度
        text_indices = self.text_indices[idx]
        label = self.labels[idx]
        length = min(len(self.tokenizer(self.texts[idx])), self.max_len)
        
        return {
            'text': torch.tensor(text_indices),
            'label': torch.tensor(label, dtype=torch.float),
            'length': torch.tensor(length)
        }

# 中文分词函数
def chinese_tokenizer(text):
    return [token for token in jieba.cut(text)]


if __name__ == "__main__":
    texts = [

    ]
    labels = []
    tokenizer = chinese_tokenizer()

    dataset = TextDataset(texts, labels, tokenizer)