# Test Suite Overview

This directory contains a lightweight set of tests for the RockAuto API.  The
focus is on quickly validating the most important pieces of functionality
without hitting the real RockAuto website.  These tests run fast and can be
executed as part of development or in CI.

* `test_basic.py` - Smoke tests for the root endpoint and the part number search
  logic.  Network calls are mocked so the tests run offline.

## Extending the suite

Additional tests can be appended by creating new `test_*.py` modules in this
folder.  When adding more tests, prefer mocking external network requests so the
suite remains fast.  A more comprehensive set of integration tests can live in a
separate directory once the basic suite is stable.
