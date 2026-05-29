#!/usr/bin/env python3
"""
Lanzador del MuJoCo SDK Bridge para G1.
Ejecutar desde la raíz del repo: python simulacion/sdk_bridge/run_g1_bridge.py
"""
import sys
import os

# Asegurar que el bridge encuentra sus módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Usar config G1 en lugar del config genérico
import importlib
import config_g1 as config
sys.modules['config'] = config

# Lanzar el simulador
exec(open(os.path.join(os.path.dirname(__file__), 'unitree_mujoco.py')).read())
