# Dataset1 Inspection Report

**Dataset:** Physical Exercise Recognition | Time Series Dataset
**Location:** `D:\AIML_Project\Dataset\Dataset1`
**Inspection Date:** 2026-09-12 01:35:17

## File Summary

| File | Rows | Columns | Size |
|------|------|---------|------|
| `angles.csv` | 83,922 | 9 | 6.0 MB |
| `calculated_3d_distances.csv` | 83,922 | 18 | 12.8 MB |
| `labels.csv` | 448 | 2 | 0.0 MB |
| `landmarks.csv` | 83,922 | 101 | 81.8 MB |
| `xyz_distances.csv` | 83,922 | 50 | 39.6 MB |

---
## angles.csv

- **Shape:** 83,922 rows × 9 columns
- **File size:** 6.02 MB
- **Missing values:** 0
- **Duplicate rows:** 0

### Columns

| Column | Data Type | Non-Null | Unique | Sample Values |
|--------|-----------|----------|--------|---------------|
| `vid_id` | int64 | 83,922 | 448 | 0, 1, 2 |
| `frame_order` | int64 | 83,922 | 301 | 0, 1, 2 |
| `right_elbow_right_shoulder_right_hip` | float64 | 83,922 | 83,590 | 16.926802, 14.199318, 18.0658 |
| `left_elbow_left_shoulder_left_hip` | float64 | 83,922 | 83,603 | 7.667874, 8.954973, 10.315741 |
| `right_knee_mid_hip_left_knee` | float64 | 83,922 | 83,493 | 18.982162, 18.966124, 17.527954 |
| `right_hip_right_knee_right_ankle` | float64 | 83,922 | 83,235 | 112.747505, 109.70719, 114.5621 |
| `left_hip_left_knee_left_ankle` | float64 | 83,922 | 83,271 | 112.62553, 109.76263, 112.08965 |
| `right_wrist_right_elbow_right_shoulder` | float64 | 83,922 | 83,208 | 112.0993, 110.645454, 113.34035 |
| `left_wrist_left_elbow_left_shoulder` | float64 | 83,922 | 83,263 | 101.05565, 102.00027, 104.09502 |

---
## calculated_3d_distances.csv

- **Shape:** 83,922 rows × 18 columns
- **File size:** 12.84 MB
- **Missing values:** 0
- **Duplicate rows:** 0

### Columns

| Column | Data Type | Non-Null | Unique | Sample Values |
|--------|-----------|----------|--------|---------------|
| `vid_id` | int64 | 83,922 | 448 | 0, 1, 2 |
| `frame_order` | int64 | 83,922 | 301 | 0, 1, 2 |
| `left_shoulder_left_wrist` | float64 | 83,922 | 83,591 | 44.616184, 44.785343, 44.907803 |
| `right_shoulder_right_wrist` | float64 | 83,922 | 83,594 | 45.58366, 45.319645, 45.655598 |
| `left_hip_left_ankle` | float64 | 83,922 | 83,535 | 74.31164, 76.10876, 76.511536 |
| `right_hip_right_ankle` | float64 | 83,922 | 83,571 | 75.78382, 76.79507, 78.169975 |
| `left_hip_left_wrist` | float64 | 83,922 | 83,560 | 33.730007, 31.981766, 39.03759 |
| `right_hip_right_wrist` | float64 | 83,922 | 83,582 | 42.13161, 39.302784, 43.101467 |
| `left_shoulder_left_ankle` | float64 | 83,922 | 83,461 | 122.58039, 123.38482, 128.73569 |
| `right_shoulder_right_ankle` | float64 | 83,922 | 83,468 | 127.11895, 126.65802, 132.46251 |
| `left_hip_right_wrist` | float64 | 83,922 | 83,572 | 51.88966, 49.100586, 51.61608 |
| `right_hip_left_wrist` | float64 | 83,922 | 83,540 | 34.165817, 33.16866, 40.597023 |
| `left_elbow_right_elbow` | float64 | 83,922 | 83,631 | 29.366705, 28.751902, 27.868805 |
| `left_knee_right_knee` | float64 | 83,922 | 83,658 | 11.997074, 11.787817, 10.669149 |
| `left_wrist_right_wrist` | float64 | 83,922 | 83,657 | 34.49884, 35.02561, 36.084465 |
| `left_ankle_right_ankle` | float64 | 83,922 | 83,668 | 9.536471, 9.934409, 9.258501 |
| `left_hip_avg_left_wrist_left_ankle` | float64 | 83,922 | 83,635 | 34.766296, 34.764217, 34.062817 |
| `right_hip_avg_right_wrist_right_ankle` | float64 | 83,922 | 83,626 | 34.263794, 33.39555, 33.561043 |

