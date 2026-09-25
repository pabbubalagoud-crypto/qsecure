# 🔐 Q-Secure: Quantum Eavesdropper Detector
**BB84 Quantum Key Distribution Simulator**

Detects eavesdroppers on quantum communication channels using the BB84 protocol.

---

## 🚀 Quick Start

### 1. Clone / Download the project
```bash
cd qsecure
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## 🎮 How to Demo

| Step | Action | Result |
|------|--------|--------|
| 1 | Toggle **Eve OFF** | QBER ≈ 0%, 🟢 SECURE |
| 2 | Click **Run Quantum Simulation** | See clean key, low error rate |
| 3 | Toggle **Eve ON** | QBER jumps to ~25% |
| 4 | Click **Run Quantum Simulation** | 🔴 EAVESDROPPING DETECTED |

---

## 📁 Project Structure

```
qsecure/
├── app.py            ← Streamlit UI
├── bb84.py           ← BB84 quantum simulation logic
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## ⚛️ BB84 Protocol — How It Works

```
Alice ──────────────────────────────────→ Bob
  │           QUANTUM CHANNEL             │
  │                                       │
  └──────────── Eve (optional) ──────────┘
```

1. **Alice** generates random bits and encodes them using random quantum bases
   - Z-basis (rectilinear): `|0⟩` = ↑, `|1⟩` = ↓  
   - X-basis (diagonal): `|+⟩` = ↗, `|−⟩` = ↘

2. **Eve** (if active) intercepts qubits, measures with a random basis, resends
   - Wrong basis guess → collapses qubit → introduces errors

3. **Bob** measures each received qubit with a random basis

4. **Sifting**: Alice and Bob compare bases publicly, keep only matching ones

5. **QBER Check**: They sacrifice a sample to estimate the error rate
   - QBER < 11% → **SECURE** ✅
   - QBER ≈ 25% → **EVE DETECTED** 🚨

---

## 🔬 Quantum Physics Behind It

| Scenario | Result |
|----------|--------|
| Alice & Bob same basis, no Eve | 0% errors |
| Alice & Bob same basis, Eve intercepts | ~25% errors |
| Eve guesses basis correctly | No disturbance |
| Eve guesses basis wrong | 50% chance of wrong bit → error |

**Why ~25%?**
- Eve guesses wrong basis 50% of the time
- When wrong, she introduces 50% error on that qubit
- 50% × 50% = **25% QBER**

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Streamlit | Interactive web UI |
| NumPy | Quantum probability simulation |
| Plotly | QBER gauge, charts |
| Pandas | Protocol table |
| Qiskit | Quantum computing framework (listed as dependency) |

> **Note:** This simulator implements quantum probability rules faithfully in NumPy/Python without needing a real quantum computer. The same logic runs on Qiskit's `qasm_simulator` backend.

---

## 🏆 Hackathon Talking Points

- **No quantum hardware needed** — runs on any laptop
- **Real quantum physics** — superposition, measurement collapse, Heisenberg uncertainty
- **Clear visual demo** — one button shows secure, one shows detected
- **Mathematical proof** — QBER formula is provably ~25% with eavesdropper
- **Extensible** — can swap NumPy backend for real Qiskit circuits

---

## 📄 License
MIT License — free to use, modify, and distribute.
