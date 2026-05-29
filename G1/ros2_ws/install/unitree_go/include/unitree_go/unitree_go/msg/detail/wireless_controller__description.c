// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/WirelessController.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/wireless_controller__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__WirelessController__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x83, 0xa5, 0xbb, 0xbf, 0x02, 0x2f, 0x06, 0x0a,
      0xa3, 0x67, 0x16, 0xee, 0x78, 0xaf, 0xb8, 0x02,
      0x52, 0x8f, 0x26, 0xce, 0x16, 0x23, 0x8b, 0x9c,
      0x37, 0x87, 0x93, 0x9c, 0x83, 0x0c, 0xbd, 0xe5,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__WirelessController__TYPE_NAME[] = "unitree_go/msg/WirelessController";

// Define type names, field names, and default values
static char unitree_go__msg__WirelessController__FIELD_NAME__lx[] = "lx";
static char unitree_go__msg__WirelessController__FIELD_NAME__ly[] = "ly";
static char unitree_go__msg__WirelessController__FIELD_NAME__rx[] = "rx";
static char unitree_go__msg__WirelessController__FIELD_NAME__ry[] = "ry";
static char unitree_go__msg__WirelessController__FIELD_NAME__keys[] = "keys";

static rosidl_runtime_c__type_description__Field unitree_go__msg__WirelessController__FIELDS[] = {
  {
    {unitree_go__msg__WirelessController__FIELD_NAME__lx, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__WirelessController__FIELD_NAME__ly, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__WirelessController__FIELD_NAME__rx, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__WirelessController__FIELD_NAME__ry, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__WirelessController__FIELD_NAME__keys, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__WirelessController__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__WirelessController__TYPE_NAME, 33, 33},
      {unitree_go__msg__WirelessController__FIELDS, 5, 5},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32 lx\n"
  "float32 ly\n"
  "float32 rx\n"
  "float32 ry\n"
  "uint16 keys";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__WirelessController__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__WirelessController__TYPE_NAME, 33, 33},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 55, 55},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__WirelessController__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__WirelessController__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