---
## labels.csv

- **Shape:** 448 rows × 2 columns
- **File size:** 0.01 MB
- **Missing values:** 0
- **Duplicate rows:** 0

### Columns

| Column | Data Type | Non-Null | Unique | Sample Values |
|--------|-----------|----------|--------|---------------|
| `vid_id` | int64 | 448 | 448 | 0, 1, 2 |
| `class` | str | 448 | 5 | jumping_jack, pull_up, push_up |

---
## landmarks.csv

- **Shape:** 83,922 rows × 101 columns
- **File size:** 81.81 MB
- **Missing values:** 0
- **Duplicate rows:** 0

### Columns

| Column | Data Type | Non-Null | Unique | Sample Values |
|--------|-----------|----------|--------|---------------|
| `vid_id` | int64 | 83,922 | 448 | 0, 1, 2 |
| `frame_order` | int64 | 83,922 | 301 | 0, 1, 2 |
| `x_nose` | float64 | 83,922 | 83,737 | -0.6458509, -0.29047298, -0.3781558 |
| `y_nose` | float64 | 83,922 | 83,193 | -59.99263, -61.06931, -61.102 |
| `z_nose` | float64 | 83,922 | 83,727 | -80.985, -78.4787, -86.33219 |
| `x_left_eye_inner` | float64 | 83,922 | 83,736 | 0.5604641, 0.8813095, 0.96860325 |
| `y_left_eye_inner` | float64 | 83,922 | 83,166 | -62.55525, -63.67481, -63.431263 |
| `z_left_eye_inner` | float64 | 83,922 | 83,731 | -76.38421, -73.719315, -81.922356 |
| `x_left_eye` | float64 | 83,922 | 83,733 | 1.3626087, 1.6396329, 1.7886573 |
| `y_left_eye` | float64 | 83,922 | 83,174 | -62.543415, -63.648945, -63.423435 |
| `z_left_eye` | float64 | 83,922 | 83,737 | -76.38174, -73.71788, -81.92055 |
| `x_left_eye_outer` | float64 | 83,922 | 83,732 | 1.9466951, 2.199054, 2.3845415 |
| `y_left_eye_outer` | float64 | 83,922 | 83,170 | -62.432976, -63.530403, -63.350002 |
| `z_left_eye_outer` | float64 | 83,922 | 83,731 | -76.3819, -73.717125, -81.92332 |
| `x_right_eye_inner` | float64 | 83,922 | 83,732 | -1.824263, -1.4756736, -1.5426731 |
| `y_right_eye_inner` | float64 | 83,922 | 83,206 | -62.312202, -63.36599, -63.163673 |
| `z_right_eye_inner` | float64 | 83,922 | 83,745 | -77.34051, -74.58266, -82.56537 |
| `x_right_eye` | float64 | 83,922 | 83,732 | -2.6609955, -2.3498347, -2.4024591 |
| `y_right_eye` | float64 | 83,922 | 83,205 | -62.112595, -63.129837, -62.982796 |
| `z_right_eye` | float64 | 83,922 | 83,729 | -77.349, -74.588936, -82.574554 |
| `x_right_eye_outer` | float64 | 83,922 | 83,734 | -3.4569702, -3.0943406, -3.1987705 |
| `y_right_eye_outer` | float64 | 83,922 | 83,173 | -61.828804, -62.86121, -62.734528 |
| `z_right_eye_outer` | float64 | 83,922 | 83,731 | -77.3485, -74.58703, -82.574875 |
| `x_left_ear` | float64 | 83,922 | 83,724 | 2.989569, 3.2640505, 3.5998788 |
| `y_left_ear` | float64 | 83,922 | 83,126 | -60.542645, -61.494858, -61.425137 |
| `z_left_ear` | float64 | 83,922 | 83,732 | -47.39664, -44.665066, -53.781845 |
| `x_right_ear` | float64 | 83,922 | 83,724 | -4.697913, -4.365295, -4.3094683 |
| `y_right_ear` | float64 | 83,922 | 83,180 | -60.102783, -60.951866, -60.874928 |
| `z_right_ear` | float64 | 83,922 | 83,747 | -52.24263, -49.109596, -57.187756 |
| `x_mouth_left` | float64 | 83,922 | 83,744 | 0.96722394, 1.2737361, 1.346518 |
| `y_mouth_left` | float64 | 83,922 | 83,235 | -56.71856, -57.761627, -57.62824 |
| `z_mouth_left` | float64 | 83,922 | 83,732 | -70.09636, -67.63869, -75.7604 |
| `x_mouth_right` | float64 | 83,922 | 83,737 | -2.2262666, -1.8864969, -1.9397374 |
| `y_mouth_right` | float64 | 83,922 | 83,229 | -56.68729, -57.7791, -57.49693 |
| `z_mouth_right` | float64 | 83,922 | 83,731 | -71.504684, -68.9341, -76.759575 |
| `x_left_shoulder` | float64 | 83,922 | 83,706 | 10.046103, 10.2653, 10.275087 |
| `y_left_shoulder` | float64 | 83,922 | 82,325 | -39.195942, -39.092106, -38.88581 |
| `z_left_shoulder` | float64 | 83,922 | 83,730 | -24.809559, -23.120546, -32.37296 |
| `x_right_shoulder` | float64 | 83,922 | 83,705 | -11.90165, -11.630168, -11.614682 |
| `y_right_shoulder` | float64 | 83,922 | 82,294 | -40.78252, -40.896255, -41.102974 |
| `z_right_shoulder` | float64 | 83,922 | 83,737 | -34.48215, -31.483227, -37.850357 |
| `x_left_elbow` | float64 | 83,922 | 83,715 | 11.512819, 12.119037, 12.093607 |
| `y_left_elbow` | float64 | 83,922 | 83,631 | -16.912388, -16.169744, -16.023012 |
| `z_left_elbow` | float64 | 83,922 | 83,717 | -8.672732, -7.1201406, -16.31424 |
| `x_right_elbow` | float64 | 83,922 | 83,724 | -13.676053, -13.373364, -14.1555805 |
| `y_right_elbow` | float64 | 83,922 | 83,638 | -17.177427, -17.337593, -17.161877 |
| `z_right_elbow` | float64 | 83,922 | 83,717 | -23.767557, -20.365725, -25.606895 |
| `x_left_wrist` | float64 | 83,922 | 83,730 | 15.022108, 15.56796, 16.689487 |
| `y_left_wrist` | float64 | 83,922 | 83,677 | 4.919023, 5.178662, 5.474722 |
| `z_left_wrist` | float64 | 83,922 | 83,712 | -29.24953, -27.32861, -35.1495 |
| `x_right_wrist` | float64 | 83,922 | 83,722 | -16.286884, -16.835918, -18.44547 |
| `y_right_wrist` | float64 | 83,922 | 83,673 | 3.6472044, 3.2155297, 3.7225294 |
| `z_right_wrist` | float64 | 83,922 | 83,727 | -43.682117, -40.478836, -43.184013 |
| `x_left_pinky_1` | float64 | 83,922 | 83,729 | 15.642354, 16.146683, 17.476372 |
| `y_left_pinky_1` | float64 | 83,922 | 83,666 | 11.247596, 11.883275, 12.433371 |
| `z_left_pinky_1` | float64 | 83,922 | 83,732 | -34.830585, -32.973595, -40.404613 |
| `x_right_pinky_1` | float64 | 83,922 | 83,730 | -17.390242, -18.15442, -19.854525 |
| `y_right_pinky_1` | float64 | 83,922 | 83,665 | 9.767575, 8.846813, 9.387528 |
| `z_right_pinky_1` | float64 | 83,922 | 83,729 | -50.869335, -47.663574, -49.43894 |
| `x_left_index_1` | float64 | 83,922 | 83,736 | 14.843432, 15.344484, 16.760984 |
| `y_left_index_1` | float64 | 83,922 | 83,639 | 11.138071, 11.754019, 12.835108 |
| `z_left_index_1` | float64 | 83,922 | 83,710 | -43.70032, -41.76713, -48.772697 |
| `x_right_index_1` | float64 | 83,922 | 83,720 | -16.209095, -17.105679, -19.076092 |
| `y_right_index_1` | float64 | 83,922 | 83,660 | 10.169658, 9.346465, 9.987496 |
| `z_right_index_1` | float64 | 83,922 | 83,726 | -58.742393, -55.632793, -57.664635 |
| `x_left_thumb_2` | float64 | 83,922 | 83,732 | 14.339092, 14.756375, 16.137205 |
| `y_left_thumb_2` | float64 | 83,922 | 83,668 | 8.969725, 9.368257, 10.352235 |
| `z_left_thumb_2` | float64 | 83,922 | 83,735 | -33.377342, -31.395643, -39.022705 |
| `x_right_thumb_2` | float64 | 83,922 | 83,729 | -15.474065, -16.29058, -18.08404 |
| `y_right_thumb_2` | float64 | 83,922 | 83,659 | 8.467219, 7.61815, 8.254533 |
| `z_right_thumb_2` | float64 | 83,922 | 83,737 | -47.36573, -44.241314, -47.016907 |
| `x_left_hip` | float64 | 83,922 | 83,709 | 6.1818705, 6.114988, 6.125658 |
| `y_left_hip` | float64 | 83,922 | 83,765 | 0.2820156, 0.27300814, 0.38944465 |
| `z_left_hip` | float64 | 83,922 | 83,728 | 2.969433, 2.827803, 2.0859509 |
| `x_right_hip` | float64 | 83,922 | 83,690 | -6.1818705, -6.1149745, -6.1256714 |
| `y_right_hip` | float64 | 83,922 | 83,768 | -0.2820024, -0.27300814, -0.38944465 |
| `z_right_hip` | float64 | 83,922 | 83,728 | -2.969433, -2.827803, -2.0859509 |
| `x_left_knee` | float64 | 83,922 | 83,718 | 5.7622557, 5.4485817, 5.4657364 |
| `y_left_knee` | float64 | 83,922 | 83,594 | 35.101257, 34.496147, 34.57939 |
| `z_left_knee` | float64 | 83,922 | 83,741 | -4.042131, -3.7002234, -2.4047718 |
| `x_right_knee` | float64 | 83,922 | 83,723 | -5.3884983, -5.48809, -5.0200486 |
| `y_right_knee` | float64 | 83,922 | 83,585 | 35.342953, 34.81154, 34.286583 |
| `z_right_knee` | float64 | 83,922 | 83,743 | -8.46164, -8.086836, -4.35242 |
| `x_left_ankle` | float64 | 83,922 | 83,734 | 3.6714349, 4.017675, 4.2145643 |
| `y_left_ankle` | float64 | 83,922 | 83,595 | 64.72976, 63.401997, 62.46605 |
| `z_left_ankle` | float64 | 83,922 | 83,730 | 39.8802, 45.288086, 46.772163 |
| `x_right_ankle` | float64 | 83,922 | 83,728 | -5.5517015, -5.329083, -4.929604 |
| `y_right_ankle` | float64 | 83,922 | 83,599 | 63.658203, 61.86257, 61.33722 |
| `z_right_ankle` | float64 | 83,922 | 83,726 | 37.705387, 42.294632, 45.861244 |
| `x_left_heel` | float64 | 83,922 | 83,730 | 2.6492505, 3.092264, 3.2845814 |
| `y_left_heel` | float64 | 83,922 | 83,585 | 68.67856, 66.99291, 65.966125 |
| `z_left_heel` | float64 | 83,922 | 83,726 | 42.49331, 48.48736, 49.983517 |
| `x_right_heel` | float64 | 83,922 | 83,740 | -4.885307, -4.7532754, -4.517086 |
| `y_right_heel` | float64 | 83,922 | 83,615 | 67.51277, 64.96957, 64.51098 |
| `z_right_heel` | float64 | 83,922 | 83,722 | 40.333897, 45.439384, 48.99688 |
| `x_left_foot_index` | float64 | 83,922 | 83,735 | 5.3567114, 5.492989, 5.4337583 |
| `y_left_foot_index` | float64 | 83,922 | 83,567 | 73.93424, 73.17727, 72.199036 |
| `z_left_foot_index` | float64 | 83,922 | 83,742 | 11.78033, 18.108229, 19.192911 |
| `x_right_foot_index` | float64 | 83,922 | 83,725 | -5.852993, -6.0383263, -5.51349 |
| `y_right_foot_index` | float64 | 83,922 | 83,572 | 73.78203, 72.70349, 71.79309 |
| `z_right_foot_index` | float64 | 83,922 | 83,733 | 9.016774, 14.22201, 17.322145 |

