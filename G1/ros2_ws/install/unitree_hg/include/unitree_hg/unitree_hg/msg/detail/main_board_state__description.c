// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/MainBoardState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/main_board_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__MainBoardState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x14, 0x20, 0x20, 0x0f, 0xd0, 0xee, 0xdd, 0x8d,
      0xba, 0xbb, 0x47, 0xd0, 0xea, 0x2c, 0x3b, 0xdb,
      0x38, 0xa7, 0xee, 0x47, 0xc6, 0x82, 0xc8, 0x43,
      0x01, 0x32, 0x6d, 0xb5, 0x1b, 0xaa, 0x54, 0x50,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__MainBoardState__TYPE_NAME[] = "unitree_hg/msg/MainBoardState";

// Define type names, field names, and default values
static char unitree_hg__msg__MainBoardState__FIELD_NAME__fan_state[] = "fan_state";
static char unitree_hg__msg__MainBoardState__FIELD_NAME__temperature[] = "temperature";
static char unitree_hg__msg__MainBoardState__FIELD_NAME__value[] = "value";
static char unitree_hg__msg__MainBoardState__FIELD_NAME__state[] = "state";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__MainBoardState__FIELDS[] = {
  {
    {unitree_hg__msg__MainBoardState__FIELD_NAME__fan_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16_ARRAY,
      6,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MainBoardState__FIELD_NAME__temperature, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      6,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MainBoardState__FIELD_NAME__value, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      6,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MainBoardState__FIELD_NAME__state, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      6,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__MainBoardState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__MainBoardState__TYPE_NAME, 29, 29},
      {unitree_hg__msg__MainBoardState__FIELDS, 4, 4},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint16[6] fan_state\n"
  "int16[6] temperature\n"
  "float32[6] value\n"
  "uint32[6] state";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__MainBoardState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__MainBoardState__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 73, 73},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__MainBoardState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__MainBoardState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
