// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/PressSensorState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/press_sensor_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__PressSensorState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x3c, 0x61, 0xba, 0xe2, 0x3b, 0x78, 0x5e, 0xe8,
      0x50, 0xc5, 0x7d, 0xf7, 0x3a, 0x94, 0x8d, 0x53,
      0xca, 0x5c, 0xb0, 0x0c, 0xcb, 0xdb, 0x82, 0xee,
      0x52, 0x69, 0x94, 0xc7, 0x7a, 0xe8, 0xd9, 0x08,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__PressSensorState__TYPE_NAME[] = "unitree_hg/msg/PressSensorState";

// Define type names, field names, and default values
static char unitree_hg__msg__PressSensorState__FIELD_NAME__pressure[] = "pressure";
static char unitree_hg__msg__PressSensorState__FIELD_NAME__temperature[] = "temperature";
static char unitree_hg__msg__PressSensorState__FIELD_NAME__lost[] = "lost";
static char unitree_hg__msg__PressSensorState__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__PressSensorState__FIELDS[] = {
  {
    {unitree_hg__msg__PressSensorState__FIELD_NAME__pressure, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__PressSensorState__FIELD_NAME__temperature, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__PressSensorState__FIELD_NAME__lost, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__PressSensorState__FIELD_NAME__reserve, 7, 7},
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
unitree_hg__msg__PressSensorState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__PressSensorState__TYPE_NAME, 31, 31},
      {unitree_hg__msg__PressSensorState__FIELDS, 4, 4},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32[12] pressure\n"
  "float32[12] temperature\n"
  "uint32 lost\n"
  "uint32 reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__PressSensorState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__PressSensorState__TYPE_NAME, 31, 31},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 71, 71},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__PressSensorState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__PressSensorState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