---
## xyz_distances.csv

- **Shape:** 83,922 rows × 50 columns
- **File size:** 39.63 MB
- **Missing values:** 0
- **Duplicate rows:** 0

### Columns

| Column | Data Type | Non-Null | Unique | Sample Values |
|--------|-----------|----------|--------|---------------|
| `vid_id` | int64 | 83,922 | 448 | 0, 1, 2 |
| `frame_order` | int64 | 83,922 | 301 | 0, 1, 2 |
| `x_left_shoulder_left_wrist` | float64 | 83,922 | 83,740 | 4.9760056, 5.30266, 6.4144 |
| `y_left_shoulder_left_wrist` | float64 | 83,922 | 83,692 | 44.114964, 44.270767, 44.360535 |
| `z_left_shoulder_left_wrist` | float64 | 83,922 | 83,733 | -4.439972, -4.208063, -2.7765427 |
| `x_right_shoulder_right_wrist` | float64 | 83,922 | 83,705 | -4.385234, -5.2057505, -6.8307886 |
| `y_right_shoulder_right_wrist` | float64 | 83,922 | 83,693 | 44.429726, 44.111786, 44.825504 |
| `z_right_shoulder_right_wrist` | float64 | 83,922 | 83,731 | -9.199966, -8.995609, -5.3336563 |
| `x_left_hip_left_ankle` | float64 | 83,922 | 83,754 | -2.5104356, -2.097313, -1.9110937 |
| `y_left_hip_left_ankle` | float64 | 83,922 | 83,640 | 64.44775, 63.12899, 62.076603 |
| `z_left_hip_left_ankle` | float64 | 83,922 | 83,748 | 36.910767, 42.46028, 44.68621 |
| `x_right_hip_right_ankle` | float64 | 83,922 | 83,750 | 0.6301689, 0.78589153, 1.1960673 |
| `y_right_hip_right_ankle` | float64 | 83,922 | 83,653 | 63.940205, 62.13558, 61.726665 |
| `z_right_hip_right_ankle` | float64 | 83,922 | 83,749 | 40.67482, 45.122437, 47.947197 |
| `x_left_hip_left_wrist` | float64 | 83,922 | 83,745 | 8.840238, 9.452972, 10.563829 |
| `y_left_hip_left_wrist` | float64 | 83,922 | 83,672 | 4.637007, 4.9056535, 5.085277 |
| `z_left_hip_left_wrist` | float64 | 83,922 | 83,733 | -32.218964, -30.156412, -37.23545 |
| `x_right_hip_right_wrist` | float64 | 83,922 | 83,753 | -10.105014, -10.720943, -12.319799 |
| `y_right_hip_right_wrist` | float64 | 83,922 | 83,695 | 3.9292068, 3.4885378, 4.1119742 |
| `z_right_hip_right_wrist` | float64 | 83,922 | 83,735 | -40.712685, -37.65103, -41.09806 |
| `x_left_shoulder_left_ankle` | float64 | 83,922 | 83,736 | -6.3746676, -6.247625, -6.060523 |
| `y_left_shoulder_left_ankle` | float64 | 83,922 | 83,492 | 103.925705, 102.4941, 101.35186 |
| `z_left_shoulder_left_ankle` | float64 | 83,922 | 83,729 | 64.68976, 68.40863, 79.14513 |
| `x_right_shoulder_right_ankle` | float64 | 83,922 | 83,741 | 6.349949, 6.301085, 6.685078 |
| `y_right_shoulder_right_ankle` | float64 | 83,922 | 83,510 | 104.44072, 102.75883, 102.44019 |
| `z_right_shoulder_right_ankle` | float64 | 83,922 | 83,736 | 72.18754, 73.77786, 83.7116 |
| `x_left_hip_right_wrist` | float64 | 83,922 | 83,746 | -22.468754, -22.950907, -24.571129 |
| `y_left_hip_right_wrist` | float64 | 83,922 | 83,688 | 3.3651888, 2.9425216, 3.3330848 |
| `z_left_hip_right_wrist` | float64 | 83,922 | 83,732 | -46.65155, -43.30664, -45.269966 |
| `x_right_hip_left_wrist` | float64 | 83,922 | 83,742 | 21.20398, 21.682934, 22.815159 |
| `y_right_hip_left_wrist` | float64 | 83,922 | 83,671 | 5.2010255, 5.45167, 5.8641667 |
| `z_right_hip_left_wrist` | float64 | 83,922 | 83,712 | -26.280098, -24.500807, -33.063553 |
| `x_left_elbow_right_elbow` | float64 | 83,922 | 83,723 | -25.188873, -25.492401, -26.249187 |
| `y_left_elbow_right_elbow` | float64 | 83,922 | 83,473 | -0.26503944, -1.1678486, -1.1388645 |
| `z_left_elbow_right_elbow` | float64 | 83,922 | 83,743 | -15.094825, -13.2455845, -9.292656 |
| `x_left_knee_right_knee` | float64 | 83,922 | 83,702 | -11.150754, -10.936672, -10.485785 |
| `y_left_knee_right_knee` | float64 | 83,922 | 83,488 | 0.2416954, 0.31539154, -0.29280853 |
| `z_left_knee_right_knee` | float64 | 83,922 | 83,732 | -4.4195094, -4.3866124, -1.947648 |
| `x_left_wrist_right_wrist` | float64 | 83,922 | 83,723 | -31.308992, -32.403877, -35.134956 |
| `y_left_wrist_right_wrist` | float64 | 83,922 | 83,464 | -1.2718186, -1.9631321, -1.7521925 |
| `z_left_wrist_right_wrist` | float64 | 83,922 | 83,739 | -14.432587, -13.150227, -8.034512 |
| `x_left_ankle_right_ankle` | float64 | 83,922 | 83,662 | -9.223137, -9.346758, -9.144169 |
| `y_left_ankle_right_ankle` | float64 | 83,922 | 83,403 | -1.0715561, -1.5394249, -1.12883 |
| `z_left_ankle_right_ankle` | float64 | 83,922 | 83,721 | -2.1748123, -2.993454, -0.9109192 |
| `x_left_hip_avg_left_wrist_left_ankle` | float64 | 83,922 | 83,731 | -3.1649008, -3.6778293, -4.3263683 |
| `y_left_hip_avg_left_wrist_left_ankle` | float64 | 83,922 | 83,741 | -34.542374, -34.017323, -33.58094 |
| `z_left_hip_avg_left_wrist_left_ankle` | float64 | 83,922 | 83,752 | -2.3459013, -6.1519356, -3.72538 |
| `x_right_hip_avg_right_wrist_right_ankle` | float64 | 83,922 | 83,738 | 4.737422, 4.967526, 5.561866 |
| `y_right_hip_avg_right_wrist_right_ankle` | float64 | 83,922 | 83,750 | -33.934704, -32.812057, -32.91932 |
| `z_right_hip_avg_right_wrist_right_ankle` | float64 | 83,922 | 83,740 | 0.018932104, -3.7357008, -3.4245663 |

