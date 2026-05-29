// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/LowCmd.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/low_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__LowCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xb0, 0xee, 0xc4, 0x77, 0x8d, 0xb3, 0xad, 0x67,
      0xff, 0xad, 0xe3, 0x28, 0xb0, 0x63, 0xbe, 0xa7,
      0x00, 0xbd, 0x15, 0x58, 0xf3, 0xf3, 0x59, 0xea,
      0x5e, 0x4c, 0x86, 0xe3, 0xc3, 0xf2, 0x5b, 0xc5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_hg/msg/detail/motor_cmd__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_hg__msg__MotorCmd__EXPECTED_HASH = {1, {
    0xb4, 0x74, 0x68, 0x41, 0x3c, 0x70, 0x37, 0xd0,
    0xe2, 0xc0, 0x22, 0x7f, 0xce, 0xd0, 0x4b, 0x91,
    0x22, 0x4c, 0xc1, 0x65, 0xe5, 0xbe, 0xfe, 0x2b,
    0x8c, 0xef, 0xac, 0xbe, 0x08, 0x39, 0x13, 0x29,
  }};
#endif

static char unitree_hg__msg__LowCmd__TYPE_NAME[] = "unitree_hg/msg/LowCmd";
static char unitree_hg__msg__MotorCmd__TYPE_NAME[] = "unitree_hg/msg/MotorCmd";

// Define type names, field names, and default values
static char unitree_hg__msg__LowCmd__FIELD_NAME__mode_pr[] = "mode_pr";
static char unitree_hg__msg__LowCmd__FIELD_NAME__mode_machine[] = "mode_machine";
static char unitree_hg__msg__LowCmd__FIELD_NAME__motor_cmd[] = "motor_cmd";
static char unitree_hg__msg__LowCmd__FIELD_NAME__reserve[] = "reserve";
static char unitree_hg__msg__LowCmd__FIELD_NAME__crc[] = "crc";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__LowCmd__FIELDS[] = {
  {
    {unitree_hg__msg__LowCmd__FIELD_NAME__mode_pr, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowCmd__FIELD_NAME__mode_machine, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowCmd__FIELD_NAME__motor_cmd, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_ARRAY,
      35,
      0,
      {unitree_hg__msg__MotorCmd__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowCmd__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__LowCmd__FIELD_NAME__crc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_hg__msg__LowCmd__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_hg__msg__MotorCmd__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__LowCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__LowCmd__TYPE_NAME, 21, 21},
      {unitree_hg__msg__LowCmd__FIELDS, 5, 5},
    },
    {unitree_hg__msg__LowCmd__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_hg__msg__MotorCmd__EXPECTED_HASH, unitree_hg__msg__MotorCmd__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_hg__msg__MotorCmd__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 mode_pr\n"
  "uint8 mode_machine\n"
  "\n"
  "MotorCmd[35] motor_cmd\n"
  "\n"
  "uint32[4] reserve\n"
  "uint32 crc";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__LowCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__LowCmd__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 86, 86},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__LowCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__LowCmd__get_individual_type_description_source(NULL),
    sources[1] = *unitree_hg__msg__MotorCmd__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
