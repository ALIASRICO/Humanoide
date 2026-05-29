"""Helper para activar omni.isaac.ros2_bridge programáticamente.

Uso:
    from ros2_bridge_extension import enable_ros2_bridge
    enable_ros2_bridge()

Llamar DESPUÉS de SimulationApp() y ANTES de crear el env de Isaac Lab.
"""
from __future__ import annotations


def enable_ros2_bridge():
    """Habilita la extensión oficial omni.isaac.ros2_bridge.

    Verifica que ROS2 esté en el environment (LD_LIBRARY_PATH).
    """
    import os
    if "/opt/ros/humble/lib" not in os.environ.get("LD_LIBRARY_PATH", ""):
        raise RuntimeError(
            "ROS2 no está en el environment. `source /opt/ros/humble/setup.bash` "
            "antes de lanzar Isaac Sim."
        )

    import omni.kit.app
    ext_manager = omni.kit.app.get_app().get_extension_manager()

    # Probar varias variantes (el nombre cambia entre versiones)
    candidates = [
        "omni.isaac.ros2_bridge",
        "isaacsim.ros2.bridge",
    ]
    for name in candidates:
        try:
            ext_manager.set_extension_enabled_immediate(name, True)
            print(f"[INFO] {name} habilitado.")
            return name
        except Exception:
            continue
    raise RuntimeError("No se encontró la extensión ROS2 bridge en este Isaac Sim.")


def setup_action_graph_publish_clock(prim_path: str = "/World/ROS_Clock"):
    """Crea un Action Graph que publica /clock.

    Útil para que todos los nodos ROS2 con use_sim_time=true sigan el reloj.
    """
    import omni.graph.core as og
    from omni.isaac.core.utils.prims import is_prim_path_valid, delete_prim

    if is_prim_path_valid(prim_path):
        delete_prim(prim_path)

    keys = og.Controller.Keys
    og.Controller.edit(
        {"graph_path": prim_path, "evaluator_name": "execution"},
        {
            keys.CREATE_NODES: [
                ("OnTick", "omni.graph.action.OnPlaybackTick"),
                ("PublishClock", "omni.isaac.ros2_bridge.ROS2PublishClock"),
                ("ReadSimTime",  "omni.isaac.core_nodes.IsaacReadSimulationTime"),
            ],
            keys.CONNECT: [
                ("OnTick.outputs:tick", "PublishClock.inputs:execIn"),
                ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
            ],
        },
    )
    print(f"[INFO] Action Graph /clock creado en {prim_path}")
