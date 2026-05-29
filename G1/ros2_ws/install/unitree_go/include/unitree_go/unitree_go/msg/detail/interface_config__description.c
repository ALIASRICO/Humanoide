// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/InterfaceConfig.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/interface_config__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__InterfaceConfig__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x78, 0xcd, 0xda, 0x3c, 0xfb, 0xbf, 0xeb, 0x9b,
      0x32, 0xfc, 0xa9, 0xa0, 0x56, 0x72, 0x74, 0x19,
      0xed, 0x88, 0xf9, 0x08, 0xed, 0x99, 0xc6, 0x4e,
      0x7b, 0x81, 0x0f, 0x35, 0x28, 0x1b, 0xe6, 0x1b,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__InterfaceConfig__TYPE_NAME[] = "unitree_go/msg/InterfaceConfig";

// Define type names, field names, and default values
static char unitree_go__msg__InterfaceConfig__FIELD_NAME__mode[] = "mode";
static char unitree_go__msg__InterfaceConfig__FIELD_NAME__value[] = "value";
static char unitree_go__msg__InterfaceConfig__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_go__msg__InterfaceConfig__FIELDS[] = {
  {
    {unitree_go__msg__InterfaceConfig__FIELD_NAME__mode, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__InterfaceConfig__FIELD_NAME__value, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__InterfaceConfig__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__InterfaceConfig__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__InterfaceConfig__TYPE_NAME, 30, 30},
      {unitree_go__msg__InterfaceConfig__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 mode\n"
  "uint8 value\n"
  "uint8[2] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__InterfaceConfig__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__InterfaceConfig__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 39, 39},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__InterfaceConfig__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__InterfaceConfig__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
