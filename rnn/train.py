import torch.nn as nn
import torch
from sklearn.model_selection import train_test_split
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import time
import pandas as pd
import random
from tqdm import tqdm


from my_dataset import TextDataset, chinese_tokenizer
from model import RNNClassifier

# 加载和处理数据
def load_and_process_data(file_path, test_size=0.2, valid_size=0.1, random_state=42, print_details=False):
    """加载并处理情感分析数据集，过滤无效数据"""
    # 检查文件格式
    if not file_path.endswith('.csv'):
        raise ValueError("不支持的文件格式，请使用CSV")
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 定义关键列名
    TEXT_COLUMN = 'sentence'  # 文本列名
    LABEL_COLUMN = 'label'    # 标签列名
    
    # 检查必要列是否存在
    for col in [TEXT_COLUMN, LABEL_COLUMN]:
        if col not in df.columns:
            raise ValueError(f"数据集缺少必要列 '{col}'")
    
    # 记录原始数据大小
    original_size = len(df)
    
    # 数据清洗流程
    print(f"开始数据清洗，原始样本数: {original_size}")
    
    # 1. 过滤含有NaN的行（同时处理文本和标签）
    df = df.dropna(subset=[TEXT_COLUMN, LABEL_COLUMN])
    nan_dropped = original_size - len(df)
    if nan_dropped > 0:
        print(f"✂️ 过滤含有NaN的行: {nan_dropped}条")
    
    # 2. 处理文本列
    df[TEXT_COLUMN] = (
        df[TEXT_COLUMN]
        .astype(str)     # 确保是字符串类型
        .str.strip()     # 去除前后空格
    )
    
    # 3. 过滤空文本
    empty_text_mask = df[TEXT_COLUMN] == ''
    empty_text_count = empty_text_mask.sum()
    if empty_text_count > 0:
        df = df[~empty_text_mask]
        print(f"✂️ 过滤空文本: {empty_text_count}条")
    
    # 4. 过滤过短文本（可选，默认保留）
    MIN_TEXT_LENGTH = 3  # 可调整的最小文本长度
    short_text_mask = df[TEXT_COLUMN].str.len() < MIN_TEXT_LENGTH
    short_text_count = short_text_mask.sum()
    if short_text_count > 0 and print_details:
        print(f"⚠️ 发现 {short_text_count} 条短文本（<{MIN_TEXT_LENGTH}字符）")
    
    # 5. 处理标签列
    df[LABEL_COLUMN] = (
        df[LABEL_COLUMN]
        .astype(str)     # 先转为字符串以处理各种格式
        .str.strip()     # 去除前后空格
    )
    
    # 6. 转换标签为数值型（0/1）
    df[LABEL_COLUMN] = pd.to_numeric(df[LABEL_COLUMN], errors='coerce')
    df = df.dropna(subset=[LABEL_COLUMN])  # 删除无法转换为数值的标签
    df[LABEL_COLUMN] = df[LABEL_COLUMN].astype(int)
    
    # 7. 只保留二分类标签（0/1）
    df = df[df[LABEL_COLUMN].isin([0, 1])]
    
    # 8. 最终数据统计
    final_size = len(df)
    print(f"✅ 数据清洗完成，有效样本数: {final_size} ({final_size/original_size*100:.2f}%)")
    
    # 打印详细信息（如果需要）
    if print_details:
        print("\n" + "="*50)
        print("数据基本信息:")
        print("="*50)
        print(f"类别分布:")
        print(df[LABEL_COLUMN].value_counts())
        print(f"\n正负样本比例:")
        print(df[LABEL_COLUMN].value_counts(normalize=True))
        print("\n第一个样本示例:")
        print(df.iloc[0])
        print("="*50)
    
    # 分割数据集
    texts = df[TEXT_COLUMN].values
    labels = df[LABEL_COLUMN].values
    
    # 先分割出测试集
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=test_size, random_state=random_state
    )
    
    # 从剩余数据中分割出验证集
    if valid_size > 0:
        train_texts, valid_texts, train_labels, valid_labels = train_test_split(
            train_texts, train_labels, test_size=valid_size/(1-test_size), random_state=random_state
        )
    else:
        valid_texts, valid_labels = np.array([]), np.array([])
    
    return train_texts, train_labels, valid_texts, valid_labels, test_texts, test_labels

# 创建数据加载器
def create_data_loaders(train_dataset, valid_dataset, test_dataset, batch_size=128):
    """创建数据加载器"""
    # 训练集需要打乱顺序
    train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True,collate_fn=collate_fn)
    # 验证集和测试集不需要打乱
    valid_loader = DataLoader(valid_dataset,batch_size=batch_size,shuffle=False,collate_fn=collate_fn)
    test_loader = DataLoader(test_dataset,batch_size=batch_size,shuffle=False,collate_fn=collate_fn)
    
    return train_loader, valid_loader, test_loader

# 自定义批处理函数（用于处理变长序列）
def collate_fn(batch):
    """
    自定义批处理函数，按序列长度排序，便于使用pack_padded_sequence
    
    参数:
        batch: 一批数据
        
    返回:
        排序后的文本、标签和长度
    """
    # 按长度降序排序
    batch.sort(key=lambda x: x['length'], reverse=True)
    
    # 提取文本、标签和长度
    texts = [item['text'] for item in batch]
    labels = [item['label'] for item in batch]
    lengths = [item['length'] for item in batch]
    
    # 转换为张量
    texts = torch.stack(texts)
    labels = torch.stack(labels)
    lengths = torch.tensor(lengths)
    
    return texts, labels, lengths


