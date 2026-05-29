// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_go:msg/LowState.idl
// generated code does not contain a copyright notice

#include "unitree_go/msg/detail/low_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_go
const rosidl_type_hash_t *
unitree_go__msg__LowState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xdb, 0x51, 0x72, 0xca, 0xc9, 0x33, 0xe3, 0xcf,
      0xc0, 0xe7, 0x05, 0x90, 0x33, 0x43, 0xeb, 0x4e,
      0xea, 0x42, 0xe6, 0x5e, 0x22, 0x4e, 0x9d, 0x72,
      0x6d, 0x3e, 0x67, 0x2a, 0xec, 0x0c, 0xaf, 0x0f,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_go/msg/detail/bms_state__functions.h"
#include "unitree_go/msg/detail/imu_state__functions.h"
#include "unitree_go/msg/detail/motor_state__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_go__msg__BmsState__EXPECTED_HASH = {1, {
    0xa7, 0xfe, 0x45, 0xfb, 0xbb, 0x6a, 0x90, 0x8b,
    0xde, 0xe7, 0x8b, 0xaa, 0x3b, 0x93, 0xe9, 0x62,
    0xed, 0x92, 0x4c, 0x14, 0x34, 0x81, 0xa6, 0x96,
    0xf9, 0x5b, 0x69, 0x11, 0xce, 0x30, 0xb8, 0x71,
  }};
static const rosidl_type_hash_t unitree_go__msg__IMUState__EXPECTED_HASH = {1, {
    0x22, 0x67, 0x72, 0x53, 0x1e, 0x06, 0xca, 0x57,
    0x68, 0xda, 0xd7, 0xae, 0x26, 0x42, 0x21, 0x62,
    0x2e, 0x92, 0xba, 0x1d, 0xbc, 0x7f, 0xcd, 0x7f,
    0x80, 0x74, 0x35, 0x1a, 0x23, 0xfe, 0x1c, 0x11,
  }};
static const rosidl_type_hash_t unitree_go__msg__MotorState__EXPECTED_HASH = {1, {
    0x86, 0xfb, 0x56, 0xa4, 0xf6, 0xbe, 0xbc, 0xba,
    0x85, 0x4e, 0x9b, 0x51, 0x02, 0x25, 0xe6, 0x66,
    0x6e, 0xf4, 0x6c, 0xf4, 0xea, 0x13, 0x35, 0x58,
    0x70, 0xc2, 0xdd, 0x3c, 0x34, 0x78, 0xa8, 0x8c,
  }};
#endif

static char unitree_go__msg__LowState__TYPE_NAME[] = "unitree_go/msg/LowState";
static char unitree_go__msg__BmsState__TYPE_NAME[] = "unitree_go/msg/BmsState";
static char unitree_go__msg__IMUState__TYPE_NAME[] = "unitree_go/msg/IMUState";
static char unitree_go__msg__MotorState__TYPE_NAME[] = "unitree_go/msg/MotorState";

// Define type names, field names, and default values
static char unitree_go__msg__LowState__FIELD_NAME__head[] = "head";
static char unitree_go__msg__LowState__FIELD_NAME__level_flag[] = "level_flag";
static char unitree_go__msg__LowState__FIELD_NAME__frame_reserve[] = "frame_reserve";
static char unitree_go__msg__LowState__FIELD_NAME__sn[] = "sn";
static char unitree_go__msg__LowState__FIELD_NAME__version[] = "version";
static char unitree_go__msg__LowState__FIELD_NAME__bandwidth[] = "bandwidth";
static char unitree_go__msg__LowState__FIELD_NAME__imu_state[] = "imu_state";
static char unitree_go__msg__LowState__FIELD_NAME__motor_state[] = "motor_state";
static char unitree_go__msg__LowState__FIELD_NAME__bms_state[] = "bms_state";
static char unitree_go__msg__LowState__FIELD_NAME__foot_force[] = "foot_force";
static char unitree_go__msg__LowState__FIELD_NAME__foot_force_est[] = "foot_force_est";
static char unitree_go__msg__LowState__FIELD_NAME__tick[] = "tick";
static char unitree_go__msg__LowState__FIELD_NAME__wireless_remote[] = "wireless_remote";
static char unitree_go__msg__LowState__FIELD_NAME__bit_flag[] = "bit_flag";
static char unitree_go__msg__LowState__FIELD_NAME__adc_reel[] = "adc_reel";
static char unitree_go__msg__LowState__FIELD_NAME__temperature_ntc1[] = "temperature_ntc1";
static char unitree_go__msg__LowState__FIELD_NAME__temperature_ntc2[] = "temperature_ntc2";
static char unitree_go__msg__LowState__FIELD_NAME__power_v[] = "power_v";
static char unitree_go__msg__LowState__FIELD_NAME__power_a[] = "power_a";
static char unitree_go__msg__LowState__FIELD_NAME__fan_frequency[] = "fan_frequency";
static char unitree_go__msg__LowState__FIELD_NAME__reserve[] = "reserve";
static char unitree_go__msg__LowState__FIELD_NAME__crc[] = "crc";

static rosidl_runtime_c__type_description__Field unitree_go__msg__LowState__FIELDS[] = {
  {
    {unitree_go__msg__LowState__FIELD_NAME__head, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__level_flag, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__frame_reserve, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__sn, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__version, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__bandwidth, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__imu_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__IMUState__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__motor_state, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_ARRAY,
      20,
      0,
      {unitree_go__msg__MotorState__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__bms_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_go__msg__BmsState__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__foot_force, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__foot_force_est, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT16_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__tick, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__wireless_remote, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8_ARRAY,
      40,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__bit_flag, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__adc_reel, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__temperature_ntc1, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__temperature_ntc2, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__power_v, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__power_a, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__fan_frequency, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT16_ARRAY,
      4,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__LowState__FIELD_NAME__crc, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_go__msg__LowState__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_go__msg__BmsState__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__IMUState__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {unitree_go__msg__MotorState__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_go__msg__LowState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_go__msg__LowState__TYPE_NAME, 23, 23},
      {unitree_go__msg__LowState__FIELDS, 22, 22},
    },
    {unitree_go__msg__LowState__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_go__msg__BmsState__EXPECTED_HASH, unitree_go__msg__BmsState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_go__msg__BmsState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_go__msg__IMUState__EXPECTED_HASH, unitree_go__msg__IMUState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_go__msg__IMUState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_go__msg__MotorState__EXPECTED_HASH, unitree_go__msg__MotorState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = unitree_go__msg__MotorState__get_type_description(NULL)->type_description.fields;
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
  "IMUState imu_state\n"
  "MotorState[20] motor_state\n"
  "BmsState bms_state\n"
  "int16[4] foot_force\n"
  "int16[4] foot_force_est\n"
  "uint32 tick\n"
  "uint8[40] wireless_remote\n"
  "uint8 bit_flag\n"
  "float32 adc_reel\n"
  "int8 temperature_ntc1\n"
  "int8 temperature_ntc2\n"
  "float32 power_v\n"
  "float32 power_a\n"
  "uint16[4] fan_frequency\n"
  "uint32 reserve\n"
  "uint32 crc";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_go__msg__LowState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_go__msg__LowState__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 403, 403},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_go__msg__LowState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_go__msg__LowState__get_individual_type_description_source(NULL),
    sources[1] = *unitree_go__msg__BmsState__get_individual_type_description_source(NULL);
    sources[2] = *unitree_go__msg__IMUState__get_individual_type_description_source(NULL);
    sources[3] = *unitree_go__msg__MotorState__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
