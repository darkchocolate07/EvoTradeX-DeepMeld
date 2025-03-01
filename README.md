# AI TRADING SYSTEM
___        _            ___         _     _            

> **A unified pipeline for data ingestion, deep learning modeling, fuzzy clustering, and reinforcement learning in an AI-powered trading system.**  

---

## 📌 TABLE OF CONTENTS
- [Overview](#overview)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Installation](#installation)
- [Data Pipeline](#data-pipeline)
- [Feature Engineering](#feature-engineering)
- [Clustering & Fuzzification](#clustering--fuzzification)
- [SeroFAM Module](#serofam-module)
- [Transformer + GRU Model](#transformer--gru-model)
- [Reinforcement Learning Agent](#reinforcement-learning-agent)
- [Frontend](#frontend)
- [Usage](#usage)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## OVERVIEW
This project integrates **fuzzy clustering**, **deep learning** (GRU + Transformer), and **reinforcement learning** to create an **adaptive AI trading system**. It continuously ingests and processes real-world financial data, extracts meaningful features, and generates **buy/sell signals** via a sophisticated RL agent. The pipeline handles data from multiple sources (e.g., insider info, news, social media sentiment) to inform a robust market prediction model.

---


---

## KEY COMPONENTS
- **Data Pipeline**: Pulls and updates real-time financial data (stocks, crypto) plus insider info, news sentiment, and social media analytics.
- **Feature Engineering**: Cleans, normalizes, and fuses multiple data sources. Creates custom indicators.
- **Clustering & Fuzzification**: Learns fuzzy memberships (DIC, FCKN, FuzzyART) for interpretability.
- **SeroFAM**: Self-Reorganizing Fuzzy Associative Machine for incremental rule-based adaptation.
- **Transformer + GRU**: Combines short-term pattern extraction (GRU) with long-term dependencies (Transformer).
- **RL Agent**: PPO-based agent that optimizes portfolio allocations and trade decisions.
- **Frontend**: Real-time interactive dashboard to visualize signals, trades, and portfolio metrics.

---

## INSTALLATION
1. **Clone the Repo**:
git clone https://github.com/YourUser/AITradingSystem.git cd AITradingSystem

2. **Install Dependencies**:
3. **Set Up Data**: Provide your data in the `data/` folder or configure `data_download/` scripts to fetch from APIs.

---

## DATA PIPELINE
- **historical_price_data.py**: Fetches historical OHLCV from Yahoo Finance or any chosen source.
- **news_sentiment.py**: Extracts sentiment from major news outlets.
- **social_media_sentiment.py**: Scrapes Twitter/Reddit to gauge crowd sentiment.
- **multimodal_data_fusion.py**: Merges insider info, fundamental data, sentiment, and price streams into a single dataset.

---

## FEATURE ENGINEERING
- **technical_indicators.py**: Creates advanced features (RSI, MACD, Bollinger Bands).
- **expert_system.py**: Optionally adds logic-based features or flags (insider buys, unusual volume).
- **DataFrame merges** to produce final training set with relevant features and targets.

---

## CLUSTERING & FUZZIFICATION
Inside **PredictionModel/Clustering_Fuzzification**:
- **DIC.py**: Discrete Incremental Clustering to handle unknown number of clusters.  
- **FCKN.py**: Fuzzy Kohonen Clustering Network merges fuzzy logic + Kohonen self-organization.  
- **FuzzyART.py**: Adaptively learns categories in an on-line manner without prior cluster count.

These modules transform numeric data into fuzzy memberships that feed the fuzzy systems or deep learning pipelines.

---

## SeroFAM MODULE
In **PredictionModel/SeroFam**:
- **SeroFAM.py**: A Self-Reorganizing Fuzzy Associative Machine that incrementally refines fuzzy rules in real-time.  
- Combines Hebbian-like updates with fuzzy rule management to handle non-stationary markets.

---

## TRANSFORMER + GRU MODEL
In **PredictionModel/TransformerModel**:
- **GRUTransformer.py**: Hybrid deep model.  
- GRU handles short-term memory of price movements.  
- Transformer extracts long-range patterns and multi-horizon forecasts.  
- Output layer produces final market predictions (price direction, volatility, etc.).

---

## REINFORCEMENT LEARNING AGENT
In **PredictionModel/RL_Agent**:
- **environment.py**: Custom Gym environment for simulating trades, PnL, transaction costs.  
- **memory.py**: Rollout buffer for storing state transitions.  
- **networks.py**: Actor-Critic architecture.  
- **agent.py**: PPO logic. Periodically updates policy to maximize cumulative rewards (Sharpe ratio, etc.).

---

## FRONTEND
In **frontend**:
- Real-time dashboard to display:
- **Market data** (candlesticks, volume).  
- **RL signals** (buy/sell, confidence).  
- **Portfolio performance** (PnL, Sharpe ratio).  
- Possible frameworks: React, Vue, or plain HTML + JS. Connects to backend via REST or WebSocket.

---


