 #!/usr/bin/python



import logging
import sys
import time
import queue
import paho.mqtt.client as mqtt

import weeutil.logger
import weeutil.weeutil
import weewx.wxformulas
import weewx.drivers

log = logging.getLogger(__name__)
DRIVER_NAME = 'GenMqtt'
DRIVER_VERSION = "0.1"

def _get_as_float(d, s):
    v = None
    if s in d:
        try:
            v = float(d[s])
        except ValueError as e:
            log.error("cannot read value for '%s': %s" % (s, e))
    return v

def loader(config_dict, engine):
    return GenericMqttDriver(**config_dict[DRIVER_NAME])

# flags for enabling/disabling debug verbosity
DEBUG_COMM = 0
DEBUG_CONFIG_DATA = 0
DEBUG_WEATHER_DATA = 0
DEBUG_HISTORY_DATA = 0
DEBUG_DUMP_FORMAT = 'auto'

class GenericMqttDriver(weewx.drivers.AbstractDevice):
    """weewx driver that sources data from MQTT Server"""

    def __init__(self, **stn_dict):
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
      # TODO is this a good idea?
      # while self.connected != True:
      #    time.sleep(1)
      #    logdbg("Connecting...\n")
      
      log.debug("Connected")
      self.client.loop_start()
      self.client.subscribe(self.topic, qos=1)

    @property
    def hardware_name(self):
        return DRIVER_NAME

    # The callback for when a PUBLISH message is received from the MQTT server.
    def on_message(self, client, userdata, msg):
      self.mqtt_queue.put([msg.topic, float(msg.payload)])
      log.debug("Added to queue of %d message %s:%s" % (self.mqtt_queue.qsize(), msg.topic, msg.payload))

    def on_connect(self, client, userdata, rc):
      if rc == 0:
          self.connected = True
        
    def closePort(self):
      self.client.disconnect()
      self.client.loop_stop()


    def genLoopPackets(self):
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
        

