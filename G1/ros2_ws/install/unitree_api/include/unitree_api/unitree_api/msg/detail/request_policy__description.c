// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/RequestPolicy.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/request_policy__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__RequestPolicy__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x74, 0x2c, 0x36, 0x12, 0xb9, 0x91, 0xbe, 0x55,
      0x43, 0x0d, 0x18, 0x47, 0xaf, 0x4a, 0xfb, 0x2f,
      0x11, 0x90, 0x69, 0xf2, 0xe1, 0x6e, 0x3a, 0x21,
      0x43, 0xc6, 0x35, 0x2a, 0x94, 0xef, 0x35, 0xe4,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_api__msg__RequestPolicy__TYPE_NAME[] = "unitree_api/msg/RequestPolicy";

// Define type names, field names, and default values
static char unitree_api__msg__RequestPolicy__FIELD_NAME__priority[] = "priority";
static char unitree_api__msg__RequestPolicy__FIELD_NAME__noreply[] = "noreply";

static rosidl_runtime_c__type_description__Field unitree_api__msg__RequestPolicy__FIELDS[] = {
  {
    {unitree_api__msg__RequestPolicy__FIELD_NAME__priority, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestPolicy__FIELD_NAME__noreply, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_api__msg__RequestPolicy__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__RequestPolicy__TYPE_NAME, 29, 29},
      {unitree_api__msg__RequestPolicy__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "int32 priority\n"
  "bool noreply";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__RequestPolicy__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__RequestPolicy__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 27, 27},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__RequestPolicy__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__RequestPolicy__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
