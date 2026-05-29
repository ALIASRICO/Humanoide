// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/MotorStates.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/motor_states__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__MotorStates__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x04, 0x51, 0x33, 0x6d, 0x1b, 0x20, 0x3b, 0x1f,
      0xc0, 0xe3, 0x78, 0xd8, 0xa8, 0xe2, 0xf0, 0x4a,
      0x95, 0xa8, 0x34, 0x6d, 0xcf, 0x98, 0x8f, 0x0b,
      0xb8, 0x4a, 0xc4, 0xff, 0x7e, 0xe5, 0x08, 0xd6,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/motor_state__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__MotorState__EXPECTED_HASH = {1, {
    0x86, 0xfb, 0x56, 0xa4, 0xf6, 0xbe, 0xbc, 0xba,
    0x85, 0x4e, 0x9b, 0x51, 0x02, 0x25, 0xe6, 0x66,
    0x6e, 0xf4, 0x6c, 0xf4, 0xea, 0x13, 0x35, 0x58,
    0x70, 0xc2, 0xdd, 0x3c, 0x34, 0x78, 0xa8, 0x8c,
  }};
#endif

static char unitree_go__msg__MotorStates__TYPE_NAME[] = "unitree_go/msg/MotorStates";
static char unitree_go__msg__MotorState__TYPE_NAME[] = "unitree_go/msg/MotorState";

// Define type names, field names, and default values
static char unitree_go__msg__MotorStates__FIELD_NAME__states[] = "states";

static rosidl_runtime_c__type_description__Field unitree_go__msg__MotorStates__FIELDS[] = {
  {
    {unitree_go__msg__MotorStates__FIELD_NAME__states, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {unitree_go__msg__MotorState__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__MotorStates__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__MotorState__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__MotorStates__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__MotorStates__TYPE_NAME, 26, 26},
      {unitree_go__msg__MotorStates__FIELDS, 1, 1},
    },
    {unitree_go__msg__MotorStates__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__MotorState__EXPECTED_HASH, unitree_go__msg__MotorState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__MotorState__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "MotorState[] states";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__MotorStates__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__MotorStates__TYPE_NAME, 26, 26},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 19, 19},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__MotorStates__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__MotorStates__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__MotorState__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
