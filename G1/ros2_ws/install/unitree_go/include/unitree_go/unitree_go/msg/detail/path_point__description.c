// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/PathPoint.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/path_point__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__PathPoint__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xc8, 0xbc, 0xdd, 0x0b, 0x29, 0xc2, 0x8f, 0x9e,
      0x85, 0x3f, 0xfa, 0x2f, 0x4d, 0x40, 0x47, 0x18,
      0xc0, 0x58, 0xf4, 0xc0, 0x84, 0xdc, 0x13, 0x73,
      0x75, 0x40, 0xd8, 0x1e, 0xdb, 0x1c, 0xcd, 0x17,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__PathPoint__TYPE_NAME[] = "unitree_go/msg/PathPoint";

// Define type names, field names, and default values
static char unitree_go__msg__PathPoint__FIELD_NAME__t_from_start[] = "t_from_start";
static char unitree_go__msg__PathPoint__FIELD_NAME__x[] = "x";
static char unitree_go__msg__PathPoint__FIELD_NAME__y[] = "y";
static char unitree_go__msg__PathPoint__FIELD_NAME__yaw[] = "yaw";
static char unitree_go__msg__PathPoint__FIELD_NAME__vx[] = "vx";
static char unitree_go__msg__PathPoint__FIELD_NAME__vy[] = "vy";
static char unitree_go__msg__PathPoint__FIELD_NAME__vyaw[] = "vyaw";

static rosidl_runtime_c__type_description__Field unitree_go__msg__PathPoint__FIELDS[] = {
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__t_from_start, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__yaw, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__vx, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__vy, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__PathPoint__FIELD_NAME__vyaw, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__PathPoint__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__PathPoint__TYPE_NAME, 24, 24},
      {unitree_go__msg__PathPoint__FIELDS, 7, 7},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32 t_from_start\n"
  "float32 x\n"
  "float32 y\n"
  "float32 yaw\n"
  "float32 vx\n"
  "float32 vy\n"
  "float32 vyaw";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__PathPoint__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__PathPoint__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 87, 87},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__PathPoint__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__PathPoint__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
