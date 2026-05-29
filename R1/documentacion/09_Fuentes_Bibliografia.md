# 09 — Fuentes y bibliografía de la investigación

> Tomado de `space_r1/fuentes.md` y enriquecido con notas de cómo cada paper se aplicó al proyecto.

---

## 1. Learning Agile Locomotion on Risky Terrains

- **URL**: <https://revistas.udistrital.edu.co/index.php/Tecnura/article/view/8152/10423>
- **Aporta**:
  - Curriculum de terrenos progresivos (plano → rugoso → escaleras → gaps).
  - Importancia del *symmetric data augmentation* para evitar sesgos direccionales.
  - Recompensa basada en alcanzar un punto de meta vs. mantener velocidad fija.

**Aplicado en**: [doc 05](./05_Path_Coordenadas_Velocidad.md) §3 (mirror augmentation), [doc 06](./06_Playground_Terrenos.md) §1 (curriculum por niveles).

---

## 2. Técnicas de control para el balance de un robot bípedo (Estado del arte)

- **URL**: <https://www.research-collection.ethz.ch/server/api/core/bitstreams/3cf7e77b-ec58-40e2-a0db-987cbf307a01/content>
- **Aporta**:
  - Estrategias jerárquicas de equilibrio: **tobillo → cadera → paso**.
  - Modelos LIPM (Linear Inverted Pendulum) y ZMP (Zero Moment Point) como baselines clásicos.
  - Justifica que la recompensa de **CoM sobre soporte** es un buen *shaping* para PPO.

**Aplicado en**: [doc 02](./02_Crear_Politica_Basica.md) §4 (rewards `rew_com_lateral_balance`, `rew_feet_separation`, `rew_recovery`), [doc 04](./04_Fine_Tuning.md) §3 (curriculum de etapas: estática → activa → push → stepping).

---

## 3. Advanced Skills by Learning Locomotion and Local Navigation End-to-End

- **URL**: <https://arxiv.org/pdf/2209.12827>
- **Aporta**:
  - Política end-to-end que combina locomoción + navegación local.
  - Formulación de comandos por **coordenadas de meta** (en lugar de velocidad).
  - Heightmap como input para adaptación a terreno.
  - Muestreo de targets en disco polar uniforme [1m, 5m].

**Aplicado en**: [doc 05](./05_Path_Coordenadas_Velocidad.md) §1, §2, §7 — la base teórica del WASD por coordenadas.

---

## 4. Zero-Shot Whole-Body Humanoid Control via Behavioral Foundation Models

- **URL**: <https://arxiv.org/pdf/2504.11054>
- **Aporta**:
  - Pre-entrenamiento de un modelo *foundation* que genera políticas zero-shot.
  - Cómo escalar HRL con sub-políticas como expertos.

**Aplicado en**: [doc 03](./03_Politica_Padre_Jerarquica.md) §1 (BFM como alternativa avanzada al HRL clásico).

---

## 5. Otras fuentes implícitas usadas en el repo

| Tema | Referencia |
|-----|-----------|
| Isaac Lab Direct Workflow | <https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.envs.html#direct-workflow> |
| RSL-RL PPO | <https://github.com/leggedrobotics/rsl_rl> |
| SKRL PPO | <https://skrl.readthedocs.io/en/latest/api/agents/ppo.html> |
| Curriculum terrains | `IsaacLab/source/isaaclab/isaaclab/terrains/` |
| Domain Randomization | <https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.envs.mdp.events.html> |

---

## 6. Cómo seguir leyendo

Recomendaciones por temas:

- **HRL clásico**: *FeUdal Networks* (Vezhnevets et al. 2017), *Options Framework* (Sutton 1999).
- **Push recovery**: *Push Recovery Strategies for Humanoid Robots* (Stephens 2007).
- **Sim2real**: *Domain Randomization for Sim2Real Transfer* (Tobin et al. 2017), *RMA: Rapid Motor Adaptation* (Kumar et al. 2021).
- **Locomotion en cuadrúpedos** (los principios trasladan a bípedos): *Learning to Walk in Minutes Using Massively Parallel Deep RL* (Rudin et al. 2022).

Próximo → [10_Correcciones_Aplicadas.md](./10_Correcciones_Aplicadas.md).
