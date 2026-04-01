# Real-Time Acoustic Radar for Device-Free Motion Detection

## Overview

This project implements a real-time acoustic sensing system that detects human motion using a standard laptop’s speaker and microphone. The system emits a high-frequency acoustic signal and analyzes its reflections to infer motion-related changes in the environment.

Unlike vision-based systems, this approach operates without cameras or external sensors. It leverages signal processing and machine learning techniques to model variations in the received signal caused by motion, primarily through Doppler shifts and multipath effects.

The primary task is a binary classification problem:

* `0`: no motion
* `1`: motion

---

## Problem Formulation

The system can be framed as a supervised learning problem over time-series data:

* **Input**: Sliding window of audio-derived features (e.g., spectrogram slices)
* **Output**: Binary motion label
* **Constraints**:

  * Real-time inference
  * Low latency (< 50 ms)
  * Limited computational resources (CPU-based)

---

## System Architecture

```
Signal Generation → Audio Acquisition → Buffering → Preprocessing → Feature Extraction → Model Inference → Prediction
```

### Signal Generation

* Continuous sinusoidal tone
* Frequency range: 18–20 kHz
* Sample rate: ≥ 44.1 kHz

### Audio Acquisition

* Full-duplex streaming (simultaneous playback and recording)
* Chunk-based processing (50–200 ms)

### Buffering

* Sliding window mechanism with configurable overlap
* Ensures temporal continuity for feature extraction

### Preprocessing

* Bandpass filtering around carrier frequency
* Amplitude normalization
* Windowing prior to spectral analysis

### Feature Extraction

* Short-Time Fourier Transform (STFT)
* Spectrogram patches centered around carrier frequency
* Frequency deviation (Doppler signatures)
* Energy and variance in the target band
* Optional temporal derivatives

### Model Inference

Two approaches are supported:

**Baseline**

* Threshold-based detection using spectral deviation

**Machine Learning**

* Classical models: Logistic Regression, SVM, Random Forest
* Deep learning: lightweight 1D CNN

Typical input representation:

* Spectrogram window (time × frequency)

---

## Repository Structure

```
acoustic_radar/
├── configs/                 # Configuration files (YAML/JSON)
├── data/                    # Dataset storage
│   ├── raw/                 # Unprocessed audio recordings (.wav, .npz)
│   ├── processed/           # Extracted features (.pt, .npy)
│   └── splits/              # Train/val/test index files
├── models/                  # Model artifacts
│   ├── architectures/       # PyTorch model definitions (.py)
│   └── checkpoints/         # Trained weights (.pth, .onnx)
├── notebooks/               # Jupyter notebooks for exploration
├── scripts/                 # Entry points for execution
│   ├── train.py             # Training pipeline
│   ├── evaluate.py          # Model evaluation
│   └── run_realtime.py      # Main real-time application
├── src/                     # Core source code (importable package)
│   ├── __init__.py
│   ├── audio_io/            # Audio hardware interaction
│   ├── dsp/                 # Digital Signal Processing logic
│   ├── features/            # Feature extraction modules
│   ├── models/              # ML model classes (inference)
│   └── utils/               # Helpers (logging, viz, config)
├── tests/                   # Unit and integration tests
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/anesmeftah/acoustic-radar.git
cd acoustic-radar
pip install -r requirements.txt
```

### Dependencies

* numpy
* scipy
* matplotlib
* sounddevice
* torch (optional, for deep learning models)
* scikit-learn (for baseline models)

---

## Usage

```bash
python main.py --config configs/default.yaml
```

### Example Configuration

```yaml
sample_rate: 48000
carrier_freq: 19000
window_size_ms: 100
hop_size_ms: 50
threshold: 0.2
model_path: models/cnn.pt
```

---

## Data Collection

Data quality is the main bottleneck in this project.

Recommended protocol:

* Collect labeled audio in controlled environments
* Include both positive (motion) and negative (no motion) samples
* Vary distance, orientation, and motion type
* Include realistic noise conditions

Typical dataset:

* Input: raw audio or processed spectrograms
* Labels: binary motion indicator

---

## Feature Engineering

Effective features are critical for performance:

* Spectrogram patches around the carrier frequency
* Peak frequency deviation from baseline
* Energy distribution in frequency bands
* Temporal gradients (delta features)

Dimensionality reduction (PCA, t-SNE) can be used to validate class separability.

---

## Model Development

### Baseline Models

* Logistic Regression
* Support Vector Machine
* Random Forest

These provide strong baselines with low computational cost.

### Deep Learning Model

A lightweight 1D CNN is recommended:

* Input: spectrogram window
* Architecture: Conv → Normalization → Activation → Pooling → Dense
* Constraint: < 100k parameters for real-time inference

### Evaluation Metrics

* Accuracy
* Precision / Recall
* F1-score
* Detection latency
* False positive rate over time

---

## Real-Time Constraints

This system operates under strict timing constraints:

* End-to-end latency must remain below the hop size
* Audio callbacks must be non-blocking
* Feature extraction and inference must be optimized

Naive implementations often fail due to:

* Buffer mismanagement
* Blocking I/O
* Excessive model complexity

---

## Limitations

* Strong dependence on microphone and speaker quality
* Sensitivity to environmental noise
* Limited spatial awareness (no localization)
* Performance degradation in acoustically complex environments

---

## Reproducibility

To ensure consistent results:

* Fix random seeds during training
* Version datasets and preprocessing steps
* Store model checkpoints and configurations
* Log evaluation metrics systematically

---

## License

MIT License

---

## Author

anesmeftah
[https://github.com/anesmeftah](https://github.com/anesmeftah)

---

## Notes

This project sits at the intersection of:

* Digital Signal Processing (DSP)
* Time-series analysis
* Embedded machine learning

The main difficulty is not the model itself, but building a **stable, low-latency data pipeline**. Poor signal quality or incorrect buffering will invalidate downstream machine learning results.
