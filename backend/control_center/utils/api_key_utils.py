# File: api_key_utils.py
# Copyright (C) 2025 Taurine Technology
#
# This file is part of the SDN Launch Control project.
#
# This project is licensed under the GNU General Public License v3.0 (GPL-3.0),
# available at: https://www.gnu.org/licenses/gpl-3.0.en.html#license-text
#
# Contributions to this project are governed by a Contributor License Agreement (CLA).
# By submitting a contribution, contributors grant Taurine Technology exclusive rights to
# the contribution, including the right to relicense it under a different license
# at the copyright owner's discretion.
#
# Unless required by applicable law or agreed to in writing, software distributed
# under this license is provided "AS IS", WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the GNU General Public License for more details.
#
# For inquiries, contact Keegan White at keeganwhite@taurinetech.com.

"""
Utility functions for creating and managing API keys.

This module provides helper functions for programmatic API key creation,
primarily for use during device setup and configuration.
"""

from rest_framework_api_key.models import APIKey
from typing import Tuple


def create_api_key(name: str, revoked: bool = False) -> Tuple[APIKey, str]:
    """
    Create a new API key programmatically.
    
    This function is useful for creating API keys during device setup,
    switch configuration, or other automated processes.
    
    Args:
        name: A descriptive name for the API key (e.g., "switch-192.168.1.10")
        revoked: Whether the key should be created in a revoked state (default: False)
    
    Returns:
        A tuple containing:
        - The APIKey model instance
        - The plaintext API key (only available at creation time)
    
    Example:
        >>> api_key, key = create_api_key("switch-192.168.1.10")
        >>> print(f"Created key: {key}")
        >>> # Store 'key' securely on the switch
    """
    api_key, key = APIKey.objects.create_key(name=name, revoked=revoked)
    return api_key, key


