// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/BmsState.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/bms_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__BmsState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xa7, 0xfe, 0x45, 0xfb, 0xbb, 0x6a, 0x90, 0x8b,
      0xde, 0xe7, 0x8b, 0xaa, 0x3b, 0x93, 0xe9, 0x62,
      0xed, 0x92, 0x4c, 0x14, 0x34, 0x81, 0xa6, 0x96,
      0xf9, 0x5b, 0x69, 0x11, 0xce, 0x30, 0xb8, 0x71,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_go__msg__BmsState__TYPE_NAME[] = "unitree_go/msg/BmsState";

// Define type names, field names, and default values
static char unitree_go__msg__BmsState__FIELD_NAME__version_high[] = "version_high";
static char unitree_go__msg__BmsState__FIELD_NAME__version_low[] = "version_low";
static char unitree_go__msg__BmsState__FIELD_NAME__status[] = "status";
static char unitree_go__msg__BmsState__FIELD_NAME__soc[] = "soc";
static char unitree_go__msg__BmsState__FIELD_NAME__current[] = "current";
static char unitree_go__msg__BmsState__FIELD_NAME__cycle[] = "cycle";
static char unitree_go__msg__BmsState__FIELD_NAME__bq_ntc[] = "bq_ntc";
static char unitree_go__msg__BmsState__FIELD_NAME__mcu_ntc[] = "mcu_ntc";
static char unitree_go__msg__BmsState__FIELD_NAME__cell_vol[] = "cell_vol";

static rosidl_runtime_c__type_description__Field unitree_go__msg__BmsState__FIELDS[] = {
  {
    {unitree_go__msg__BmsState__FIELD_NAME__version_high, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__version_low, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__status, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__soc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__current, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__cycle, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__bq_ntc, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__mcu_ntc, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__BmsState__FIELD_NAME__cell_vol, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16_ARRAY,
      15,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__BmsState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__BmsState__TYPE_NAME, 23, 23},
      {unitree_go__msg__BmsState__FIELDS, 9, 9},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8 version_high\n"
  "uint8 version_low\n"
  "uint8 status\n"
  "uint8 soc\n"
  "int32 current\n"
  "uint16 cycle\n"
  "int8[2] bq_ntc\n"
  "int8[2] mcu_ntc\n"
  "uint16[15] cell_vol";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__BmsState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__BmsState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 137, 137},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__BmsState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__BmsState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