# 训练函数
def train(model, train_loader, optimizer, criterion, device, epoch):
    """训练模型一个epoch"""
    model.train()
    epoch_loss = 0
    epoch_acc = 0
    
    # 创建tqdm进度条
    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch}", unit="batch")
    for batch in progress_bar:
        # 获取数据
        text, labels, lengths = batch
        text = text.to(device)
        labels = labels.to(device)
        lengths = lengths
        
        optimizer.zero_grad()
        predictions = model(text, lengths)
        loss = criterion(predictions, labels)
        
        acc = binary_accuracy(predictions, labels)
        
        # 反向传播
        loss.backward()
        # 梯度裁剪，防止梯度爆炸
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        # 更新参数
        optimizer.step()

        epoch_loss += loss.item()
        epoch_acc += acc.item()
    # 更新进度条显示
    progress_bar.set_postfix({
        'loss': f'{loss.item():.4f}',
        'acc': f'{acc.item():.4f}',
        'avg_loss': f'{epoch_loss / (progress_bar.n + 1):.4f}',
        'avg_acc': f'{epoch_acc / (progress_bar.n + 1):.4f}'
    })
    # 返回平均损失和准确率
    return epoch_loss / len(train_loader), epoch_acc / len(train_loader)

# 评估函数
def evaluate(model, iterator, criterion, device):
    """评估模型性能"""
    model.eval()
    epoch_loss = 0
    epoch_acc = 0
    
    with torch.no_grad():
        for batch in iterator:
            text, labels, lengths = batch
            text = text.to(device)
            labels = labels.to(device)
            lengths = lengths
            
            predictions = model(text, lengths)
            
            loss = criterion(predictions, labels)
            acc = binary_accuracy(predictions, labels)
            
            epoch_loss += loss.item()
            epoch_acc += acc.item()
    
    return epoch_loss / len(iterator), epoch_acc / len(iterator)

# 计算准确率
def binary_accuracy(preds, y):
    """计算二分类准确率"""
    rounded_preds = torch.round(torch.sigmoid(preds))
    correct = (rounded_preds == y).float()
    acc = correct.sum() / len(correct)
    return acc



def main():
    # 设置随机种子
    SEED = 42
    torch.manual_seed(SEED)
    torch.cuda.manual_seed(SEED)
    np.random.seed(SEED)
    random.seed(SEED)
    torch.backends.cudnn.deterministic = True
    
    # 定义设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 加载和处理数据
    print("加载数据...")
    file_path = "./data/comments.csv"
    train_texts, train_labels, valid_texts, valid_labels, test_texts, test_labels = load_and_process_data(
        file_path, test_size=0.2, valid_size=0.1
    )
    
    # 创建训练集
    print("创建训练集...")
    train_dataset = TextDataset(train_texts, train_labels, tokenizer=chinese_tokenizer, max_len=512)
    
    print("创建验证集和测试集...")
    valid_dataset = TextDataset(valid_texts, valid_labels, tokenizer=chinese_tokenizer,vocab=train_dataset.vocab,max_len=512)
    test_dataset = TextDataset(test_texts, test_labels, tokenizer=chinese_tokenizer,vocab=train_dataset.vocab,max_len=512)
    
    train_loader, valid_loader, test_loader = create_data_loaders(train_dataset, valid_dataset, test_dataset, batch_size=128)
    
    # 初始化模型
    print("初始化模型...")
    model = RNNClassifier(
        vocab_size=train_dataset.vocab_size,
        embedding_dim=100,
        hidden_dim=256,
        num_layers=2,
        dropout=0.5
    ).to(device)
    
    # 打印模型结构
    print(model)
    
    # 初始化优化器和损失函数
    optimizer = optim.Adam(model.parameters())
    criterion = nn.BCEWithLogitsLoss().to(device)
    
    # 训练模型
    print("开始训练...")
    N_EPOCHS = 10
    best_valid_acc = float(0)
    
    all_time = time.time()
    for epoch in range(N_EPOCHS):
        start_time = time.time()
        
        train_loss, train_acc = train(model, train_loader, optimizer, criterion, device, epoch)
        valid_loss, valid_acc = evaluate(model, valid_loader, criterion, device)
        
        epoch_mins, epoch_secs = divmod(time.time() - start_time, 60)
        # 保存最佳模型
        if best_valid_acc < valid_acc:
            best_valid_acc = valid_acc
            torch.save(model.state_dict(), f'best_rnn_classifier_{epoch}.pt')
            print(f'模型已保存!')
        
        print(f'Epoch: {epoch+1:02} | Epoch Time: {epoch_mins:.0f}m {epoch_secs:.0f}s')
        print(f'\tTrain Loss: {train_loss:.3f} | Train Acc: {train_acc*100:.2f}%')
        print(f'\t Val. Loss: {valid_loss:.3f} |  Val. Acc: {valid_acc*100:.2f}%')
    

    print(f"总耗时：{time.time() - all_time}")
    # 加载最佳模型并在测试集上评估
    # print("在测试集上评估...")
    # model.load_state_dict(torch.load('best_rnn_classifier.pt'))
    # test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    # print(f'Test Loss: {test_loss:.3f} | Test Acc: {test_acc*100:.2f}%')
    


if __name__ == "__main__":
    main()