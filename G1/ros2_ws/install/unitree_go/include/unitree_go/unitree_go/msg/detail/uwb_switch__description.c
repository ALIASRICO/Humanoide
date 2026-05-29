// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/UwbSwitch.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/uwb_switch__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__UwbSwitch__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xde, 0x3a, 0x33, 0x0c, 0x27, 0xe9, 0xa4, 0x4e,
      0xb3, 0xa7, 0xdc, 0xf3, 0x54, 0x7d, 0x97, 0xfd,
      0xaf, 0xb7, 0x42, 0x30, 0xbf, 0x67, 0x9e, 0x6f,
      0x04, 0xe4, 0x56, 0x39, 0x35, 0xa6, 0xa2, 0x70,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__UwbSwitch__TYPE_NAME[] = "unitree_go/msg/UwbSwitch";

// Define type names, field names, and default values
static char unitree_go__msg__UwbSwitch__FIELD_NAME__enabled[] = "enabled";

static rosidl_runtime_c__type_description__Field unitree_go__msg__UwbSwitch__FIELDS[] = {
  {
    {unitree_go__msg__UwbSwitch__FIELD_NAME__enabled, 7, 7},
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
unitree_go__msg__UwbSwitch__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__UwbSwitch__TYPE_NAME, 24, 24},
      {unitree_go__msg__UwbSwitch__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 enabled";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__UwbSwitch__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__UwbSwitch__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 13, 13},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__UwbSwitch__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__UwbSwitch__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
