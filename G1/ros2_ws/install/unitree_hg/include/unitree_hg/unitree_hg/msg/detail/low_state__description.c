// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/LowState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/low_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__LowState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xae, 0xe6, 0xc5, 0xbd, 0x4b, 0x4d, 0x2e, 0xec,
      0xa8, 0x54, 0xbf, 0x47, 0xe3, 0x2e, 0x4e, 0x3d,
      0x34, 0xc4, 0x7c, 0x2c, 0xaf, 0xa0, 0x5c, 0x08,
      0xb6, 0xb0, 0xfa, 0x4b, 0xc5, 0x1c, 0x6b, 0x3a,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_hg/msg/detail/imu_state__functions.h"
#include "unitree_hg/msg/detail/motor_state__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_hg__msg__IMUState__EXPECTED_HASH = {1, {
    0x6f, 0xbb, 0xa1, 0xa6, 0x72, 0x36, 0x0b, 0xf4,
    0x1e, 0x43, 0x93, 0xad, 0x73, 0xd2, 0x47, 0x03,
    0x6f, 0xd8, 0x02, 0xd0, 0x8a, 0xdf, 0xb4, 0x36,
    0xd0, 0xc9, 0x9a, 0x2a, 0x7b, 0x3c, 0xee, 0xc2,
  }};
static const rosidl_type_hash_t unitree_hg__msg__MotorState__EXPECTED_HASH = {1, {
    0x9f, 0xb0, 0xc7, 0xe5, 0x0c, 0xef, 0x17, 0x69,
    0x03, 0x7c, 0x58, 0x03, 0x04, 0x75, 0x0d, 0xf0,
    0xda, 0x54, 0xb7, 0xa6, 0xa5, 0xfb, 0xfa, 0x92,
    0x88, 0x0f, 0x97, 0xad, 0xd4, 0x94, 0x53, 0x45,
  }};
#endif

static char unitree_hg__msg__LowState__TYPE_NAME[] = "unitree_hg/msg/LowState";
static char unitree_hg__msg__IMUState__TYPE_NAME[] = "unitree_hg/msg/IMUState";
static char unitree_hg__msg__MotorState__TYPE_NAME[] = "unitree_hg/msg/MotorState";

// Define type names, field names, and default values
static char unitree_hg__msg__LowState__FIELD_NAME__version[] = "version";
static char unitree_hg__msg__LowState__FIELD_NAME__mode_pr[] = "mode_pr";
static char unitree_hg__msg__LowState__FIELD_NAME__mode_machine[] = "mode_machine";
static char unitree_hg__msg__LowState__FIELD_NAME__tick[] = "tick";
static char unitree_hg__msg__LowState__FIELD_NAME__imu_state[] = "imu_state";
static char unitree_hg__msg__LowState__FIELD_NAME__motor_state[] = "motor_state";
static char unitree_hg__msg__LowState__FIELD_NAME__wireless_remote[] = "wireless_remote";
static char unitree_hg__msg__LowState__FIELD_NAME__reserve[] = "reserve";
static char unitree_hg__msg__LowState__FIELD_NAME__crc[] = "crc";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__LowState__FIELDS[] = {
  {
    {unitree_hg__msg__LowState__FIELD_NAME__version, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__mode_pr, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__mode_machine, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__tick, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__imu_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__motor_state, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_ARRAY,
      35,
      0,
      {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__wireless_remote, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      40,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowState__FIELD_NAME__crc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_hg__msg__LowState__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__LowState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__LowState__TYPE_NAME, 23, 23},
      {unitree_hg__msg__LowState__FIELDS, 9, 9},
    },
    {unitree_hg__msg__LowState__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_hg__msg__IMUState__EXPECTED_HASH, unitree_hg__msg__IMUState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_hg__msg__IMUState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_hg__msg__MotorState__EXPECTED_HASH, unitree_hg__msg__MotorState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_hg__msg__MotorState__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint32[2] version\n"
  "uint8 mode_pr\n"
  "uint8 mode_machine\n"
  "uint32 tick\n"
  "IMUState imu_state\n"
  "MotorState[35] motor_state\n"
  "uint8[40] wireless_remote\n"
  "uint32[4] reserve\n"
  "uint32 crc";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__LowState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__LowState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 163, 163},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__LowState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__LowState__get_individual_type_description_source(NULL),
    sources[1] = *unitree_hg__msg__IMUState__get_individual_type_description_source(NULL);
    sources[2] = *unitree_hg__msg__MotorState__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
