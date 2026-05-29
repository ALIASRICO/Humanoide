std_msgs/Header header

# Comando absoluto en world frame
geometry_msgs/Pose2D target_pose

# Velocidad máxima permitida (m/s). 0 = sin tope.
float32 max_speed

# Skill hint para la política madre / FSM
# "auto": decide la madre / FSM
# "stand": forzar standing
# "walk": forzar locomotion
# "stair": forzar stair-climbing
string skill_hint
