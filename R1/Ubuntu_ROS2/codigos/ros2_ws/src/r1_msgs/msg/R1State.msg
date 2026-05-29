std_msgs/Header header

sensor_msgs/JointState joints
sensor_msgs/Imu imu

geometry_msgs/Pose root_pose
geometry_msgs/Twist root_vel

# True por pie en contacto con el suelo
bool[] foot_contact

float32 base_height

# FSM
uint8 FSM_POWER_ON = 0
uint8 FSM_STANDBY  = 1
uint8 FSM_READY    = 2
uint8 FSM_STANDING = 3
uint8 FSM_WALKING  = 4
uint8 FSM_FALLING  = 5
uint8 FSM_ESTOP    = 6
uint8 fsm_state

# Estado del último ONNX run
float32 inference_rate_hz
bool estopped
