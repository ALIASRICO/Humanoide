// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/BmsState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/bms_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__BmsState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x59, 0xd9, 0xc2, 0x45, 0x9d, 0xdf, 0x39, 0x00,
      0x72, 0x90, 0x28, 0x96, 0x85, 0x0c, 0xe1, 0x3e,
      0xa5, 0xde, 0x39, 0x41, 0x57, 0x90, 0x7c, 0x7d,
      0xc5, 0x14, 0xd2, 0x18, 0x7f, 0xf3, 0xe5, 0x1f,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char unitree_hg__msg__BmsState__TYPE_NAME[] = "unitree_hg/msg/BmsState";

// Define type names, field names, and default values
static char unitree_hg__msg__BmsState__FIELD_NAME__version_high[] = "version_high";
static char unitree_hg__msg__BmsState__FIELD_NAME__version_low[] = "version_low";
static char unitree_hg__msg__BmsState__FIELD_NAME__fn[] = "fn";
static char unitree_hg__msg__BmsState__FIELD_NAME__cell_vol[] = "cell_vol";
static char unitree_hg__msg__BmsState__FIELD_NAME__bmsvoltage[] = "bmsvoltage";
static char unitree_hg__msg__BmsState__FIELD_NAME__current[] = "current";
static char unitree_hg__msg__BmsState__FIELD_NAME__soc[] = "soc";
static char unitree_hg__msg__BmsState__FIELD_NAME__soh[] = "soh";
static char unitree_hg__msg__BmsState__FIELD_NAME__temperature[] = "temperature";
static char unitree_hg__msg__BmsState__FIELD_NAME__cycle[] = "cycle";
static char unitree_hg__msg__BmsState__FIELD_NAME__manufacturer_date[] = "manufacturer_date";
static char unitree_hg__msg__BmsState__FIELD_NAME__bmsstate[] = "bmsstate";
static char unitree_hg__msg__BmsState__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__BmsState__FIELDS[] = {
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__version_high, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__version_low, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__fn, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__cell_vol, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16_ARRAY,
      40,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__bmsvoltage, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__current, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__soc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__soh, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__temperature, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__cycle, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__manufacturer_date, 17, 17},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__bmsstate, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      5,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__BmsState__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      3,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__BmsState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__BmsState__TYPE_NAME, 23, 23},
      {unitree_hg__msg__BmsState__FIELDS, 13, 13},
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
  "uint8 fn\n"
  "uint16[40] cell_vol\n"
  "uint32[3] bmsvoltage\n"
  "int32 current\n"
  "uint8 soc\n"
  "uint8 soh\n"
  "int16[12] temperature\n"
  "uint16 cycle\n"
  "uint16 manufacturer_date\n"
  "uint32[5] bmsstate\n"
  "uint32[3] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__BmsState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__BmsState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 218, 218},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__BmsState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__BmsState__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
