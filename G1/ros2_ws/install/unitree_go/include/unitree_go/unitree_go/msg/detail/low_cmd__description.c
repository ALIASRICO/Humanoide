// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/LowCmd.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/low_cmd__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__LowCmd__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0d, 0xa1, 0x14, 0x2c, 0x99, 0x4d, 0x18, 0x4f,
      0x61, 0x02, 0x94, 0x8c, 0x3a, 0xcf, 0x52, 0xb9,
      0x55, 0x78, 0x36, 0xcf, 0xe5, 0x06, 0x2b, 0x92,
      0x4a, 0x1f, 0x08, 0xac, 0x8b, 0x72, 0xdc, 0x34,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/bms_cmd__functions.h"
#include "unitree_go/msg/detail/motor_cmd__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__BmsCmd__EXPECTED_HASH = {1, {
    0x81, 0x53, 0x10, 0xdf, 0xf4, 0xeb, 0xba, 0x1e,
    0x0d, 0x37, 0x80, 0x2d, 0xfd, 0xc5, 0x6d, 0x4b,
    0x5a, 0x84, 0x97, 0x61, 0xf6, 0x13, 0x95, 0x41,
    0x72, 0xbd, 0xb4, 0x47, 0x6a, 0xed, 0x5a, 0xa2,
  }};
static const rosidl_type_hash_t unitree_go__msg__MotorCmd__EXPECTED_HASH = {1, {
    0x45, 0x81, 0xf1, 0x8a, 0x3b, 0xf5, 0x8b, 0xaa,
    0xd0, 0x4f, 0x12, 0xf5, 0x17, 0x47, 0xf2, 0xdd,
    0x38, 0x8f, 0x64, 0xaa, 0x2a, 0xc9, 0x97, 0xd1,
    0xd6, 0x47, 0x77, 0x56, 0x3c, 0x62, 0x7f, 0xbf,
  }};
#endif

static char unitree_go__msg__LowCmd__TYPE_NAME[] = "unitree_go/msg/LowCmd";
static char unitree_go__msg__BmsCmd__TYPE_NAME[] = "unitree_go/msg/BmsCmd";
static char unitree_go__msg__MotorCmd__TYPE_NAME[] = "unitree_go/msg/MotorCmd";

// Define type names, field names, and default values
static char unitree_go__msg__LowCmd__FIELD_NAME__head[] = "head";
static char unitree_go__msg__LowCmd__FIELD_NAME__level_flag[] = "level_flag";
static char unitree_go__msg__LowCmd__FIELD_NAME__frame_reserve[] = "frame_reserve";
static char unitree_go__msg__LowCmd__FIELD_NAME__sn[] = "sn";
static char unitree_go__msg__LowCmd__FIELD_NAME__version[] = "version";
static char unitree_go__msg__LowCmd__FIELD_NAME__bandwidth[] = "bandwidth";
static char unitree_go__msg__LowCmd__FIELD_NAME__motor_cmd[] = "motor_cmd";
static char unitree_go__msg__LowCmd__FIELD_NAME__bms_cmd[] = "bms_cmd";
static char unitree_go__msg__LowCmd__FIELD_NAME__wireless_remote[] = "wireless_remote";
static char unitree_go__msg__LowCmd__FIELD_NAME__led[] = "led";
static char unitree_go__msg__LowCmd__FIELD_NAME__fan[] = "fan";
static char unitree_go__msg__LowCmd__FIELD_NAME__gpio[] = "gpio";
static char unitree_go__msg__LowCmd__FIELD_NAME__reserve[] = "reserve";
static char unitree_go__msg__LowCmd__FIELD_NAME__crc[] = "crc";

static rosidl_runtime_c__type_description__Field unitree_go__msg__LowCmd__FIELDS[] = {
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__head, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__level_flag, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__frame_reserve, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__sn, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__version, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__bandwidth, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__motor_cmd, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_ARRAY,
      20,
      0,
      {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__bms_cmd, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__wireless_remote, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      40,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__led, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      12,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__fan, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__gpio, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowCmd__FIELD_NAME__crc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__LowCmd__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__BmsCmd__TYPE_NAME, 21, 21},
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorCmd__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__LowCmd__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__LowCmd__TYPE_NAME, 21, 21},
      {unitree_go__msg__LowCmd__FIELDS, 14, 14},
    },
    {unitree_go__msg__LowCmd__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__BmsCmd__EXPECTED_HASH, unitree_go__msg__BmsCmd__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__BmsCmd__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_go__msg__MotorCmd__EXPECTED_HASH, unitree_go__msg__MotorCmd__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_go__msg__MotorCmd__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "uint8[2] head\n"
  "uint8 level_flag\n"
  "uint8 frame_reserve\n"
  "uint32[2] sn\n"
  "uint32[2] version\n"
  "uint16 bandwidth\n"
  "MotorCmd[20] motor_cmd\n"
  "BmsCmd bms_cmd\n"
  "uint8[40] wireless_remote\n"
  "uint8[12] led\n"
  "uint8[2] fan\n"
  "uint8 gpio\n"
  "uint32 reserve\n"
  "uint32 crc\n"
  "";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__LowCmd__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__LowCmd__TYPE_NAME, 21, 21},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 228, 228},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__LowCmd__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__LowCmd__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__BmsCmd__get_individual_type_description_source(NULL);
    sources[2] = *unitree_go__msg__MotorCmd__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
