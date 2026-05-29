// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/MotorCmd.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/motor_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__MotorCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xb4, 0x74, 0x68, 0x41, 0x3c, 0x70, 0x37, 0xd0,
      0xe2, 0xc0, 0x22, 0x7f, 0xce, 0xd0, 0x4b, 0x91,
      0x22, 0x4c, 0xc1, 0x65, 0xe5, 0xbe, 0xfe, 0x2b,
      0x8c, 0xef, 0xac, 0xbe, 0x08, 0x39, 0x13, 0x29,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__MotorCmd__TYPE_NAME[] = "unitree_hg/msg/MotorCmd";

// Define type names, field names, and default values
static char unitree_hg__msg__MotorCmd__FIELD_NAME__mode[] = "mode";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__q[] = "q";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__dq[] = "dq";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__tau[] = "tau";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__kp[] = "kp";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__kd[] = "kd";
static char unitree_hg__msg__MotorCmd__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__MotorCmd__FIELDS[] = {
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__q, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__dq, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__tau, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__kp, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__kd, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorCmd__FIELD_NAME__reserve, 7, 7},
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
unitree_hg__msg__MotorCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__MotorCmd__TYPE_NAME, 23, 23},
      {unitree_hg__msg__MotorCmd__FIELDS, 7, 7},
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
  "uint32 reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__MotorCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__MotorCmd__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 80, 80},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__MotorCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__MotorCmd__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
