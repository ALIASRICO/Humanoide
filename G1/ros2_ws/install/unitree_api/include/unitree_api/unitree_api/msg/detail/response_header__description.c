// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/ResponseHeader.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/response_header__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__ResponseHeader__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xeb, 0xa1, 0x36, 0xc9, 0x30, 0x27, 0x1e, 0xec,
      0x2f, 0xc5, 0x82, 0xcf, 0xcc, 0xc5, 0x94, 0x8f,
      0x8a, 0xf3, 0xfe, 0x44, 0x31, 0x49, 0x28, 0x42,
      0xa0, 0x3a, 0x3d, 0xac, 0xb1, 0xb0, 0xd7, 0x65,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_api/msg/detail/request_identity__functions.h"
#include "unitree_api/msg/detail/response_status__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_api__msg__RequestIdentity__EXPECTED_HASH = {1, {
    0x91, 0x2f, 0xcf, 0x30, 0x8a, 0x7c, 0xd6, 0xe2,
    0x7e, 0xa3, 0xae, 0xea, 0x02, 0x51, 0x5f, 0x58,
    0x7f, 0xa6, 0x66, 0xb7, 0x6a, 0xf1, 0x96, 0x36,
    0x60, 0x42, 0x99, 0x95, 0xf0, 0xe3, 0x81, 0xc6,
  }};
static const rosidl_type_hash_t unitree_api__msg__ResponseStatus__EXPECTED_HASH = {1, {
    0x28, 0x2a, 0xfd, 0x2a, 0x97, 0x77, 0x10, 0x14,
    0xab, 0xb1, 0xf5, 0xae, 0xad, 0x0f, 0xd2, 0x44,
    0xd6, 0x48, 0xd4, 0x75, 0xf5, 0x5a, 0x82, 0xb0,
    0xc3, 0xc4, 0x12, 0x32, 0xa8, 0xc5, 0x27, 0xf7,
  }};
#endif

static char unitree_api__msg__ResponseHeader__TYPE_NAME[] = "unitree_api/msg/ResponseHeader";
static char unitree_api__msg__RequestIdentity__TYPE_NAME[] = "unitree_api/msg/RequestIdentity";
static char unitree_api__msg__ResponseStatus__TYPE_NAME[] = "unitree_api/msg/ResponseStatus";

// Define type names, field names, and default values
static char unitree_api__msg__ResponseHeader__FIELD_NAME__identity[] = "identity";
static char unitree_api__msg__ResponseHeader__FIELD_NAME__status[] = "status";

static rosidl_runtime_c__type_description__Field unitree_api__msg__ResponseHeader__FIELDS[] = {
  {
    {unitree_api__msg__ResponseHeader__FIELD_NAME__identity, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__ResponseHeader__FIELD_NAME__status, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_api__msg__ResponseStatus__TYPE_NAME, 30, 30},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_api__msg__ResponseHeader__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__ResponseStatus__TYPE_NAME, 30, 30},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_api__msg__ResponseHeader__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__ResponseHeader__TYPE_NAME, 30, 30},
      {unitree_api__msg__ResponseHeader__FIELDS, 2, 2},
    },
    {unitree_api__msg__ResponseHeader__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_api__msg__RequestIdentity__EXPECTED_HASH, unitree_api__msg__RequestIdentity__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_api__msg__RequestIdentity__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_api__msg__ResponseStatus__EXPECTED_HASH, unitree_api__msg__ResponseStatus__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_api__msg__ResponseStatus__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "RequestIdentity identity\n"
  "ResponseStatus status";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__ResponseHeader__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__ResponseHeader__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 47, 47},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__ResponseHeader__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__ResponseHeader__get_individual_type_description_source(NULL),
    sources[1] = *unitree_api__msg__RequestIdentity__get_individual_type_description_source(NULL);
    sources[2] = *unitree_api__msg__ResponseStatus__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
