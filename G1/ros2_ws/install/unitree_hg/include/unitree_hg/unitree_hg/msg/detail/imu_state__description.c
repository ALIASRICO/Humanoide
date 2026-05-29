// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/IMUState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/imu_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__IMUState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x6f, 0xbb, 0xa1, 0xa6, 0x72, 0x36, 0x0b, 0xf4,
      0x1e, 0x43, 0x93, 0xad, 0x73, 0xd2, 0x47, 0x03,
      0x6f, 0xd8, 0x02, 0xd0, 0x8a, 0xdf, 0xb4, 0x36,
      0xd0, 0xc9, 0x9a, 0x2a, 0x7b, 0x3c, 0xee, 0xc2,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__IMUState__TYPE_NAME[] = "unitree_hg/msg/IMUState";

// Define type names, field names, and default values
static char unitree_hg__msg__IMUState__FIELD_NAME__quaternion[] = "quaternion";
static char unitree_hg__msg__IMUState__FIELD_NAME__gyroscope[] = "gyroscope";
static char unitree_hg__msg__IMUState__FIELD_NAME__accelerometer[] = "accelerometer";
static char unitree_hg__msg__IMUState__FIELD_NAME__rpy[] = "rpy";
static char unitree_hg__msg__IMUState__FIELD_NAME__temperature[] = "temperature";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__IMUState__FIELDS[] = {
  {
    {unitree_hg__msg__IMUState__FIELD_NAME__quaternion, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__IMUState__FIELD_NAME__gyroscope, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__IMUState__FIELD_NAME__accelerometer, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__IMUState__FIELD_NAME__rpy, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__IMUState__FIELD_NAME__temperature, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__IMUState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
      {unitree_hg__msg__IMUState__FIELDS, 5, 5},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32[4] quaternion\n"
  "float32[3] gyroscope\n"
  "float32[3] accelerometer\n"
  "float32[3] rpy\n"
  "int16 temperature";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__IMUState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 101, 101},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__IMUState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__IMUState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
