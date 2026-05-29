// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/RequestLease.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/request_lease__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__RequestLease__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x16, 0xb5, 0xc2, 0x25, 0x7d, 0x52, 0x80, 0xa0,
      0x95, 0xe3, 0xe4, 0xfe, 0x26, 0xa4, 0x8e, 0x78,
      0x2e, 0x29, 0x4f, 0xa3, 0xd6, 0x87, 0x60, 0xce,
      0x38, 0x59, 0x92, 0x60, 0xa3, 0x44, 0xbf, 0x4e,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_api__msg__RequestLease__TYPE_NAME[] = "unitree_api/msg/RequestLease";

// Define type names, field names, and default values
static char unitree_api__msg__RequestLease__FIELD_NAME__id[] = "id";

static rosidl_runtime_c__type_description__Field unitree_api__msg__RequestLease__FIELDS[] = {
  {
    {unitree_api__msg__RequestLease__FIELD_NAME__id, 2, 2},
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
unitree_api__msg__RequestLease__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__RequestLease__TYPE_NAME, 28, 28},
      {unitree_api__msg__RequestLease__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int64 id";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__RequestLease__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__RequestLease__TYPE_NAME, 28, 28},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 8, 8},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__RequestLease__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__RequestLease__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
