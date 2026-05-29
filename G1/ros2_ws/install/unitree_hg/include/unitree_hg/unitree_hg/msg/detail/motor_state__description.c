// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/MotorState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/motor_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__MotorState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x9f, 0xb0, 0xc7, 0xe5, 0x0c, 0xef, 0x17, 0x69,
      0x03, 0x7c, 0x58, 0x03, 0x04, 0x75, 0x0d, 0xf0,
      0xda, 0x54, 0xb7, 0xa6, 0xa5, 0xfb, 0xfa, 0x92,
      0x88, 0x0f, 0x97, 0xad, 0xd4, 0x94, 0x53, 0x45,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__MotorState__TYPE_NAME[] = "unitree_hg/msg/MotorState";

// Define type names, field names, and default values
static char unitree_hg__msg__MotorState__FIELD_NAME__mode[] = "mode";
static char unitree_hg__msg__MotorState__FIELD_NAME__q[] = "q";
static char unitree_hg__msg__MotorState__FIELD_NAME__dq[] = "dq";
static char unitree_hg__msg__MotorState__FIELD_NAME__ddq[] = "ddq";
static char unitree_hg__msg__MotorState__FIELD_NAME__tau_est[] = "tau_est";
static char unitree_hg__msg__MotorState__FIELD_NAME__temperature[] = "temperature";
static char unitree_hg__msg__MotorState__FIELD_NAME__vol[] = "vol";
static char unitree_hg__msg__MotorState__FIELD_NAME__sensor[] = "sensor";
static char unitree_hg__msg__MotorState__FIELD_NAME__motorstate[] = "motorstate";
static char unitree_hg__msg__MotorState__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__MotorState__FIELDS[] = {
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__q, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__dq, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__ddq, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__tau_est, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__temperature, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__vol, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__sensor, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__motorstate, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__MotorState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
      {unitree_hg__msg__MotorState__FIELDS, 10, 10},
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
  "float32 ddq\n"
  "float32 tau_est\n"
  "\n"
  "int16[2] temperature\n"
  "float32 vol\n"
  "uint32[2] sensor\n"
  "uint32 motorstate\n"
  "uint32[4] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__MotorState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 146, 146},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__MotorState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__MotorState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
