// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/Go2FrontVideoData.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/go2_front_video_data__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__Go2FrontVideoData__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xf5, 0x48, 0xf7, 0xcc, 0xf1, 0x01, 0xbb, 0x02,
      0x55, 0xb0, 0x54, 0x14, 0x84, 0xab, 0x42, 0xaa,
      0xac, 0x31, 0x30, 0x5c, 0xcb, 0xa0, 0x6d, 0xb9,
      0x76, 0xa8, 0xa1, 0x9a, 0x3d, 0xbb, 0x1a, 0x33,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__Go2FrontVideoData__TYPE_NAME[] = "unitree_go/msg/Go2FrontVideoData";

// Define type names, field names, and default values
static char unitree_go__msg__Go2FrontVideoData__FIELD_NAME__time_frame[] = "time_frame";
static char unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video720p[] = "video720p";
static char unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video360p[] = "video360p";
static char unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video180p[] = "video180p";

static rosidl_runtime_c__type_description__Field unitree_go__msg__Go2FrontVideoData__FIELDS[] = {
  {
    {unitree_go__msg__Go2FrontVideoData__FIELD_NAME__time_frame, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT64,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video720p, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video360p, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__Go2FrontVideoData__FIELD_NAME__video180p, 9, 9},
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
unitree_go__msg__Go2FrontVideoData__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__Go2FrontVideoData__TYPE_NAME, 32, 32},
      {unitree_go__msg__Go2FrontVideoData__FIELDS, 4, 4},
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
  "uint8[] video720p\n"
  "uint8[] video360p\n"
  "uint8[] video180p ";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__Go2FrontVideoData__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__Go2FrontVideoData__TYPE_NAME, 32, 32},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 72, 72},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__Go2FrontVideoData__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__Go2FrontVideoData__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
