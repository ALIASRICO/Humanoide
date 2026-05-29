// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/BmsCmd.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/bms_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__BmsCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x7b, 0x7d, 0x2f, 0x71, 0xab, 0x06, 0x19, 0x02,
      0xdd, 0x20, 0x7e, 0x6f, 0x24, 0x31, 0x09, 0x16,
      0x7b, 0x3f, 0xed, 0x94, 0x42, 0x70, 0x66, 0xf4,
      0x01, 0x80, 0xd5, 0x63, 0x29, 0x0b, 0x6e, 0x15,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__BmsCmd__TYPE_NAME[] = "unitree_hg/msg/BmsCmd";

// Define type names, field names, and default values
static char unitree_hg__msg__BmsCmd__FIELD_NAME__cmd[] = "cmd";
static char unitree_hg__msg__BmsCmd__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__BmsCmd__FIELDS[] = {
  {
    {unitree_hg__msg__BmsCmd__FIELD_NAME__cmd, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsCmd__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      40,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__BmsCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__BmsCmd__TYPE_NAME, 21, 21},
      {unitree_hg__msg__BmsCmd__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 cmd\n"
  "uint8[40] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__BmsCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__BmsCmd__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 27, 27},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__BmsCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__BmsCmd__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
