// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from unitree_api:msg/RequestHeader.idl
// generated code does not contain a copyright notice

#include "unitree_api/msg/detail/request_header__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_unitree_api
const rosidl_type_hash_t *
unitree_api__msg__RequestHeader__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x42, 0x73, 0xd5, 0xfb, 0xe6, 0xbe, 0xe5, 0x25,
      0x02, 0xf5, 0x5a, 0x6a, 0x73, 0x42, 0x7e, 0x4a,
      0xe2, 0xf1, 0x23, 0x29, 0xf1, 0x75, 0xd7, 0xc0,
      0x7b, 0x95, 0x34, 0x1f, 0xd5, 0x27, 0xac, 0xff,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "unitree_api/msg/detail/request_policy__functions.h"
#include "unitree_api/msg/detail/request_identity__functions.h"
#include "unitree_api/msg/detail/request_lease__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t unitree_api__msg__RequestIdentity__EXPECTED_HASH = {1, {
    0x91, 0x2f, 0xcf, 0x30, 0x8a, 0x7c, 0xd6, 0xe2,
    0x7e, 0xa3, 0xae, 0xea, 0x02, 0x51, 0x5f, 0x58,
    0x7f, 0xa6, 0x66, 0xb7, 0x6a, 0xf1, 0x96, 0x36,
    0x60, 0x42, 0x99, 0x95, 0xf0, 0xe3, 0x81, 0xc6,
  }};
static const rosidl_type_hash_t unitree_api__msg__RequestLease__EXPECTED_HASH = {1, {
    0x16, 0xb5, 0xc2, 0x25, 0x7d, 0x52, 0x80, 0xa0,
    0x95, 0xe3, 0xe4, 0xfe, 0x26, 0xa4, 0x8e, 0x78,
    0x2e, 0x29, 0x4f, 0xa3, 0xd6, 0x87, 0x60, 0xce,
    0x38, 0x59, 0x92, 0x60, 0xa3, 0x44, 0xbf, 0x4e,
  }};
static const rosidl_type_hash_t unitree_api__msg__RequestPolicy__EXPECTED_HASH = {1, {
    0x74, 0x2c, 0x36, 0x12, 0xb9, 0x91, 0xbe, 0x55,
    0x43, 0x0d, 0x18, 0x47, 0xaf, 0x4a, 0xfb, 0x2f,
    0x11, 0x90, 0x69, 0xf2, 0xe1, 0x6e, 0x3a, 0x21,
    0x43, 0xc6, 0x35, 0x2a, 0x94, 0xef, 0x35, 0xe4,
  }};
#endif

static char unitree_api__msg__RequestHeader__TYPE_NAME[] = "unitree_api/msg/RequestHeader";
static char unitree_api__msg__RequestIdentity__TYPE_NAME[] = "unitree_api/msg/RequestIdentity";
static char unitree_api__msg__RequestLease__TYPE_NAME[] = "unitree_api/msg/RequestLease";
static char unitree_api__msg__RequestPolicy__TYPE_NAME[] = "unitree_api/msg/RequestPolicy";

// Define type names, field names, and default values
static char unitree_api__msg__RequestHeader__FIELD_NAME__identity[] = "identity";
static char unitree_api__msg__RequestHeader__FIELD_NAME__lease[] = "lease";
static char unitree_api__msg__RequestHeader__FIELD_NAME__policy[] = "policy";

static rosidl_runtime_c__type_description__Field unitree_api__msg__RequestHeader__FIELDS[] = {
  {
    {unitree_api__msg__RequestHeader__FIELD_NAME__identity, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestHeader__FIELD_NAME__lease, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_api__msg__RequestLease__TYPE_NAME, 28, 28},
    },
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestHeader__FIELD_NAME__policy, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {unitree_api__msg__RequestPolicy__TYPE_NAME, 29, 29},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription unitree_api__msg__RequestHeader__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {unitree_api__msg__RequestIdentity__TYPE_NAME, 31, 31},
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestLease__TYPE_NAME, 28, 28},
    {NULL, 0, 0},
  },
  {
    {unitree_api__msg__RequestPolicy__TYPE_NAME, 29, 29},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
unitree_api__msg__RequestHeader__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {unitree_api__msg__RequestHeader__TYPE_NAME, 29, 29},
      {unitree_api__msg__RequestHeader__FIELDS, 3, 3},
    },
    {unitree_api__msg__RequestHeader__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&unitree_api__msg__RequestIdentity__EXPECTED_HASH, unitree_api__msg__RequestIdentity__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = unitree_api__msg__RequestIdentity__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_api__msg__RequestLease__EXPECTED_HASH, unitree_api__msg__RequestLease__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = unitree_api__msg__RequestLease__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&unitree_api__msg__RequestPolicy__EXPECTED_HASH, unitree_api__msg__RequestPolicy__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = unitree_api__msg__RequestPolicy__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "RequestIdentity identity\n"
  "RequestLease lease\n"
  "RequestPolicy policy";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
unitree_api__msg__RequestHeader__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {unitree_api__msg__RequestHeader__TYPE_NAME, 29, 29},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 64, 64},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
unitree_api__msg__RequestHeader__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *unitree_api__msg__RequestHeader__get_individual_type_description_source(NULL),
    sources[1] = *unitree_api__msg__RequestIdentity__get_individual_type_description_source(NULL);
    sources[2] = *unitree_api__msg__RequestLease__get_individual_type_description_source(NULL);
    sources[3] = *unitree_api__msg__RequestPolicy__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
