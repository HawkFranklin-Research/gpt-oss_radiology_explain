# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import patch
import importlib
import os
# Import module under test. Initial load uses actual or globally patched dependencies.
import cache_store

class TestCacheStore(unittest.TestCase):

    @patch('diskcache.Cache')
    @patch('os.getenv')
    def test_cache_directory_env_var_set(self, mock_os_getenv, mock_DiskCache_class):
        expected_dir = '/custom/cache/path'

        # Mock os.getenv for this test.
        def getenv_side_effect_set(key, default=None):
            if key == 'CACHE_DIR':
                return expected_dir
            return os.environ.get(key, default) # Fallback for other env var calls.
        mock_os_getenv.side_effect = getenv_side_effect_set

        # Reload cache_store to apply method-specific mocks.
        importlib.reload(cache_store)

        # Check os.getenv call by cache_store.py.
        mock_os_getenv.assert_any_call('CACHE_DIR', '/app/cache_dir')
        # Check diskcache.Cache initialization with the expected directory.
        mock_DiskCache_class.assert_called_once_with(expected_dir)

    @patch('diskcache.Cache')
    @patch('os.getenv')
    def test_cache_directory_env_var_not_set(self, mock_os_getenv, mock_DiskCache_class):
        # Mock os.getenv: simulate 'CACHE_DIR' not set, so it returns the default.
        def getenv_side_effect_not_set(key, default=None):
            if key == 'CACHE_DIR':
                # 'default' will be '/app/cache_dir' from cache_store.py's call
                return default
            return os.environ.get(key, default) # Fallback for other env vars
        mock_os_getenv.side_effect = getenv_side_effect_not_set

        # Reload cache_store to apply method-specific mocks.
        importlib.reload(cache_store)

        # Check os.getenv call by cache_store.py.
        mock_os_getenv.assert_any_call('CACHE_DIR', '/app/cache_dir')
        # Check diskcache.Cache initialization with the default directory.
        mock_DiskCache_class.assert_called_once_with('/app/cache_dir')

if __name__ == '__main__':
    unittest.main()
