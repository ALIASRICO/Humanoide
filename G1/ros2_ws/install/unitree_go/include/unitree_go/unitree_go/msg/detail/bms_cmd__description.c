// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/BmsCmd.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/bms_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__BmsCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x81, 0x53, 0x10, 0xdf, 0xf4, 0xeb, 0xba, 0x1e,
      0x0d, 0x37, 0x80, 0x2d, 0xfd, 0xc5, 0x6d, 0x4b,
      0x5a, 0x84, 0x97, 0x61, 0xf6, 0x13, 0x95, 0x41,
      0x72, 0xbd, 0xb4, 0x47, 0x6a, 0xed, 0x5a, 0xa2,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__BmsCmd__TYPE_NAME[] = "unitree_go/msg/BmsCmd";

// Define type names, field names, and default values
static char unitree_go__msg__BmsCmd__FIELD_NAME__off[] = "off";
static char unitree_go__msg__BmsCmd__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_go__msg__BmsCmd__FIELDS[] = {
  {
    {unitree_go__msg__BmsCmd__FIELD_NAME__off, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsCmd__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__BmsCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
      {unitree_go__msg__BmsCmd__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 off\n"
  "uint8[3] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__BmsCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 26, 26},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__BmsCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__BmsCmd__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
