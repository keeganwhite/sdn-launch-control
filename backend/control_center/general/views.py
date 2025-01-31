# File: views.py
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

from django.shortcuts import render
from django.shortcuts import get_list_or_404
from ovs_install.utilities.ansible_tasks import run_playbook
from ovs_install.utilities.utils import write_to_inventory, save_ip_to_config, save_bridge_name_to_config, \
    save_interfaces_to_config
import os
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from .models import Device, Port, Bridge
from django.shortcuts import get_object_or_404
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError
import logging
from .serializers import BridgeSerializer
from .models import Controller, Plugins
from .serializers import DeviceSerializer

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
logger = logging.getLogger(__name__)
test_connection = "test-connection"
playbook_dir_path = f"{parent_dir}/ansible/playbooks"
inventory_path = f"{parent_dir}/ansible/inventory/inventory"
config_path = f"{parent_dir}/ansible/group_vars/all.yml"
from .models import ClassifierModel


# *---------- Network Connectivity Methods ----------*
class CheckDeviceConnectionView(APIView):
    def get(self, request, lan_ip_address):
        try:
            validate_ipv4_address(lan_ip_address)
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            data = {
                "name": device.name,
                "device_type": device.device_type,
                'username': device.username,
                'password': device.password,
                "os_type": device.os_type,
                "lan_ip_address": device.lan_ip_address,
                "ports": device.num_ports,
                "ovs_enabled": device.ovs_enabled,
                "ovs_version": device.ovs_version,
                "openflow_version": device.openflow_version
            }
            write_to_inventory(lan_ip_address, data.get('username'), data.get('password'), inventory_path)
            save_ip_to_config(lan_ip_address, config_path)
            result = run_playbook(test_connection, playbook_dir_path, inventory_path)
            if result['status'] == 'failed':
                print()
                return Response({'status': 'error', 'message': result['error']},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('CAUGHT AN UNEXPECTED ERROR')
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# *---------- Basic device get and post methods ----------*
class AddDeviceView(APIView):
    def post(self, request):
        try:
            data = request.data

            try:
                validate_ipv4_address(data.get('lan_ip_address'))
            except ValidationError:
                return Response({"status": "error", "message": "Invalid IP address format."},
                                status=status.HTTP_400_BAD_REQUEST)
            if data.get('ovs_enabled'):
                ovs_enabled = True
                ports = data.get('ports')
                ovs_version = data.get('ovs_version')
                openflow_version = data.get('openflow_version')
                device = Device.objects.create(
                    name=data.get('name'),
                    device_type=data.get('device_type'),
                    username=data.get('username'),
                    password=data.get('password'),
                    os_type=data.get('os_type'),
                    lan_ip_address=data.get('lan_ip_address'),
                    num_ports=ports,
                    ovs_enabled=ovs_enabled,
                    ovs_version=ovs_version,
                    openflow_version=openflow_version,
                )
            else:
                device = Device.objects.create(
                    name=data.get('name'),
                    device_type=data.get('device_type'),
                    username=data.get('username'),
                    password=data.get('password'),
                    os_type=data.get('os_type'),
                    lan_ip_address=data.get('lan_ip_address'),
                )

            device.save()
            return Response({"status": "success", "message": "Device added successfully."},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PluginListView(APIView):
    def get(self, request):
        try:
            plugins = Plugins.objects.all()
            data = [
                {
                    "alias": plugin.alias,
                    "name": plugin.name,
                    "version": plugin.version,
                    "short_description": plugin.short_description,
                    "long_description": plugin.long_description,
                    "author": plugin.author,
                    "installed": plugin.installed,
                } for plugin in plugins
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckPluginInstallation(APIView):

    def get(self, request, plugin_name):

        try:
            plugin = Plugins.objects.get(name=plugin_name)
            if plugin_name == 'tau-traffic-classification-sniffer':
                # Check if there are any devices associated with the plugin
                has_devices = plugin.target_devices.exists()
                return JsonResponse({'hasDevices': has_devices}, safe=False)
            else:
                installed = plugin.installed
                return Response({"message": installed},
                                status=status.HTTP_200_OK)
        except Plugins.DoesNotExist:
            return JsonResponse({'hasDevices': False}, safe=False)


class InstallPluginDatabaseAlterView(APIView):
    def post(self, request, plugin_name):
        try:
            plugin = Plugins.objects.get(name=plugin_name)
            plugin.installed = True
            plugin.save()
            return Response({"status": "success", "message": "Plugin installed successfully"},
                            status=status.HTTP_200_OK)
        except Plugins.DoesNotExist as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UninstallPluginDatabaseAlterView(APIView):
    def post(self, request, plugin_name):
        try:
            plugin = Plugins.objects.get(name=plugin_name)
            plugin.installed = False
            plugin.save()
            return Response({"status": "success", "message": "Plugin uninstalled successfully"},
                            status=status.HTTP_200_OK)
        except Plugins.DoesNotExist as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InstallPluginView(APIView):
    def post(self, request):
        try:
            data = request.data
            name = data.get('name')
            installed = data.get('installed')
            device_ip_address = data.get('lan_ip_address')
            validate_ipv4_address(device_ip_address)

            plugin = Plugins.objects.get(name=name)
            if installed:
                plugin.installed = True
                device = Device.objects.get(lan_ip_address=device_ip_address)
                if not plugin.target_devices.filter(id=device.id).exists():
                    print(f'adding {device.lan_ip_address}')
                    plugin.target_devices.add(device)
            else:
                plugin.installed = False
            plugin.save()
            return Response({"status": "success", "message": "Plugin installed successfully"},
                            status=status.HTTP_200_OK)
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Device.DoesNotExist:
            return Response({"status": "error", "message": "Device not found"}, status=status.HTTP_404_NOT_FOUND)
        except Plugins.DoesNotExist:
            return Response({"status": "error", "message": "Plugin not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceListView(APIView):
    def get(self, request):
        try:
            devices = Device.objects.all()
            data = [
                {
                    "name": device.name,
                    "device_type": device.device_type,
                    "os_type": device.os_type,
                    "lan_ip_address": device.lan_ip_address,
                    "ports": device.num_ports,
                    "ovs_enabled": device.ovs_enabled,
                    "ovs_version": device.ovs_version,
                    "openflow_version": device.openflow_version
                } for device in devices
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceDetailsView(APIView):
    def get(self, request, lan_ip_address):
        try:
            validate_ipv4_address(lan_ip_address)
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)

            data = {
                "name": device.name,
                "device_type": device.device_type,
                "os_type": device.os_type,
                "lan_ip_address": device.lan_ip_address,
                "ports": device.num_ports,
                "ovs_enabled": device.ovs_enabled,
                "ovs_version": device.ovs_version,
                "openflow_version": device.openflow_version
            }
            print(data)

            return Response({"status": "success", "device": data}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForceDeleteDeviceView(APIView):
    def delete(self, request):
        data = request.data
        try:
            validate_ipv4_address(data.get('lan_ip_address'))
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            lan_ip_address = data.get('lan_ip_address')
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            bridges = Bridge.objects.filter(device=device)

            # remove links to bridges if this device is a controller
            if Controller.objects.filter(device=device).exists():
                print(f'{Device.name} is a controller.')
                controller = get_object_or_404(Controller, device=device)
                associated_bridges = controller.bridges.all()
                if associated_bridges:
                    for bridge in associated_bridges:
                        print(f"Bridge Name: {bridge.name}, Device: {bridge.device.name}")
                        bridge_name = bridge.name
                        bridge_host_device = bridge.device
                        bridge_host_lan_ip_address = bridge_host_device.lan_ip_address
                        bridge.controller = None
                        bridge.save()
                device.delete()
            else:
                device.delete()

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)


class DeleteDeviceView(APIView):
    def delete(self, request):
        data = request.data
        try:
            validate_ipv4_address(data.get('lan_ip_address'))
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            lan_ip_address = data.get('lan_ip_address')
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            bridges = Bridge.objects.filter(device=device)

            # remove links to bridges if this device is a controller
            if Controller.objects.filter(device=device).exists():
                print(f'{Device.name} is a controller.')
                controller = get_object_or_404(Controller, device=device)
                associated_bridges = controller.bridges.all()
                for bridge in associated_bridges:
                    print(f"Bridge Name: {bridge.name}, Device: {bridge.device.name}")
                    bridge_name = bridge.name
                    bridge_host_device = bridge.device
                    bridge_host_lan_ip_address = bridge_host_device.lan_ip_address
                    save_bridge_name_to_config(bridge_name, config_path)
                    write_to_inventory(bridge_host_lan_ip_address, bridge_host_device.username,
                                       bridge_host_device.password, inventory_path)
                    save_ip_to_config(bridge_host_lan_ip_address, config_path)
                    delete_controller = run_playbook('remove-controller', playbook_dir_path, inventory_path)
                    if delete_controller.get('status') == 'success':
                        bridge.controller = None
                        bridge.save()
                    else:
                        return Response(
                            {'status': 'failed', 'message': 'Unable to remove controller from assosciated bridges'
                                                            ' due to external system failure.'},
                            status=status.HTTP_400_BAD_REQUEST)
            # delete bridges on the device
            if bridges:
                for b in bridges:
                    save_bridge_name_to_config(b.name, config_path)
                    write_to_inventory(lan_ip_address, device.username, device.password, inventory_path)
                    save_ip_to_config(lan_ip_address, config_path)
                    delete_bridge = run_playbook('ovs-delete-bridge', playbook_dir_path, inventory_path)
                    if delete_bridge.get('status') == 'success':
                        print(f'Bridge {b.name} successfully deleted on {device.name}')
                    else:
                        return Response({'status': 'error', 'message': f'unable to delete bridge {b.name}'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                device.delete()
            else:
                device.delete()

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateDeviceView(APIView):
    def put(self, request, lan_ip_address):
        try:
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            data = request.data

            # Update fields if they are present in the request
            for field in ['lan_ip_address', 'name', 'device_type', 'os_type', 'username', 'password', 'num_ports',
                          'ovs_enabled',
                          'ovs_version', 'openflow_version']:
                if field in data:
                    if field == 'lan_ip_address':
                        validate_ipv4_address(data[field])
                    setattr(device, field, data[field])

            # Validate and save the device
            device.full_clean()
            device.save()
            return Response({"status": "success", "message": "Device updated successfully."}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# *---------- OVS get and post methods ----------*
class DeviceBridgesView(APIView):
    def get(self, request, lan_ip_address):
        try:
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            bridges = device.bridges.all()
            if bridges.exists():
                serializer = BridgeSerializer(bridges, many=True)
                print(serializer.data)
                return Response({'status': 'success', 'bridges': serializer.data})
            else:
                return Response({'status': 'info', 'message': 'No bridges assigned to this device.'})
        except ValueError:
            return Response({'status': 'error', 'message': 'Invalid IP address format.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DevicePortsView(APIView):
    def get(self, request, lan_ip_address):
        try:
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            ports = Port.objects.filter(bridge__device=device)
            if ports.exists():
                ports_data = [{'name': port.name} for port in ports]
                return Response({'status': 'success', 'ports': ports_data})
            else:
                return Response({'status': 'info', 'message': 'No ports assigned to this device.'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class UnassignedDevicePortsView(APIView):
#     def get(self, request, lan_ip_address):
#         try:
#             ports_data = [{'name': port.name} for port in ports]
#             device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
#             ports = Port.objects.filter(bridge__device=device)
#             if ports.exists():
#                 for port in ports:
#                 ports_data = [{'name': port.name} for port in ports]
#                 return Response({'status': 'success', 'ports': ports_data})
#             else:
#                 return Response({'status': 'info', 'message': 'No ports assigned to this device.'})
#         except Exception as e:
#             return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# *---------- Controller get and post methods ----------*
class AddControllerView(APIView):
    def post(self, request):
        try:
            data = request.data
            lan_ip_address = data.get('lan_ip_address')
            validate_ipv4_address(lan_ip_address)
            device = get_object_or_404(Device, lan_ip_address=lan_ip_address)
            controller = Controller.objects.create(
                type=data.get('type'),
                device=device,
                lan_ip_address=lan_ip_address,
            )
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)


class ControllerListView(APIView):
    def get(self, request):
        try:
            controllers = Controller.objects.all()
            for controller in controllers:
                print(controller.switches.all())  # Check the output

            data = [
                {
                    "type": controller.type,
                    "device": controller.device.name,
                    "lan_ip_address": controller.device.lan_ip_address,
                    "switches": [
                        {
                            "name": switch.name,
                            "lan_ip_address": switch.lan_ip_address,
                        }
                        for switch in controller.switches.all()
                    ],
                } for controller in controllers
            ]

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ControllerSwitchList(APIView):
    def get(self, request, controller_ip):
        try:
            controller = Controller.objects.get(device__lan_ip_address=controller_ip)
            switches = controller.switches.all()
            serializer = DeviceSerializer(switches, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Controller.DoesNotExist:
            return Response({'error': 'Controller not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ONOSControllerListView(APIView):
    def get(self, request):
        try:
            onos_controllers = Controller.objects.filter(type='onos')

            lan_ips = [controller.device.lan_ip_address for controller in onos_controllers]
            return Response(lan_ips, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e, exc_info=True)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryListView(APIView):
    def get(self, request):
        try:
            classifier = ClassifierModel.objects.first()
            if classifier:
                return JsonResponse({'categories': classifier.categories}, status=200)
            else:
                return JsonResponse({'error': 'Classifier not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
