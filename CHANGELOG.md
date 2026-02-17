# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-17

### Added

- Initial release of django-role-based-masking
- Role-based field masking for Django REST Framework serializers
- Built-in masking strategies:
  - `full`: Mask entire string
  - `partial_last`: Keep last N characters, mask rest
  - `email`: Mask email local-part except first character
  - `percentage`: Mask percentage of string length
  - `noop`: No masking (passthrough)
- Support for nested serializer masking with dotted path notation
- Custom callable strategy support
- `RoleMaskedSerializerMixin` for easy integration
- `RoleMaskedModelSerializer` and `RoleMaskedSerializer` base classes
- Configurable settings via Django settings:
  - `DRM_ROLE_ATTR`: Role attribute path (default: "role")
  - `DRM_MASK_CHAR`: Masking character (default: "\*")
  - `DRM_DEFAULT_STRATEGY`: Default strategy (default: "full")
- Comprehensive test suite with pytest
- Documentation and usage examples
- Support for Python 3.10+, Django 3.2+, DRF 3.14+

[0.1.0]: https://github.com/gaikwadakshay79/django-role-based-masking/releases/tag/v0.1.0
