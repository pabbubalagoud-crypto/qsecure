"""
bb84.py — Pure BB84 Quantum Key Distribution Simulation
Implements faithful quantum probability rules without requiring a real quantum computer.
Uses Qiskit-style logic: superposition, measurement collapse, basis mismatch randomness.
"""

import numpy as np
import pandas as pd
from datetime import datetime


class BB84Simulator:
    """
    Simulates the BB84 Quantum Key Distribution protocol.

    Quantum rules implemented:
    - Same basis measurement  → deterministic (correct bit)
    - Different basis measurement → 50/50 random (superposition collapse)
    - Eve intercept with wrong basis → disturbs qubit → ~25% QBER on sifted key
    """

    # Basis constants
    Z_BASIS = 0   # Rectilinear: |0⟩, |1⟩
    X_BASIS = 1   # Diagonal:    |+⟩, |−⟩

    BASIS_LABELS = {0: "Z(↑)", 1: "X(↗)"}

    def __init__(self, n_qubits: int = 100, eve_present: bool = False, sample_pct: float = 0.25):
        self.n_qubits    = n_qubits
        self.eve_present = eve_present
        self.sample_pct  = sample_pct
        self.rng         = np.random.default_rng()

        # Will be populated after run()
        self.alice_bits   = None
        self.alice_bases  = None
        self.eve_bases    = None
        self.eve_measured = None
        self.bob_bases    = None
        self.bob_results  = None

    # ── Quantum measurement ──────────────────────────────────────────────────
    def _measure(self, bit: int, prep_basis: int, meas_basis: int) -> int:
        """
        Simulate quantum measurement of a qubit.
        - Same basis → deterministic (no disturbance)
        - Different basis → random 50/50 (Heisenberg uncertainty / superposition collapse)
        """
        if prep_basis == meas_basis:
            return bit
        return int(self.rng.integers(0, 2))

    # ── Main simulation ──────────────────────────────────────────────────────
    def run(self) -> dict:
        n   = self.n_qubits
        log = []

        def ts():
            return datetime.now().strftime("%H:%M:%S")

        log.append(f"[{ts()}] Starting BB84 simulation — {n} qubits, Eve={'ON' if self.eve_present else 'OFF'}")

        # Step 1: Alice generates random bits and bases
        self.alice_bits  = self.rng.integers(0, 2, size=n)
        self.alice_bases = self.rng.integers(0, 2, size=n)
        log.append(f"[{ts()}] Alice generated {n} random bits and {n} random bases")

        # Step 2: Quantum channel — Eve optionally intercepts
        self.eve_bases    = self.rng.integers(0, 2, size=n)
        self.eve_measured = np.full(n, -1, dtype=int)
        resent_bits       = self.alice_bits.copy()
        resent_bases      = self.alice_bases.copy()

        if self.eve_present:
            log.append(f"[{ts()}] ⚠ Eve is intercepting ALL {n} qubits with random basis guesses")
            for i in range(n):
                m = self._measure(self.alice_bits[i], self.alice_bases[i], self.eve_bases[i])
                self.eve_measured[i] = m
                resent_bits[i]  = m
                resent_bases[i] = self.eve_bases[i]  # Eve resends from her measured state
            correct_guesses = int(np.sum(self.eve_bases == self.alice_bases))
            log.append(f"[{ts()}] Eve guessed basis correctly {correct_guesses}/{n} times ({correct_guesses/n*100:.1f}%)")
        else:
            log.append(f"[{ts()}] Channel clear — qubits pass through undisturbed")

        # Step 3: Bob measures with random bases
        self.bob_bases   = self.rng.integers(0, 2, size=n)
        self.bob_results = np.array([
            self._measure(resent_bits[i], resent_bases[i], self.bob_bases[i])
            for i in range(n)
        ])
        log.append(f"[{ts()}] Bob measured {n} qubits with random bases")

        # Step 4: Sifting — keep only matching bases
        match_mask    = self.alice_bases == self.bob_bases
        sifted_idx    = np.where(match_mask)[0]
        alice_sifted  = self.alice_bits[sifted_idx]
        bob_sifted    = self.bob_results[sifted_idx]
        matching_bases = len(sifted_idx)

        log.append(f"[{ts()}] Sifting complete — {matching_bases}/{n} qubits kept ({matching_bases/n*100:.1f}%)")

        # Step 5: QBER estimation on sample
        sample_size = max(1, int(matching_bases * self.sample_pct))
        sample_idx  = self.rng.choice(len(alice_sifted), size=sample_size, replace=False)
        sample_alice = alice_sifted[sample_idx]
        sample_bob   = bob_sifted[sample_idx]
        errors        = int(np.sum(sample_alice != sample_bob))
        qber          = errors / sample_size if sample_size > 0 else 0.0

        log.append(f"[{ts()}] QBER sample: {sample_size} bits, {errors} errors → QBER = {qber*100:.1f}%")

        # Remove sample bits from final key
        keep_mask   = np.ones(len(alice_sifted), dtype=bool)
        keep_mask[sample_idx] = False
        alice_key   = alice_sifted[keep_mask]
        bob_key     = bob_sifted[keep_mask]
        key_errors  = int(np.sum(alice_key != bob_key))

        is_secure = qber < 0.11
        if is_secure:
            log.append(f"[{ts()}] ✅ SECURE — QBER {qber*100:.1f}% < 11% threshold. Key of {len(alice_key)} bits is safe.")
        else:
            log.append(f"[{ts()}] 🚨 EAVESDROPPING DETECTED — QBER {qber*100:.1f}% ≥ 11% threshold. Discard key!")

        # Store for later use
        self._sifted_idx   = sifted_idx
        self._alice_sifted = alice_sifted
        self._bob_sifted   = bob_sifted

        return {
            "n_qubits":      n,
            "matching_bases": matching_bases,
            "key_length":    len(alice_key),
            "sample_size":   sample_size,
            "errors":        errors,
            "qber":          qber,
            "alice_key":     alice_key.tolist(),
            "bob_key":       bob_key.tolist(),
            "is_secure":     is_secure,
            "log":           log,
        }

    # ── Basis distribution for chart ─────────────────────────────────────────
    def basis_distribution(self) -> list:
        """Returns counts of [ZZ, XX, ZX, XZ] basis combinations."""
        if self.alice_bases is None:
            return [0, 0, 0, 0]
        zz = int(np.sum((self.alice_bases == 0) & (self.bob_bases == 0)))
        xx = int(np.sum((self.alice_bases == 1) & (self.bob_bases == 1)))
        zx = int(np.sum((self.alice_bases == 0) & (self.bob_bases == 1)))
        xz = int(np.sum((self.alice_bases == 1) & (self.bob_bases == 0)))
        return [zz, xx, zx, xz]

    # ── Protocol dataframe for table ─────────────────────────────────────────
    def protocol_dataframe(self, n: int = 30) -> pd.DataFrame:
        """Returns a DataFrame showing the first n qubits of the protocol."""
        if self.alice_bits is None:
            return pd.DataFrame()

        display_n = min(n, self.n_qubits)
        rows = []

        for i in range(display_n):
            ab  = self.alice_bases[i]
            bb  = self.bob_bases[i]
            match = ab == bb
            eve_m = str(self.eve_measured[i]) if self.eve_present and self.eve_measured[i] >= 0 else "—"
            eve_b = self.BASIS_LABELS[self.eve_bases[i]] if self.eve_present else "—"

            # Is this a key bit?
            in_sifted = i in self._sifted_idx if hasattr(self, "_sifted_idx") else match
            if in_sifted and hasattr(self, "_alice_sifted"):
                idx_pos = np.where(self._sifted_idx == i)[0]
                if len(idx_pos) > 0:
                    pos = idx_pos[0]
                    key_bit = str(self._alice_sifted[pos])
                    is_err  = self._alice_sifted[pos] != self._bob_sifted[pos]
                else:
                    key_bit = "—"
                    is_err  = False
            else:
                key_bit = "—"
                is_err  = False

            rows.append({
                "#":            i + 1,
                "Alice Bit":    int(self.alice_bits[i]),
                "Alice Basis":  self.BASIS_LABELS[ab],
                "Eve Intercept": eve_m,
                "Eve Basis":    eve_b,
                "Bob Basis":    self.BASIS_LABELS[bb],
                "Bob Result":   int(self.bob_results[i]),
                "Bases Match?": "✓" if match else "✗",
                "Error?":       "YES" if is_err else ("No" if match else "—"),
                "Key Bit":      key_bit,
            })

        return pd.DataFrame(rows)
