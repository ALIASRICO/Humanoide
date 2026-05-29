// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/LidarState.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/lidar_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__LidarState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x3a, 0x14, 0x05, 0xd7, 0x47, 0xc5, 0x1d, 0x6b,
      0x5c, 0xf5, 0x48, 0xee, 0x67, 0xbc, 0x7b, 0x63,
      0xd5, 0x4b, 0x71, 0x67, 0x3a, 0x54, 0x36, 0x5f,
      0xd6, 0x7d, 0x6d, 0x09, 0xb7, 0x59, 0x9d, 0x18,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__LidarState__TYPE_NAME[] = "unitree_go/msg/LidarState";

// Define type names, field names, and default values
static char unitree_go__msg__LidarState__FIELD_NAME__stamp[] = "stamp";
static char unitree_go__msg__LidarState__FIELD_NAME__firmware_version[] = "firmware_version";
static char unitree_go__msg__LidarState__FIELD_NAME__software_version[] = "software_version";
static char unitree_go__msg__LidarState__FIELD_NAME__sdk_version[] = "sdk_version";
static char unitree_go__msg__LidarState__FIELD_NAME__sys_rotation_speed[] = "sys_rotation_speed";
static char unitree_go__msg__LidarState__FIELD_NAME__com_rotation_speed[] = "com_rotation_speed";
static char unitree_go__msg__LidarState__FIELD_NAME__error_state[] = "error_state";
static char unitree_go__msg__LidarState__FIELD_NAME__cloud_frequency[] = "cloud_frequency";
static char unitree_go__msg__LidarState__FIELD_NAME__cloud_packet_loss_rate[] = "cloud_packet_loss_rate";
static char unitree_go__msg__LidarState__FIELD_NAME__cloud_size[] = "cloud_size";
static char unitree_go__msg__LidarState__FIELD_NAME__cloud_scan_num[] = "cloud_scan_num";
static char unitree_go__msg__LidarState__FIELD_NAME__imu_frequency[] = "imu_frequency";
static char unitree_go__msg__LidarState__FIELD_NAME__imu_packet_loss_rate[] = "imu_packet_loss_rate";
static char unitree_go__msg__LidarState__FIELD_NAME__imu_rpy[] = "imu_rpy";
static char unitree_go__msg__LidarState__FIELD_NAME__serial_recv_stamp[] = "serial_recv_stamp";
static char unitree_go__msg__LidarState__FIELD_NAME__serial_buffer_size[] = "serial_buffer_size";
static char unitree_go__msg__LidarState__FIELD_NAME__serial_buffer_read[] = "serial_buffer_read";

static rosidl_runtime_c__type_description__Field unitree_go__msg__LidarState__FIELDS[] = {
  {
    {unitree_go__msg__LidarState__FIELD_NAME__stamp, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__firmware_version, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__software_version, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__sdk_version, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__sys_rotation_speed, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__com_rotation_speed, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__error_state, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__cloud_frequency, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__cloud_packet_loss_rate, 22, 22},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__cloud_size, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__cloud_scan_num, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__imu_frequency, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__imu_packet_loss_rate, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__imu_rpy, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__serial_recv_stamp, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__serial_buffer_size, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LidarState__FIELD_NAME__serial_buffer_read, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__LidarState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__LidarState__TYPE_NAME, 25, 25},
      {unitree_go__msg__LidarState__FIELDS, 17, 17},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float64 stamp\n"
  "string firmware_version\n"
  "string software_version\n"
  "string sdk_version\n"
  "float32 sys_rotation_speed\n"
  "float32 com_rotation_speed\n"
  "uint8 error_state\n"
  "float32 cloud_frequency\n"
  "float32 cloud_packet_loss_rate\n"
  "uint32 cloud_size\n"
  "uint32 cloud_scan_num\n"
  "float32 imu_frequency\n"
  "float32 imu_packet_loss_rate\n"
  "float32[3] imu_rpy\n"
  "float64 serial_recv_stamp\n"
  "uint32 serial_buffer_size\n"
  "uint32 serial_buffer_read";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__LidarState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__LidarState__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 396, 396},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__LidarState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__LidarState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
