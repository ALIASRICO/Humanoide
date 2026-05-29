// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_hg:msg/HandState.idl
// generated code does not contain a copyright notice

#include "unitree_hg/msg/detail/hand_state__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_hg
const rosidl_type_hash_t *
unitree_hg__msg__HandState__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xf8, 0xf1, 0x61, 0x52, 0x2d, 0xeb, 0x4e, 0x58,
      0xd5, 0xc1, 0xd6, 0x79, 0x82, 0x6c, 0x2a, 0x40,
      0x5b, 0x63, 0xb4, 0x09, 0xdb, 0x7e, 0x4e, 0xa9,
      0xd1, 0x76, 0x28, 0xf3, 0x02, 0x9c, 0x4d, 0x2f,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_hg/msg/detail/press_sensor_state__functions.h"
#include "unitree_hg/msg/detail/imu_state__functions.h"
#include "unitree_hg/msg/detail/motor_state__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_hg__msg__IMUState__EXPECTED_HASH = {1, {
    0x6f, 0xbb, 0xa1, 0xa6, 0x72, 0x36, 0x0b, 0xf4,
    0x1e, 0x43, 0x93, 0xad, 0x73, 0xd2, 0x47, 0x03,
    0x6f, 0xd8, 0x02, 0xd0, 0x8a, 0xdf, 0xb4, 0x36,
    0xd0, 0xc9, 0x9a, 0x2a, 0x7b, 0x3c, 0xee, 0xc2,
  }};
static const rosidl_type_hash_t unitree_hg__msg__MotorState__EXPECTED_HASH = {1, {
    0x9f, 0xb0, 0xc7, 0xe5, 0x0c, 0xef, 0x17, 0x69,
    0x03, 0x7c, 0x58, 0x03, 0x04, 0x75, 0x0d, 0xf0,
    0xda, 0x54, 0xb7, 0xa6, 0xa5, 0xfb, 0xfa, 0x92,
    0x88, 0x0f, 0x97, 0xad, 0xd4, 0x94, 0x53, 0x45,
  }};
static const rosidl_type_hash_t unitree_hg__msg__PressSensorState__EXPECTED_HASH = {1, {
    0x3c, 0x61, 0xba, 0xe2, 0x3b, 0x78, 0x5e, 0xe8,
    0x50, 0xc5, 0x7d, 0xf7, 0x3a, 0x94, 0x8d, 0x53,
    0xca, 0x5c, 0xb0, 0x0c, 0xcb, 0xdb, 0x82, 0xee,
    0x52, 0x69, 0x94, 0xc7, 0x7a, 0xe8, 0xd9, 0x08,
  }};
#endif

static char unitree_hg__msg__HandState__TYPE_NAME[] = "unitree_hg/msg/HandState";
static char unitree_hg__msg__IMUState__TYPE_NAME[] = "unitree_hg/msg/IMUState";
static char unitree_hg__msg__MotorState__TYPE_NAME[] = "unitree_hg/msg/MotorState";
static char unitree_hg__msg__PressSensorState__TYPE_NAME[] = "unitree_hg/msg/PressSensorState";

// Define type names, field names, and default values
static char unitree_hg__msg__HandState__FIELD_NAME__motor_state[] = "motor_state";
static char unitree_hg__msg__HandState__FIELD_NAME__press_sensor_state[] = "press_sensor_state";
static char unitree_hg__msg__HandState__FIELD_NAME__imu_state[] = "imu_state";
static char unitree_hg__msg__HandState__FIELD_NAME__power_v[] = "power_v";
static char unitree_hg__msg__HandState__FIELD_NAME__power_a[] = "power_a";
static char unitree_hg__msg__HandState__FIELD_NAME__system_v[] = "system_v";
static char unitree_hg__msg__HandState__FIELD_NAME__device_v[] = "device_v";
static char unitree_hg__msg__HandState__FIELD_NAME__error[] = "error";
static char unitree_hg__msg__HandState__FIELD_NAME__reserve[] = "reserve";

static rosidl_runtime_c__type_description__Field unitree_hg__msg__HandState__FIELDS[] = {
  {
    {unitree_hg__msg__HandState__FIELD_NAME__motor_state, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__press_sensor_state, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {unitree_hg__msg__PressSensorState__TYPE_NAME, 31, 31},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__imu_state, 9, 9},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__power_v, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__power_a, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__system_v, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__device_v, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__error, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__HandState__FIELD_NAME__reserve, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT32_ARRAY,
      2,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_hg__msg__HandState__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_hg__msg__IMUState__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__MotorState__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {unitree_hg__msg__PressSensorState__TYPE_NAME, 31, 31},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_hg__msg__HandState__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_hg__msg__HandState__TYPE_NAME, 24, 24},
      {unitree_hg__msg__HandState__FIELDS, 9, 9},
    },
    {unitree_hg__msg__HandState__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_hg__msg__IMUState__EXPECTED_HASH, unitree_hg__msg__IMUState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_hg__msg__IMUState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_hg__msg__MotorState__EXPECTED_HASH, unitree_hg__msg__MotorState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_hg__msg__MotorState__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_hg__msg__PressSensorState__EXPECTED_HASH, unitree_hg__msg__PressSensorState__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = unitree_hg__msg__PressSensorState__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "MotorState[] motor_state\n"
  "PressSensorState[] press_sensor_state\n"
  "IMUState imu_state\n"
  "\n"
  "float32 power_v\n"
  "float32 power_a\n"
  "float32 system_v\n"
  "float32 device_v\n"
  "uint32[2] error\n"
  "uint32[2] reserve";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_hg__msg__HandState__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_hg__msg__HandState__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 183, 183},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_hg__msg__HandState__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_hg__msg__HandState__get_individual_type_description_source(NULL),
    sources[1] = *unitree_hg__msg__IMUState__get_individual_type_description_source(NULL);
    sources[2] = *unitree_hg__msg__MotorState__get_individual_type_description_source(NULL);
    sources[3] = *unitree_hg__msg__PressSensorState__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
