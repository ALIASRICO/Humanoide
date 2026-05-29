// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/UwbState.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/uwb_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__UwbState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xd0, 0x2a, 0x3b, 0xf8, 0x33, 0x0a, 0x00, 0x23,
      0x73, 0x28, 0x1a, 0x28, 0x88, 0xa9, 0xea, 0x92,
      0xd6, 0x13, 0x5d, 0x7e, 0xba, 0x55, 0xc9, 0x18,
      0x40, 0x3d, 0xab, 0xc3, 0x8e, 0xdc, 0xe7, 0xf5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__UwbState__TYPE_NAME[] = "unitree_go/msg/UwbState";

// Define type names, field names, and default values
static char unitree_go__msg__UwbState__FIELD_NAME__version[] = "version";
static char unitree_go__msg__UwbState__FIELD_NAME__channel[] = "channel";
static char unitree_go__msg__UwbState__FIELD_NAME__joy_mode[] = "joy_mode";
static char unitree_go__msg__UwbState__FIELD_NAME__orientation_est[] = "orientation_est";
static char unitree_go__msg__UwbState__FIELD_NAME__pitch_est[] = "pitch_est";
static char unitree_go__msg__UwbState__FIELD_NAME__distance_est[] = "distance_est";
static char unitree_go__msg__UwbState__FIELD_NAME__yaw_est[] = "yaw_est";
static char unitree_go__msg__UwbState__FIELD_NAME__tag_roll[] = "tag_roll";
static char unitree_go__msg__UwbState__FIELD_NAME__tag_pitch[] = "tag_pitch";
static char unitree_go__msg__UwbState__FIELD_NAME__tag_yaw[] = "tag_yaw";
static char unitree_go__msg__UwbState__FIELD_NAME__base_roll[] = "base_roll";
static char unitree_go__msg__UwbState__FIELD_NAME__base_pitch[] = "base_pitch";
static char unitree_go__msg__UwbState__FIELD_NAME__base_yaw[] = "base_yaw";
static char unitree_go__msg__UwbState__FIELD_NAME__joystick[] = "joystick";
static char unitree_go__msg__UwbState__FIELD_NAME__error_state[] = "error_state";
static char unitree_go__msg__UwbState__FIELD_NAME__buttons[] = "buttons";
static char unitree_go__msg__UwbState__FIELD_NAME__enabled_from_app[] = "enabled_from_app";

static rosidl_runtime_c__type_description__Field unitree_go__msg__UwbState__FIELDS[] = {
  {
    {unitree_go__msg__UwbState__FIELD_NAME__version, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__channel, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__joy_mode, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__orientation_est, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__pitch_est, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__distance_est, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__yaw_est, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__tag_roll, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__tag_pitch, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__tag_yaw, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__base_roll, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__base_pitch, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__base_yaw, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__joystick, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__error_state, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__buttons, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__UwbState__FIELD_NAME__enabled_from_app, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__UwbState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__UwbState__TYPE_NAME, 23, 23},
      {unitree_go__msg__UwbState__FIELDS, 17, 17},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8[2] version\n"
  "uint8 channel\n"
  "uint8 joy_mode\n"
  "float32 orientation_est\n"
  "float32 pitch_est\n"
  "float32 distance_est\n"
  "float32 yaw_est\n"
  "float32 tag_roll\n"
  "float32 tag_pitch\n"
  "float32 tag_yaw\n"
  "float32 base_roll\n"
  "float32 base_pitch\n"
  "float32 base_yaw\n"
  "float32[2] joystick\n"
  "uint8 error_state\n"
  "uint8 buttons\n"
  "uint8 enabled_from_app\n"
  "\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__UwbState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__UwbState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 307, 307},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__UwbState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__UwbState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
