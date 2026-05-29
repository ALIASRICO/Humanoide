// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/RequestIdentity.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/request_identity__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__RequestIdentity__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x91, 0x2f, 0xcf, 0x30, 0x8a, 0x7c, 0xd6, 0xe2,
      0x7e, 0xa3, 0xae, 0xea, 0x02, 0x51, 0x5f, 0x58,
      0x7f, 0xa6, 0x66, 0xb7, 0x6a, 0xf1, 0x96, 0x36,
      0x60, 0x42, 0x99, 0x95, 0xf0, 0xe3, 0x81, 0xc6,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_api__msg__RequestIdentity__TYPE_NAME[] = "unitree_api/msg/RequestIdentity";

// Define type names, field names, and default values
static char unitree_api__msg__RequestIdentity__FIELD_NAME__id[] = "id";
static char unitree_api__msg__RequestIdentity__FIELD_NAME__api_id[] = "api_id";

static rosidl_runtime_c__type_description__Field unitree_api__msg__RequestIdentity__FIELDS[] = {
  {
    {unitree_api__msg__RequestIdentity__FIELD_NAME__id, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestIdentity__FIELD_NAME__api_id, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_api__msg__RequestIdentity__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
      {unitree_api__msg__RequestIdentity__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int64  id\n"
  "int64 api_id";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__RequestIdentity__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 22, 22},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__RequestIdentity__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__RequestIdentity__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
