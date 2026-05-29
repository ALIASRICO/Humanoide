// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/MotorCmds.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/motor_cmds__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__MotorCmds__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x42, 0x47, 0x7c, 0x00, 0xfd, 0x1a, 0x43, 0x90,
      0x9a, 0xdb, 0x05, 0xac, 0x60, 0x47, 0x91, 0xf2,
      0x30, 0x53, 0x6f, 0x7f, 0x4d, 0x55, 0x8a, 0xab,
      0xb9, 0xc1, 0x43, 0x3a, 0xcc, 0x0c, 0xb3, 0x9b,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/motor_cmd__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__MotorCmd__EXPECTED_HASH = {1, {
    0x45, 0x81, 0xf1, 0x8a, 0x3b, 0xf5, 0x8b, 0xaa,
    0xd0, 0x4f, 0x12, 0xf5, 0x17, 0x47, 0xf2, 0xdd,
    0x38, 0x8f, 0x64, 0xaa, 0x2a, 0xc9, 0x97, 0xd1,
    0xd6, 0x47, 0x77, 0x56, 0x3c, 0x62, 0x7f, 0xbf,
  }};
#endif

static char unitree_go__msg__MotorCmds__TYPE_NAME[] = "unitree_go/msg/MotorCmds";
static char unitree_go__msg__MotorCmd__TYPE_NAME[] = "unitree_go/msg/MotorCmd";

// Define type names, field names, and default values
static char unitree_go__msg__MotorCmds__FIELD_NAME__cmds[] = "cmds";

static rosidl_runtime_c__type_description__Field unitree_go__msg__MotorCmds__FIELDS[] = {
  {
    {unitree_go__msg__MotorCmds__FIELD_NAME__cmds, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__MotorCmds__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__MotorCmds__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__MotorCmds__TYPE_NAME, 24, 24},
      {unitree_go__msg__MotorCmds__FIELDS, 1, 1},
    },
    {unitree_go__msg__MotorCmds__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__MotorCmd__EXPECTED_HASH, unitree_go__msg__MotorCmd__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__MotorCmd__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "MotorCmd[] cmds";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__MotorCmds__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__MotorCmds__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 15, 15},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__MotorCmds__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__MotorCmds__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__MotorCmd__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