---
## Class Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| `jumping_jack` | 107 | 23.9% |
| `pull_up` | 101 | 22.5% |
| `push_up` | 99 | 22.1% |
| `situp` | 78 | 17.4% |
| `squat` | 63 | 14.1% |

**Total videos:** 448

---
## Landmarks Analysis

- **Landmark feature columns:** 99
- **Implied landmarks:** 33 (×3 for x, y, z)
- **Visibility columns:** None (not present)
- **Unique video IDs:** 448

### Frames Per Video

- **Mean:** 187.3
- **Std:** 77.2
- **Min:** 14
- **Max:** 301
- **Median:** 185.5

### Landmark Names

1. `left_ankle`
2. `left_ear`
3. `left_elbow`
4. `left_eye`
5. `left_eye_inner`
6. `left_eye_outer`
7. `left_foot_index`
8. `left_heel`
9. `left_hip`
10. `left_index_1`
11. `left_knee`
12. `left_pinky_1`
13. `left_shoulder`
14. `left_thumb_2`
15. `left_wrist`
16. `mouth_left`
17. `mouth_right`
18. `nose`
19. `right_ankle`
20. `right_ear`
21. `right_elbow`
22. `right_eye`
23. `right_eye_inner`
24. `right_eye_outer`
25. `right_foot_index`
26. `right_heel`
27. `right_hip`
28. `right_index_1`
29. `right_knee`
30. `right_pinky_1`
31. `right_shoulder`
32. `right_thumb_2`
33. `right_wrist`

