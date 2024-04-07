# -*- coding: utf-8 -*-
"""train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KfonWfhVfolD5voFH9fVKLG9c21iAwuC
"""

# Commented out IPython magic to ensure Python compatibility.
# %load_ext autoreload
# %autoreload 2

from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from baseline import *
import numpy as np
import torch.optim as optim

# model
model = CNNBaseline()

# other external model settings
num_epochs = 15
batch_size = 4
train_acc, train_loss, val_acc, val_loss = [], [], [], []

# data preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

dataset = ImageFolder('./data', transform=transform)

train_size = int(0.7 * len(dataset))
val_size = int(0.2 * len(dataset))
test_size = len(dataset) - train_size - val_size

train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, val_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)
test_loader = DataLoader(test_dataset, batch_size=len(test_dataset))

# setting metrics
criterion = torch.nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.00005)

# device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# training and validating the model

min_val_loss = np.inf

for epoch in range(num_epochs):
    num_correct = 0
    epoch_train_loss = 0
    model.train()
    num_batches = 0
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()

        outputs = model(inputs)

        _, predictions = outputs.max(1)
        num_correct += (predictions == labels).sum().item()
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        epoch_train_loss += loss.item()

        num_batches = batch_idx

    train_acc.append(num_correct / num_batches)
    train_loss.append(epoch_train_loss / num_batches)


    model.eval()
    epoch_val_loss = 0
    epoch_val_correct = 0
    num_val_batches = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            _, predictions = outputs.max(1)
            epoch_val_correct += (predictions == labels).sum().item()
            loss = criterion(outputs, labels)
            epoch_val_loss += loss.item()

            num_val_batches += 1

    epoch_val_acc = epoch_val_correct / len(val_loader.dataset)
    epoch_val_loss /= num_val_batches

    val_loss.append(epoch_val_loss)
    val_acc.append(epoch_val_acc)

    if epoch_val_loss < min_val_loss:
      min_val_loss = epoch_val_loss
      torch.save(model.state_dict(), './models/final_model.h5')



    print('Epoch [{}/{}], Loss: {:.4f}, Val Loss: {:.4f}, Val Acc: {:.4f}'.format(epoch+1, num_epochs, train_loss[-1], val_loss[-1], val_acc[-1]))

# Load model
device = torch.device("cuda")
model = CNNBaseline()
model.load_state_dict(torch.load('./models/final_model.h5'))
model = model.to(device)

# Testing model
test_correct = 0
test_loss = 0

with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs)
            _, predictions = outputs.max(1)
            test_correct += (predictions == labels).sum().item()
            loss = criterion(outputs, labels)
            test_loss += loss.item()

            num_val_batches += 1
        test_acc = test_correct / len(test_loader.dataset)


        print('Test Loss: {:.4f}, Test Acc: {:.4f}'.format(test_loss, test_acc))