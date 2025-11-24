# File: permissions.py
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
Custom permission classes for DRF API key authentication.

This module provides permission classes that combine API key authentication
with standard DRF authentication methods.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class HasAPIKeyOrIsAuthenticated(BasePermission):
    """
    Permission class that allows access if either:
    1. A valid API key is provided, OR
    2. The user is authenticated via standard DRF authentication
    
    This is useful for endpoints that need to accept requests from both:
    - Automated systems using API keys (e.g., switches, monitoring scripts)
    - Web UI users authenticated with tokens
    """
    
    def has_permission(self, request, view):
        # Check API key permission first
        api_key_permission = HasAPIKey()
        if api_key_permission.has_permission(request, view):
            return True
        
        # Fall back to standard authentication
        auth_permission = IsAuthenticated()
        return auth_permission.has_permission(request, view)

