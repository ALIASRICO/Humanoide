// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/SportModeState.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/sport_mode_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__SportModeState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x81, 0x4b, 0x46, 0x92, 0xa9, 0x04, 0xd5, 0x86,
      0xa0, 0xc6, 0xfe, 0x49, 0xce, 0x34, 0x44, 0x80,
      0x43, 0x43, 0x64, 0xd0, 0xfb, 0x41, 0x0d, 0x06,
      0xdf, 0x29, 0x86, 0xa1, 0x6e, 0x79, 0xfc, 0xd4,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/time_spec__functions.h"
#include "unitree_go/msg/detail/imu_state__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__IMUState__EXPECTED_HASH = {1, {
    0x22, 0x67, 0x72, 0x53, 0x1e, 0x06, 0xca, 0x57,
    0x68, 0xda, 0xd7, 0xae, 0x26, 0x42, 0x21, 0x62,
    0x2e, 0x92, 0xba, 0x1d, 0xbc, 0x7f, 0xcd, 0x7f,
    0x80, 0x74, 0x35, 0x1a, 0x23, 0xfe, 0x1c, 0x11,
  }};
static const rosidl_type_hash_t unitree_go__msg__TimeSpec__EXPECTED_HASH = {1, {
    0x0c, 0xac, 0x3f, 0x06, 0x05, 0xaf, 0x32, 0x3a,
    0xdd, 0x43, 0xe1, 0xed, 0x3a, 0xe7, 0xfc, 0x01,
    0xf7, 0xc7, 0x85, 0x7f, 0x41, 0x38, 0x01, 0x70,
    0xb3, 0xea, 0x3a, 0x89, 0x9b, 0x28, 0xcb, 0x76,
  }};
#endif

static char unitree_go__msg__SportModeState__TYPE_NAME[] = "unitree_go/msg/SportModeState";
static char unitree_go__msg__IMUState__TYPE_NAME[] = "unitree_go/msg/IMUState";
static char unitree_go__msg__TimeSpec__TYPE_NAME[] = "unitree_go/msg/TimeSpec";

// Define type names, field names, and default values
static char unitree_go__msg__SportModeState__FIELD_NAME__stamp[] = "stamp";
static char unitree_go__msg__SportModeState__FIELD_NAME__error_code[] = "error_code";
static char unitree_go__msg__SportModeState__FIELD_NAME__imu_state[] = "imu_state";
static char unitree_go__msg__SportModeState__FIELD_NAME__mode[] = "mode";
static char unitree_go__msg__SportModeState__FIELD_NAME__progress[] = "progress";
static char unitree_go__msg__SportModeState__FIELD_NAME__gait_type[] = "gait_type";
static char unitree_go__msg__SportModeState__FIELD_NAME__foot_raise_height[] = "foot_raise_height";
static char unitree_go__msg__SportModeState__FIELD_NAME__position[] = "position";
static char unitree_go__msg__SportModeState__FIELD_NAME__body_height[] = "body_height";
static char unitree_go__msg__SportModeState__FIELD_NAME__velocity[] = "velocity";
static char unitree_go__msg__SportModeState__FIELD_NAME__yaw_speed[] = "yaw_speed";
static char unitree_go__msg__SportModeState__FIELD_NAME__range_obstacle[] = "range_obstacle";
static char unitree_go__msg__SportModeState__FIELD_NAME__foot_force[] = "foot_force";
static char unitree_go__msg__SportModeState__FIELD_NAME__foot_position_body[] = "foot_position_body";
static char unitree_go__msg__SportModeState__FIELD_NAME__foot_speed_body[] = "foot_speed_body";

static rosidl_runtime_c__type_description__Field unitree_go__msg__SportModeState__FIELDS[] = {
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__stamp, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__TimeSpec__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__error_code, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__imu_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__IMUState__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__progress, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__gait_type, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__foot_raise_height, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__position, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__body_height, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__velocity, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__yaw_speed, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__range_obstacle, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__foot_force, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__foot_position_body, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__SportModeState__FIELD_NAME__foot_speed_body, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__SportModeState__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__IMUState__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__TimeSpec__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__SportModeState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__SportModeState__TYPE_NAME, 29, 29},
      {unitree_go__msg__SportModeState__FIELDS, 15, 15},
    },
    {unitree_go__msg__SportModeState__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__IMUState__EXPECTED_HASH, unitree_go__msg__IMUState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__IMUState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_go__msg__TimeSpec__EXPECTED_HASH, unitree_go__msg__TimeSpec__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_go__msg__TimeSpec__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "TimeSpec stamp\n"
  "uint32 error_code\n"
  "IMUState imu_state\n"
  "uint8 mode\n"
  "float32 progress\n"
  "uint8 gait_type\n"
  "float32 foot_raise_height\n"
  "float32[3] position\n"
  "float32 body_height\n"
  "float32[3] velocity\n"
  "float32 yaw_speed\n"
  "float32[4] range_obstacle\n"
  "int16[4] foot_force\n"
  "float32[12] foot_position_body\n"
  "float32[12] foot_speed_body\n"
  "\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__SportModeState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__SportModeState__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 307, 307},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__SportModeState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__SportModeState__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__IMUState__get_individual_type_description_source(NULL);
    sources[2] = *unitree_go__msg__TimeSpec__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
