# SDN Launch Control AKA Launch Control
Install, manage and do everything Open vSwitch and SDN.

Launch Control is a central management tool for software defined networking (SDN) built to enable easy and automated adoption/installation of the SDN paradigm into new or pre-existing networks.

## Documentation

### Feature Set
Find details about the feature set [here](FEATURES.md).

### Errors
Find details about errors and debugging [here](docs/ERRORS.md).

### Controllers
Find documentation on the controllers [here](docs/CONTROLLERS.md).

## Running this code

### Dependencies
1. To run the backend you need to install Ansible, ansible galaxy collections in requirements.yml, openssh, sshpass, Python 
requirements in requirements.txt locally using the convenience script in the [backend folder](backend/control_center). To install it them: 
run the script in this folder: `./install.sh`
2. To run the frontend you need the NPM packages installed. Navigate to [ui/control-center](ui/control-center) and run 
the convenience script: `./install.sh`

### Running from Source
1. Install the dependencies. 
2. Activate the virtual environment: `source venv/bin/activate`
3. Navigate to the [backend folder](backend/control_center) to start the Django server, make the necessary migrations and create an admin user:
```
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
4. Navigate the [frontend folder](ui/control-center) to install the UI packages and start the frontend:
```
npm install
npm start
```
5. Navigate to the UI [here](http://localhost:3000) and the backend [here](http://127.0.0.1:8000/admin).

### Run from Convenience Script
1. To start the backend navigate to the [backend/control_center](backend/control_center) and run the 
[run.sh](backend/control_center/run.sh) script `./run.sh`. You will still need to run the migrations and create a user:
```
python manage.py createsuperuser
```
2. To start the UI navigate to [ui/control-center](ui/control-center) and run the [run.sh](ui/control-center/run.sh) script `./run.sh` 

## Contribute
Find out what we are doing and what needs to be done [here](https://trello.com/b/IVWKfVkB/launch-control). Email
keeganwhite@taurinetech.com to contribute or open a draft pull request.

ovs-vsctl set bridge br1 other-config:datapath-id=00:00:66:b1:6d:f7:a7:45
ovs-ofctl -OOpenFlow13 --names --no-stat dump-flows
ovs-ofctl -OOpenFlow13 --no-names --sort dump-flows
ovs-ofctl -OOpenFlow13 diff-flows

dump flows: ovs-ofctl -OOpenFlow13 --names --no-stat dump-flows faucet \
| sed 's/cookie=0x5adc15c0, //'

save flows: ovs-ofctl -OOpenFlow13 --no-names --sort dump-flows faucet > flows_og

diff flows: ovs-ofctl -OOpenFlow13 diff-flows flows_og faucet | sed 's/cookie=0x5adc15c0 //'