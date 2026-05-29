// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/motor_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__MotorCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x45, 0x81, 0xf1, 0x8a, 0x3b, 0xf5, 0x8b, 0xaa,
      0xd0, 0x4f, 0x12, 0xf5, 0x17, 0x47, 0xf2, 0xdd,
      0x38, 0x8f, 0x64, 0xaa, 0x2a, 0xc9, 0x97, 0xd1,
      0xd6, 0x47, 0x77, 0x56, 0x3c, 0x62, 0x7f, 0xbf,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__MotorCmd__TYPE_NAME[] = "unitree_go/msg/MotorCmd";

// Define type names, field names, and default values
static char unitree_go__msg__MotorCmd__FIELD_NAME__mode[] = "mode";
static char unitree_go__msg__MotorCmd__FIELD_NAME__q[] = "q";
static char unitree_go__msg__MotorCmd__FIELD_NAME__dq[] = "dq";
static char unitree_go__msg__MotorCmd__FIELD_NAME__tau[] = "tau";
static char unitree_go__msg__MotorCmd__FIELD_NAME__kp[] = "kp";
static char unitree_go__msg__MotorCmd__FIELD_NAME__kd[] = "kd";
static char unitree_go__msg__MotorCmd__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_go__msg__MotorCmd__FIELDS[] = {
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__q, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__dq, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__tau, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__kp, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__kd, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__MotorCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
      {unitree_go__msg__MotorCmd__FIELDS, 7, 7},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 mode\n"
  "float32 q\n"
  "float32 dq\n"
  "float32 tau\n"
  "float32 kp\n"
  "float32 kd\n"
  "uint32[3] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__MotorCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 83, 83},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__MotorCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__MotorCmd__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
