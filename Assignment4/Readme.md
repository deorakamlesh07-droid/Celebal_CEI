# 🚀 CIFAR-10 Image Classification with ANN and CNN

## 📌 Overview

This project implements and compares multiple deep learning architectures for image classification on the CIFAR-10 dataset using TensorFlow and Keras. The objective is to evaluate how different neural network architectures and training strategies affect classification performance.

The project begins with a baseline Artificial Neural Network (ANN) trained on flattened image vectors, progresses to a Convolutional Neural Network (CNN) that leverages spatial feature extraction, and concludes with advanced variants including a deeper ANN and a CNN enhanced with data augmentation and Early Stopping.

---

## 📂 Dataset

**CIFAR-10**

* 50,000 training images
* 10,000 test images
* 10 object classes
* Image size: 32 × 32 × 3 (RGB)

### Classes
✈️ Airplane
🚗 Automobile
🐦 Bird
🐱 Cat
🦌 Deer
🐶 Dog
🐸 Frog
🐴 Horse
🚢 Ship
🚚 Truck

---

## 🛠️ Project Workflow

1. Load and preprocess the CIFAR-10 dataset.
2. Normalize pixel values from 0–255 to 0–1.
3. Train a Baseline ANN on flattened image vectors.
4. Train a Baseline CNN using convolutional layers.
5. Compare validation accuracy curves.
6. Develop advanced model variants.
7. Apply data augmentation and Early Stopping.
8. Evaluate and compare all models.

---

## 🧠 Models Implemented

### 1. Baseline ANN

* Flatten layer
* Dense layers
* Dropout regularization
* 10 training epochs

### 2. Baseline CNN

* Conv2D
* BatchNormalization
* MaxPooling2D
* Dense classifier
* 10 training epochs

### 3. Advanced ANN

* Deeper dense architecture
* Additional hidden layers
* Increased model capacity

### 4. Augmented CNN ⭐

* Data augmentation
* CNN feature extraction
* Early Stopping
* Up to 20 training epochs

---

## 📊 Results

| Model         | Test Accuracy |
| ------------- | ------------- |
| Baseline ANN  | 42.77%        |
| Advanced ANN  | 41.96%        |
| Baseline CNN  | 67.31%        |
| Augmented CNN | **75.44%** 🏆 |

### 🔍 Key Observations

* ANN models struggled to capture spatial image features.
* CNN architectures significantly improved classification accuracy.
* Data augmentation reduced overfitting and improved generalization.
* The Augmented CNN achieved the highest test accuracy.

---

## 📈 Performance Evolution

```text
Baseline ANN   → 42.77%
Advanced ANN   → 41.96%
Baseline CNN   → 67.31%
Augmented CNN  → 75.44%
```

This progression demonstrates the effectiveness of convolutional feature extraction and data augmentation for image classification tasks.

---

## 💻 Technologies Used

* Python
* TensorFlow
* Keras
* NumPy
* Pandas
* Matplotlib

---

## 🎯 Conclusion

The experimental results demonstrate that Convolutional Neural Networks outperform traditional Artificial Neural Networks on image classification tasks. The Augmented CNN achieved the best balance between accuracy and generalization, reaching a test accuracy of **75.44%** while maintaining a minimal generalization gap.

This project highlights the importance of:

* Spatial feature extraction through CNNs
* Data augmentation for improved robustness
* Proper model evaluation using train, validation, and test metrics

🏆 **Best Model: Augmented CNN**