---
## Angles Analysis

- **Angle feature columns:** 7
- **Angle definitions:**
  - `right_elbow_right_shoulder_right_hip`: mean=79.9°, std=42.0°, range=[0.6°, 179.8°]
  - `left_elbow_left_shoulder_left_hip`: mean=79.8°, std=41.4°, range=[0.5°, 179.9°]
  - `right_knee_mid_hip_left_knee`: mean=51.8°, std=29.7°, range=[0.1°, 177.0°]
  - `right_hip_right_knee_right_ankle`: mean=124.9°, std=41.6°, range=[0.5°, 179.9°]
  - `left_hip_left_knee_left_ankle`: mean=123.2°, std=41.7°, range=[1.8°, 179.9°]
  - `right_wrist_right_elbow_right_shoulder`: mean=127.3°, std=28.3°, range=[1.1°, 179.9°]
  - `left_wrist_left_elbow_left_shoulder`: mean=125.4°, std=29.9°, range=[3.0°, 179.7°]

---
## 3D Distances Analysis

- **Distance feature columns:** 16
- **Distance pairs:**
  - `left_shoulder_left_wrist`
  - `right_shoulder_right_wrist`
  - `left_hip_left_ankle`
  - `right_hip_right_ankle`
  - `left_hip_left_wrist`
  - `right_hip_right_wrist`
  - `left_shoulder_left_ankle`
  - `right_shoulder_right_ankle`
  - `left_hip_right_wrist`
  - `right_hip_left_wrist`
  - `left_elbow_right_elbow`
  - `left_knee_right_knee`
  - `left_wrist_right_wrist`
  - `left_ankle_right_ankle`
  - `left_hip_avg_left_wrist_left_ankle`
  - `right_hip_avg_right_wrist_right_ankle`

---
## XYZ Distances Analysis

- **XYZ distance feature columns:** 48
- **Implied distance pairs:** 16 (×3 for x, y, z)

---
## Cross-File Relationships

- All files share `vid_id` and `frame_order` as join keys
- landmarks vid_ids: 448
- angles vid_ids: 448
- distances vid_ids: 448
- xyz_distances vid_ids: 448
- labels vid_ids: 448
- All identical: True
- landmarks rows: 83,922
- angles rows: 83,922
- distances rows: 83,922
- xyz_distances rows: 83,922
- All row counts identical: True

---
## Relevance to Target Exercises

- **Target exercises:** ['bicep_curl', 'push_up', 'shoulder_press', 'squat']
- **Available in Dataset1:** ['jumping_jack', 'pull_up', 'push_up', 'situp', 'squat']
- **Overlap:** ['push_up', 'squat']
- **Missing from Dataset1:** ['bicep_curl', 'shoulder_press']
- **Extra in Dataset1 (not needed):** ['jumping_jack', 'pull_up', 'situp']

> **Conclusion:** Dataset1 only provides `push_up` and `squat` data. It does NOT contain `bicep_curl` or `shoulder_press`. Dataset1 will be used as supplementary data only.