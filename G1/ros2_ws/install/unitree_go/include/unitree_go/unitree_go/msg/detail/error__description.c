// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/Error.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/error__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__Error__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x7b, 0x40, 0xe6, 0x33, 0x03, 0xd9, 0x09, 0x21,
      0x53, 0xa3, 0x91, 0x4b, 0xb1, 0x36, 0xec, 0xee,
      0x44, 0xba, 0x37, 0xd8, 0xb8, 0x27, 0xb1, 0x1b,
      0x14, 0x24, 0x44, 0xed, 0xa9, 0xbc, 0x94, 0x50,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__Error__TYPE_NAME[] = "unitree_go/msg/Error";

// Define type names, field names, and default values
static char unitree_go__msg__Error__FIELD_NAME__source[] = "source";
static char unitree_go__msg__Error__FIELD_NAME__state[] = "state";

static rosidl_runtime_c__type_description__Field unitree_go__msg__Error__FIELDS[] = {
  {
    {unitree_go__msg__Error__FIELD_NAME__source, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Error__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__Error__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__Error__TYPE_NAME, 20, 20},
      {unitree_go__msg__Error__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint32 source\n"
  "uint32 state";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__Error__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__Error__TYPE_NAME, 20, 20},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 26, 26},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__Error__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__Error__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
