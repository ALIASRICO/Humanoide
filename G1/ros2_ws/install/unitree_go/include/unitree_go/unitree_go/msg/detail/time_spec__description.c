// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/TimeSpec.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/time_spec__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__TimeSpec__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0c, 0xac, 0x3f, 0x06, 0x05, 0xaf, 0x32, 0x3a,
      0xdd, 0x43, 0xe1, 0xed, 0x3a, 0xe7, 0xfc, 0x01,
      0xf7, 0xc7, 0x85, 0x7f, 0x41, 0x38, 0x01, 0x70,
      0xb3, 0xea, 0x3a, 0x89, 0x9b, 0x28, 0xcb, 0x76,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__TimeSpec__TYPE_NAME[] = "unitree_go/msg/TimeSpec";

// Define type names, field names, and default values
static char unitree_go__msg__TimeSpec__FIELD_NAME__sec[] = "sec";
static char unitree_go__msg__TimeSpec__FIELD_NAME__nanosec[] = "nanosec";

static rosidl_runtime_c__type_description__Field unitree_go__msg__TimeSpec__FIELDS[] = {
  {
    {unitree_go__msg__TimeSpec__FIELD_NAME__sec, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__TimeSpec__FIELD_NAME__nanosec, 7, 7},
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
unitree_go__msg__TimeSpec__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__TimeSpec__TYPE_NAME, 23, 23},
      {unitree_go__msg__TimeSpec__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Time indicates a specific point in time, relative to a clock's 0 point.\n"
  "# The seconds component, valid over all int32 values.\n"
  "int32 sec\n"
  "# The nanoseconds component, valid in the range [0, 10e9).\n"
  "uint32 nanosec";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__TimeSpec__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__TimeSpec__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 212, 212},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__TimeSpec__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__TimeSpec__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
