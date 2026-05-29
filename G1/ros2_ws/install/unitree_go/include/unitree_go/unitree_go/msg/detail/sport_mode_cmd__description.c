// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/SportModeCmd.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/sport_mode_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__SportModeCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x22, 0xc4, 0x2d, 0x22, 0xe7, 0x5a, 0x8d, 0x41,
      0x9f, 0xa6, 0x47, 0x3b, 0x1d, 0x3a, 0xe9, 0x2b,
      0x3f, 0xa7, 0x47, 0x3c, 0xa9, 0xd7, 0xbc, 0x9e,
      0x33, 0x67, 0x85, 0x65, 0x9e, 0x7a, 0xb9, 0x28,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/path_point__functions.h"
#include "unitree_go/msg/detail/bms_cmd__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__BmsCmd__EXPECTED_HASH = {1, {
    0x81, 0x53, 0x10, 0xdf, 0xf4, 0xeb, 0xba, 0x1e,
    0x0d, 0x37, 0x80, 0x2d, 0xfd, 0xc5, 0x6d, 0x4b,
    0x5a, 0x84, 0x97, 0x61, 0xf6, 0x13, 0x95, 0x41,
    0x72, 0xbd, 0xb4, 0x47, 0x6a, 0xed, 0x5a, 0xa2,
  }};
static const rosidl_type_hash_t unitree_go__msg__PathPoint__EXPECTED_HASH = {1, {
    0xc8, 0xbc, 0xdd, 0x0b, 0x29, 0xc2, 0x8f, 0x9e,
    0x85, 0x3f, 0xfa, 0x2f, 0x4d, 0x40, 0x47, 0x18,
    0xc0, 0x58, 0xf4, 0xc0, 0x84, 0xdc, 0x13, 0x73,
    0x75, 0x40, 0xd8, 0x1e, 0xdb, 0x1c, 0xcd, 0x17,
  }};
#endif

static char unitree_go__msg__SportModeCmd__TYPE_NAME[] = "unitree_go/msg/SportModeCmd";
static char unitree_go__msg__BmsCmd__TYPE_NAME[] = "unitree_go/msg/BmsCmd";
static char unitree_go__msg__PathPoint__TYPE_NAME[] = "unitree_go/msg/PathPoint";

// Define type names, field names, and default values
static char unitree_go__msg__SportModeCmd__FIELD_NAME__mode[] = "mode";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__gait_type[] = "gait_type";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__speed_level[] = "speed_level";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__foot_raise_height[] = "foot_raise_height";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__body_height[] = "body_height";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__position[] = "position";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__euler[] = "euler";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__velocity[] = "velocity";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__yaw_speed[] = "yaw_speed";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__bms_cmd[] = "bms_cmd";
static char unitree_go__msg__SportModeCmd__FIELD_NAME__path_point[] = "path_point";

static rosidl_runtime_c__type_description__Field unitree_go__msg__SportModeCmd__FIELDS[] = {
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__gait_type, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__speed_level, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__foot_raise_height, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__body_height, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__position, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__euler, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__velocity, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__yaw_speed, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__bms_cmd, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeCmd__FIELD_NAME__path_point, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_ARRAY,
      30,
      0,
      {unitree_go__msg__PathPoint__TYPE_NAME, 24, 24},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__SportModeCmd__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__TYPE_NAME, 24, 24},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__SportModeCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__SportModeCmd__TYPE_NAME, 27, 27},
      {unitree_go__msg__SportModeCmd__FIELDS, 11, 11},
    },
    {unitree_go__msg__SportModeCmd__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__BmsCmd__EXPECTED_HASH, unitree_go__msg__BmsCmd__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__BmsCmd__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_go__msg__PathPoint__EXPECTED_HASH, unitree_go__msg__PathPoint__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_go__msg__PathPoint__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 mode\n"
  "uint8 gait_type\n"
  "uint8 speed_level\n"
  "float32 foot_raise_height\n"
  "float32 body_height\n"
  "float32[2] position\n"
  "float32[3] euler\n"
  "float32[2] velocity\n"
  "float32 yaw_speed\n"
  "BmsCmd bms_cmd\n"
  "PathPoint[30] path_point\n"
  "\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__SportModeCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__SportModeCmd__TYPE_NAME, 27, 27},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 208, 208},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__SportModeCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__SportModeCmd__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__BmsCmd__get_individual_type_description_source(NULL);
    sources[2] = *unitree_go__msg__PathPoint__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
