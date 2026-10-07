# 🎓 AI-Powered Fitness Coach — Academic AIML Viva Examination Guide

This guide is curated specifically for a **3rd-Year AIML University Project Defense and Viva Examination**.

---

## 1. Problem Statement & Motivation
**Examiner Question:** *"What is the core problem and why is computer vision suited for fitness form coaching?"*
- **Problem:** Resistance training injuries and suboptimal muscle recruitment occur due to biomechanical form breakdown (e.g. knee valgus in squats, lumbar hyperextension in overhead press, elbow flare in pushups). Personal trainers are cost-prohibitive for mass adoption, while wearable IMU sensors require cumbersome hardware calibration.
- **Solution:** Monocular RGB computer vision tracks 3D skeletal kinematics non-invasively using commodity smartphone cameras.

---

## 2. Mathematical Foundations & Formulations

### A. Scale-Invariant Hip Normalization
To make landmark coordinates invariant to distance from the camera and human stature:
$$\vec{P}_{origin} = \frac{\vec{P}_{left\_hip} + \vec{P}_{right\_hip}}{2}$$
$$s = \|\vec{P}_{shoulder\_mid} - \vec{P}_{hip\_mid}\|_2$$
$$\hat{P}_i = \frac{\vec{P}_i - \vec{P}_{origin}}{s}$$

### B. 3D Joint Angle Formulation
For any joint vertex $B$ connecting limbs $A$ and $C$:
$$\vec{u} = \vec{A} - \vec{B}, \quad \vec{v} = \vec{C} - \vec{B}$$
$$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2}\right) \times \frac{180^\circ}{\pi}$$

### C. Kinematic Smoothness & Jerk Minimization
Jerk is the 3rd derivative of position (or 2nd derivative of angular velocity):
$$J(t) = \frac{d^2 \omega(t)}{dt^2}$$
Smoothness Score:
$$S = \max\left(0, 100 - \frac{1}{N}\sum_{t=1}^N |J(t)|\right)$$

### D. Multi-Dimensional Composite Scoring
$$\text{Score} = 0.45 \cdot S_{\text{accuracy}} + 0.25 \cdot S_{\text{ROM}} + 0.15 \cdot S_{\text{tempo}} + 0.15 \cdot S_{\text{symmetry}}$$

---

## 3. Machine Learning Model Architecture & Trade-Offs

| Metric / Dimension | Random Forest (150 Trees) | XGBoost (Gradient Boosted) | PyTorch Bi-LSTM |
| :--- | :--- | :--- | :--- |
| **Primary Task** | Exercise Recognition | Biomechanical Form Faults | Temporal Sequence Phase Modeling |
| **Input Shape** | Tabular 1D (142 features) | Tabular 1D (142 features) | Sequential 3D $(B, 30, 99)$ |
| **Inference Latency**| 1.85 ms | **0.49 ms** | 4.50 ms |
| **Throughput** | ~540 FPS | **~2,034 FPS** | ~222 FPS |
| **Test Accuracy** | 94.2% | 91.5% | 98.4% (sequence) |
| **Why Chosen?** | High robustness against tabular noise | Ultra-low edge CPU latency | Captures temporal velocity transitions |

---

## 4. Deterministic State-Machine Rep Counting

**Examiner Question:** *"Why not count reps using a pure deep learning classifier?"*
- **Answer:** Deep learning sequence models trained on raw video tend to suffer from boundary ambiguity, frame rate variations, and double-counting during user hesitation.
- **Our Approach:** We implement a **Finite State Machine with Hysteresis**:
  - `IDLE`: Upright posture, joints near lockout ($\theta > 160^\circ$).
  - `ECCENTRIC`: Descent begins ($\theta < 145^\circ$).
  - `INFLECTION`: Lowest point reached ($\theta \le 95^\circ$). Peak turnaround time is recorded.
  - `CONCENTRIC`: Ascending back ($\theta > \theta_{min} + 12^\circ$).
  - `COMPLETED`: Lockout restored ($\theta \ge 160^\circ$) with minimum duration filter ($\Delta t \ge 0.8\text{s}$).

---

## 5. Dataset Rigor & Anti-Leakage Measures
1. **Video-Level Split:** Splitting was performed strictly at the **video level** (70/15/15), ensuring no consecutive frames from the same video ever exist in both train and validation sets.
2. **Deduplication:** SHA-256 content hashing identified 8 exact duplicates between `similar_dataset` and `final_kaggle`.
3. **Quarantined External Test:** `my_test_video_1` was isolated as a strict external test holdout.
