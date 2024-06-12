from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
from rest_framework.response import Response
from rest_framework import status
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError


class MeterListView(APIView):
    def get(self, request, lan_ip_address):
        try:
            validate_ipv4_address(lan_ip_address)
            url = f"http://{lan_ip_address}:8181/onos/v1/meters/"

            # Make API call
            response = requests.get(
                url=url,
                auth=HTTPBasicAuth('onos', 'rocks')
            )
            url_devices = f"http://{lan_ip_address}:8181/onos/v1/devices"
            response_devices = requests.get(
                url=url_devices,
                auth=HTTPBasicAuth('onos', 'rocks')
            )
            device_response_json = response_devices.json()
            devices = device_response_json.get('devices')
            meters = []
            for meter in response.json().get('meters'):
                band_details = meter.get('bands')[0]
                band_type = band_details.get('type')
                switch_ip = '0.0.0.0'
                for device in devices:
                    annotations = device.get('annotations')
                    device_id = device.get('id')
                    if device_id == meter.get('deviceId'):
                        switch_ip = annotations.get('managementAddress')

                if band_type == 'DROP':
                    rate = band_details.get('rate')
                    device_id = meter.get('deviceId')

                    m_id = meter.get('id')
                    state = meter.get('state')
                    unit = meter.get('unit')
                    if unit == 'KB_PER_SEC':
                        unit = 'kbs'
                    m = {
                        'id': m_id,
                        'type': 'drop',
                        'ip': switch_ip,
                        'rate': f'{rate}',
                        'unit': f'{unit}',
                        'device_id': f'{device_id}',
                        'state': f'{state}'
                    }
                    meters.append(m)

            return Response({"status": "success", "meters": meters}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response({"status": "error", "message": "Invalid IP address format."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('CAUGHT AN UNEXPECTED ERROR')
            print(e)
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateMeterView(APIView):
    def post(self, request):
        try:
            data = request.data
            controller_ip = data.get('controller_ip')
            switch_ip = data.get('switch_ip')
            rate = data.get('rate')
            url = f"http://{controller_ip}:8181/onos/v1/devices"
            response = requests.get(
                url=url,
                auth=HTTPBasicAuth('onos', 'rocks')
            )
            response_json = response.json()
            device_id = None
            devices = response_json.get('devices')
            for device in devices:
                annotations = device.get('annotations')
                if annotations.get('managementAddress') == switch_ip:
                    device_id = device.get('id')
            if device_id:
                device_id_encoded = urllib.parse.quote(device_id, safe='')
                url = f"http://{controller_ip}:8181/onos/v1/meters/{device_id_encoded}"
                payload = {
                    "deviceId": device_id,
                    "unit": "KB_PER_SEC",
                    "burst": False,
                    "bands": [
                        {
                            "type": "DROP",
                            "rate": rate,
                            "burstSize": "0",
                            "prec": "0"
                        }
                    ]
                }
                response = requests.post(
                    url=url,
                    json=payload,
                    headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                    auth=HTTPBasicAuth('onos', 'rocks')
                )
                if response.status_code == 201:
                    return JsonResponse({'message': 'Successfully created meter'}, status=201)
                else:
                    return JsonResponse({'error': 'Failed to create meter on ONOS server'}, status=500)

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def delete_meter(request):
    device_id = request.data.get('deviceId', None)
    meter_id = request.data.get('meterId', None)

    if not device_id or not meter_id:
        return JsonResponse({'error': 'Missing deviceId or meterId in request data'}, status=400)

    device_id_encoded = urllib.parse.quote(device_id, safe='')  # URL encode the device ID
    print(device_id)
    print(meter_id)
    url = f"http://127.0.0.1:8181/onos/v1/meters/{device_id_encoded}/{meter_id}"
    print(url)
    response = requests.delete(
        url=url,
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('onos', 'rocks')
    )
    print(response.text)
    if response.status_code == 204:  # Depending on the server, it may return 204 for a successful delete
        return JsonResponse({'message': 'Meter deleted successfully'}, status=200)
    else:
        print(response)
        return JsonResponse({'error': 'Failed to delete meter on ONOS server'}, status=500)


@api_view(['GET'])
def get_device_details(request):
    device_id = request.GET.get('deviceId', None)
    print(device_id)
    url = "http://127.0.0.1:8181/onos/v1/devices/"
    if device_id:
        device_id_encoded = urllib.parse.quote(device_id, safe='')  # URL encode the device ID
        url = f"http://127.0.0.1:8181/onos/v1/devices/{device_id_encoded}"

    response = requests.get(
        url=url,
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('onos', 'rocks')
    )
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
def get_port_details(request):
    device_id = request.GET.get('deviceId', None)
    print(device_id)
    if device_id:
        device_id_encoded = urllib.parse.quote(device_id, safe='')  # URL encode the device ID
        url = f"http://127.0.0.1:8181/onos/v1/devices/{device_id_encoded}/ports"
        response = requests.get(
            url=url,
            headers={'Accept': 'application/json'},
            auth=HTTPBasicAuth('onos', 'rocks')
        )
        return Response(response.json(), status=response.status_code)
    else:
        return JsonResponse({'error': 'Failed to get device port details on ONOS server'}, status=500)


@api_view(['POST'])
def delete_flows(request):
    app_id = request.data.get('appId', None)
    if not app_id:
        return JsonResponse({'error': 'Missing App ID in request data'}, status=400)

    app_id_encoded = urllib.parse.quote(app_id, safe='')  # encode
    print(app_id)
    url = f"http://127.0.0.1:8181/onos/v1/flows/application/{app_id}"
    print(url)
    response = requests.delete(
        url=url,
        headers={'Accept': 'application/json'},
        auth=HTTPBasicAuth('onos', 'rocks')
    )
    print(response.text)
    if response.status_code == 204:  # Depending on the server, it may return 204 for a successful delete
        return JsonResponse({'message': 'Flows deleted successfully'}, status=200)
    else:
        print(response)
        return JsonResponse({'error': 'Failed to delete flows on ONOS server'}, status=500)