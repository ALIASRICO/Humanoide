// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/Res.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/res__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__Res__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x5e, 0x73, 0x0f, 0xb5, 0x4d, 0x81, 0xa3, 0x2e,
      0x7e, 0x28, 0xef, 0x51, 0x9c, 0x9b, 0x10, 0x8c,
      0x99, 0xab, 0x6b, 0xe7, 0xdd, 0x77, 0xc1, 0xef,
      0x4e, 0x66, 0xf7, 0xc1, 0xe6, 0x9d, 0xde, 0x16,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__Res__TYPE_NAME[] = "unitree_go/msg/Res";

// Define type names, field names, and default values
static char unitree_go__msg__Res__FIELD_NAME__uuid[] = "uuid";
static char unitree_go__msg__Res__FIELD_NAME__data[] = "data";
static char unitree_go__msg__Res__FIELD_NAME__body[] = "body";

static rosidl_runtime_c__type_description__Field unitree_go__msg__Res__FIELDS[] = {
  {
    {unitree_go__msg__Res__FIELD_NAME__uuid, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Res__FIELD_NAME__data, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Res__FIELD_NAME__body, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__Res__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__Res__TYPE_NAME, 18, 18},
      {unitree_go__msg__Res__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "string uuid\n"
  "uint8[] data\n"
  "string body";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__Res__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__Res__TYPE_NAME, 18, 18},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 36, 36},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__Res__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__Res__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
