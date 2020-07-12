#!/usr/bin/python

"""
Generic MQTT Driver for WEEWX
Requires the paho mqtt client package to listen on publications from specified MQTT Server.
Reference the weewx.conf file section for this driver to identify the configuration parameters. 
    poll_interval = 10
    host = mqtt-server-hostname
    username = needuser
    password = needpassword
    topic = pws/+

Note the base topic is 'pws'. The subtopics must be compliant with the
standard generic weewx parameter names (listed in the weewx.conf file).
Listed here is an excerpt of the parameters that have been tested.
                barometer = Barometer
                dewpoint = Dew Point
                ET = ET
                outHumidity = Humidity
                outTemp = Outside Temperature
                radiation = Radiation
                rain = Rain
                rainRate = Rain Rate
                UV = UV Index
                windSpeed = Wind Speed

An example of publishing from Home Assistant Automation:

automation:
  - alias: "Publish BME280 Data"
    trigger: 
        platform: state
        entity_id:
          - sensor.ws_temp
          - sensor.ws_relative_humity
          - sensor.ws_pres
    action:
      - service: mqtt.publish
        data_template:
            topic: 'pws/outTemp'
            payload: "{{ states('sensor.ws_temp')|float }}"
      - service: mqtt.publish
        data_template:
            topic: 'pws/outHumidity'
            payload: "{{ states('sensor.ws_relative_humity')|float }}"
      - service: mqtt.publish
        data_template:
            topic: 'pws/barometer'
            payload: "{{ states('sensor.ws_pres')|float }}"


"""
import logging
import sys
import time
import queue
import paho.mqtt.client as mqtt

import weeutil.logger
import weeutil.weeutil
import weewx.wxformulas
import weewx.drivers

# use standard python logging infrastructure
# reviewing weeutil.logger, weewx is designed to work with this
# visit the weewx.conf file, set debug=1 to enable debug level logs
log = logging.getLogger(__name__)

# driver name must match the section title in weewx.conf
DRIVER_NAME = 'GenMqtt'
DRIVER_VERSION = "0.1"

# required to integrate into the weewx framework
def loader(config_dict, engine):
    return GenericMqttDriver(**config_dict[DRIVER_NAME])


class GenericMqttDriver(weewx.drivers.AbstractDevice):
    """Define Class for Generic MQTT Driver deriving from weewx base class
       This implementation is based off of the wxMesh driver. Unlike wxMesh
       this driver does not allow mapping from one label space to another.

       This driver is a minimal implementation and only implements a minimal
       set of class methods as defined by the AbstraceDevice class.
    """

    def __init__(self, **stn_dict):
      """ Constructor will extract the required parameters
          and connect to the MQTT server
      """
      self.host = stn_dict.get('host', 'localhost')
      self.topic = stn_dict.get('topic', 'weather')
      self.username = stn_dict.get('username', 'no default')
      self.password = stn_dict.get('password', 'no default')
      self.client_id = stn_dict.get('client', 'wxclient') # MQTT client id - adjust as desired
      
      # how often to poll the weather data file, seconds
      self.poll_interval = float(stn_dict.get('poll_interval', 5.0))

      log.info('driver version is %s' % DRIVER_VERSION)

      log.info("MQTT host is %s" % self.host)
      log.info("MQTT topic is %s" % self.topic)
      log.info("MQTT client is %s" % self.client_id)
      log.info("polling interval is %s" % self.poll_interval)
      
      self.mqtt_queue = queue.Queue()
      self.connected = False

      self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv31)

      # TODO - need some reconnect on disconnect logic
      #self.client.on_disconnect = self.on_disconnect
      self.client.on_message = self.on_message

      self.client.username_pw_set(self.username, self.password)
      self.client.connect(self.host, 1883, 60)
      
      log.debug("Connected")
      self.client.loop_start()
      self.client.subscribe(self.topic, qos=1)

    @property
    def hardware_name(self):
        return DRIVER_NAME

    def on_message(self, client, userdata, msg):
      """ callback for when a PUBLISH message is received from the MQTT server
          each message is queued for processing by the genLoopPackets method.
      """
      self.mqtt_queue.put([msg.topic, float(msg.payload)])
      log.debug("Added to queue of %d message %s:%s" % (self.mqtt_queue.qsize(), msg.topic, msg.payload))

    def on_connect(self, client, userdata, rc):
      if rc == 0:
          self.connected = True
        
    def closePort(self):
      self.client.disconnect()
      self.client.loop_stop()


    def genLoopPackets(self):
      """ Build the basic loop packet for the weewx framework. This method will create a 
          new looppacket (python dictionary) with the units and dateTime entries. It will
          add additional entries as is available in the processing queue (published messages
          received from MQTT).

          No validation is done on the topics received from MQTT. Only success path testing
          has been done at this time.
      """
      _packet = None
      while True:
        while not self.mqtt_queue.empty():
          log.debug("Processing queue of %d entries" % self.mqtt_queue.qsize())
          if _packet is None:
              _packet = {'usUnits': weewx.US, 'dateTime': int(time.time())}
          while True:
            try:
              topic = self.mqtt_queue.get_nowait()
            except queue.Empty:
              break
            log.debug("processing topic : %s" % (topic))
            key = topic[0].split('/')[1]
            value = topic[1]
            _packet[key] = value

        if _packet is not None:
            if  'outTemp' in _packet and 'outHumidity' in _packet:
                _packet['dewpoint'] = weewx.wxformulas.dewpointC(_packet['outTemp'], _packet['outHumidity'])
            log.debug("yielding loop packet with %d entries" % (len(_packet)))
            loop_packet = _packet
            _packet = None
            yield loop_packet
        else:
            log.debug("sleeping for %d secs" % (self.poll_interval))
            time.sleep(self.poll_interval)
        

