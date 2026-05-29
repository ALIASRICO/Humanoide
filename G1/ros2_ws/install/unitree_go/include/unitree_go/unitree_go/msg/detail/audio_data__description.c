// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/AudioData.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/audio_data__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__AudioData__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x55, 0x97, 0x3f, 0xf9, 0x82, 0xf5, 0x3f, 0x02,
      0x85, 0x5f, 0xf3, 0x4a, 0x18, 0x4f, 0x00, 0xee,
      0x63, 0xb6, 0x8a, 0x3f, 0x65, 0xb1, 0x91, 0x52,
      0x44, 0x8f, 0x9f, 0xd7, 0x55, 0x8e, 0x7d, 0xc5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__AudioData__TYPE_NAME[] = "unitree_go/msg/AudioData";

// Define type names, field names, and default values
static char unitree_go__msg__AudioData__FIELD_NAME__time_frame[] = "time_frame";
static char unitree_go__msg__AudioData__FIELD_NAME__data[] = "data";

static rosidl_runtime_c__type_description__Field unitree_go__msg__AudioData__FIELDS[] = {
  {
    {unitree_go__msg__AudioData__FIELD_NAME__time_frame, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__AudioData__FIELD_NAME__data, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__AudioData__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__AudioData__TYPE_NAME, 24, 24},
      {unitree_go__msg__AudioData__FIELDS, 2, 2},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint64 time_frame\n"
  "uint8[] data";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__AudioData__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__AudioData__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 30, 30},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__AudioData__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__AudioData__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
