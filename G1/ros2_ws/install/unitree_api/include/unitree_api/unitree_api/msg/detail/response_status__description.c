// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/ResponseStatus.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/response_status__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__ResponseStatus__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x28, 0x2a, 0xfd, 0x2a, 0x97, 0x77, 0x10, 0x14,
      0xab, 0xb1, 0xf5, 0xae, 0xad, 0x0f, 0xd2, 0x44,
      0xd6, 0x48, 0xd4, 0x75, 0xf5, 0x5a, 0x82, 0xb0,
      0xc3, 0xc4, 0x12, 0x32, 0xa8, 0xc5, 0x27, 0xf7,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_api__msg__ResponseStatus__TYPE_NAME[] = "unitree_api/msg/ResponseStatus";

// Define type names, field names, and default values
static char unitree_api__msg__ResponseStatus__FIELD_NAME__code[] = "code";

static rosidl_runtime_c__type_description__Field unitree_api__msg__ResponseStatus__FIELDS[] = {
  {
    {unitree_api__msg__ResponseStatus__FIELD_NAME__code, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_api__msg__ResponseStatus__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__ResponseStatus__TYPE_NAME, 30, 30},
      {unitree_api__msg__ResponseStatus__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int32 code";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__ResponseStatus__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__ResponseStatus__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 10, 10},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__ResponseStatus__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__ResponseStatus__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
