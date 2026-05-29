# Imitation Learning G1 — LeRobot Pipeline

Pipeline para entrenar políticas de imitación (ACT, Diffusion, Pi0, Gr00t)
con datos recolectados del robot G1.

Fuente: https://github.com/unitreerobotics/unitree_lerobot

---

## Flujo completo

```
Teleoperación          Conversión          Entrenamiento         Evaluación
(grabar episodios) → (formato LeRobot) → (ACT / Diffusion) → (eval_g1.py)
```

---

## Archivos

| Archivo | Descripción |
|---|---|
| `eval_g1.py` | Ejecutar política entrenada en el robot real |
| `replay_robot.py` | Reproducir episodio grabado en el robot |
| `data_editor_EN.py` | GUI para recortar/limpiar episodios (PyQt5) |
| `utils/convert_unitree_json_to_lerobot.py` | Convertir datos JSON a formato LeRobot |
| `utils/convert_lerobot_to_h5.py` | Convertir LeRobot a HDF5 |
| `utils/constants.py` | Definiciones de joints G1 para el dataset |

---

## Instalar LeRobot

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
pip install lerobot
```

O desde fuente (para acceso a scripts de entrenamiento):
```bash
git clone https://github.com/huggingface/lerobot
cd lerobot && pip install -e .
```

---

## 1. Convertir episodios grabados a formato LeRobot

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
cd /home/udc/Unitree_G1

python codigos/imitacion/utils/convert_unitree_json_to_lerobot.py \
    --input dataset/pick_cup \
    --output dataset/pick_cup_lerobot \
    --fps 30
```

---

## 2. Editar episodios (GUI)

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
pip install pyqt5
python codigos/imitacion/data_editor_EN.py
```

Permite recortar episodios, eliminar frames ruidosos, y verificar calidad.

---

## 3. Entrenar política (ACT recomendado para manipulación)

```bash
# Requiere lerobot instalado
cd lerobot
python lerobot/scripts/train.py \
    --policy.type=act \
    --dataset.repo_id=local/pick_cup \
    --dataset.root=/home/udc/Unitree_G1/dataset/pick_cup_lerobot \
    --output_dir=/home/udc/Unitree_G1/politicas/imitacion/pick_cup_act
```

---

## 4. Evaluar en robot real

```bash
conda activate /home/udc/Unitree_G1/envs/g1_udc
export CYCLONEDDS_HOME=/home/udc/Unitree_G1/humanoide/cyclonedds_install
cd /home/udc/Unitree_G1

python codigos/imitacion/eval_g1.py \
    --policy politicas/imitacion/pick_cup_act \
    --robot_interface enp7s0
```

---

## Notas sobre el robot G1

- **Arms**: joints 15-28 (L_arm[15-21], R_arm[22-28])
- **Hands**: Unitree Dex3-1 (14 DOF, opcional)
- **Cámaras**: cabeza (front) y muñecas (opcional)
- **Frecuencia de control**: 30 Hz recomendado para ACT
