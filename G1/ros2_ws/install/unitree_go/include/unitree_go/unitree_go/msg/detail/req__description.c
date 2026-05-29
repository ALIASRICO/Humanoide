// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/Req.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/req__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__Req__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x7f, 0xda, 0x90, 0x9d, 0x42, 0x42, 0x47, 0x77,
      0xc9, 0x47, 0xf9, 0xc3, 0x3a, 0x7a, 0x24, 0x3e,
      0xb1, 0xa4, 0xa1, 0xe8, 0x9a, 0xf5, 0x12, 0x4a,
      0x3a, 0x2c, 0xa7, 0xd3, 0xfa, 0x04, 0x3b, 0x6e,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__Req__TYPE_NAME[] = "unitree_go/msg/Req";

// Define type names, field names, and default values
static char unitree_go__msg__Req__FIELD_NAME__uuid[] = "uuid";
static char unitree_go__msg__Req__FIELD_NAME__body[] = "body";

static rosidl_runtime_c__type_description__Field unitree_go__msg__Req__FIELDS[] = {
  {
    {unitree_go__msg__Req__FIELD_NAME__uuid, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Req__FIELD_NAME__body, 4, 4},
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
unitree_go__msg__Req__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__Req__TYPE_NAME, 18, 18},
      {unitree_go__msg__Req__FIELDS, 2, 2},
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
  "string body";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__Req__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__Req__TYPE_NAME, 18, 18},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 23, 23},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__Req__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__Req__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
