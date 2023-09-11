"""Процесс для постоянного чтения кадров с камеры"""
import multiprocessing as mp
import subprocess
import time
from enum import Enum
import numpy as np
import logging
import re
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)


class StreamMode(Enum):
    """Перечисления состояний камеры"""
    INIT_STREAM = 1
    SETUP_STREAM = 1
    READ_STREAM = 2


class StreamCommands(Enum):
    """Перечисление команд камеры"""
    FRAME = 1
    ERROR = 2
    HEARTBEAT = 3
    RESOLUTION = 4
    STOP = 5

class Stream(mp.Process):
    """Класс для чтения потока с камеры.

    """
    def __init__(self, link: str, stop: mp.Event(), out_queue: mp.Queue, framerate: int):
        super().__init__()
        self.src = link
        self.stop = stop
        self.out_queue = out_queue
        self.framerate = framerate
        self.current_state = StreamMode.INIT_STREAM
        self.pipeline = None
        self.source = None
        self.queue = None
        self.decode = None
        self.convert = None
        self.sink = None
        self.image_arr = None
        self.newImage = False
        self.frame1 = None
        self.frame2 = None
        self.num_unexpected_tot = 40
        self.unexpected_cnt = 0
        self.cam_status = False
        self.counter = 0

    def gst_to_opencv(self, sample):
        """
        Метод для получения кадра из объекта GStreamer

        Returns:
            np.array: Изображение в формате np.array

        """
        buf = sample.get_buffer()
        caps = sample.get_caps()

        arr = np.ndarray(
            (caps.get_structure(0).get_value('height'),
             caps.get_structure(0).get_value('width'),
             3),
            buffer=buf.extract_dup(0, buf.get_size()),
            dtype=np.uint8)
        return arr

    def new_buffer(self, sink, _):
        """
        Call back метод для получения нового кадра с камеры
        """
        sample = sink.emit("pull-sample")
        arr = self.gst_to_opencv(sample)
        self.image_arr = arr
        self.newImage = True
        return Gst.FlowReturn.OK

    def find_ip(self):
        """
        Метод поиска ip адреса в адресе камеры.
        Адрес имеет вид: rtsp://login:password@8.8.8.8:port/channel
        """
        return re.findall(r'[0-9]+(?:\.[0-9]+){3}', self.src)[0]

    def test_src(self):
        """
        Метод проверки ip адреса
        Возвращает True, если подключение по адресу есть и False, если подключение отсутствует
        """
        ip = self.find_ip()
        response = os.system(f"ping -c 1 {ip}")
        if response == 0:
            return True
        else:
            return False

    def get_codec(self):
        """
        Тестовый метод для получения нужного кодека из параметров видеопотока камеры
        В текущей версии ПО не работает
        """
        stream_info = subprocess.run(f'gst-discoverer-1.0  {self.src}', shell=True, stdout=subprocess.PIPE)

        stream_info = stream_info.stdout.decode("utf-8")

        for data in stream_info.split('\n'):
            if 'video: ' in data:
                if 'h.264' in data.lower():
                    return 'rtph264depay', 'avdec_h264'

                if 'h.265' in data.lower():
                    return 'rtph265depay', 'avdec_h265'

        return None, None

        # codec_matching = {'H-264': ['rtph264depay', }

    def create_stream(self):
        """
        Метод инициализации pipeline камеры
        Returns:
            bool: Статус создания
        """
        # Test src
        if not self.test_src():
            self.stop.set()
            return False

        codec, decoder = self.get_codec()

        if codec is None:
            return False

        # Create the empty pipeline
        command = 'rtspsrc name=m_rtspsrc ! ' \
                  f'{codec} name=m_rtph264depay ! ' \
                  'queue name=m_queue !' \
                  'vpudec name=m_avdech264 ! '\
                  'videoconvert name=m_videoconvert ! '\
                  'videorate name=m_videorate ! '\
                  'appsink name=m_appsink'


        try:
            self.pipeline = Gst.parse_launch(command)
        except Exception as e:
            logging.info(e)
            command = 'rtspsrc name=m_rtspsrc ! ' \
                      f'{codec} name=m_rtph264depay ! ' \
                      'queue name=m_queue !' \
                      f'{decoder} name=m_avdech264 ! ' \
                      'videoconvert name=m_videoconvert ! ' \
                      'videorate name=m_videorate ! ' \
                      'appsink name=m_appsink'

            self.pipeline = Gst.parse_launch(command)

            self.decode = self.pipeline.get_by_name('m_avdech264')
            self.decode.set_property('max-threads', 2)
            self.decode.set_property('output-corrupt', 'false')

        # source params
        self.source = self.pipeline.get_by_name('m_rtspsrc')
        self.source.set_property('latency', 0)
        self.source.set_property('location', self.src)
        self.source.set_property('protocols', 'tcp')
        self.source.set_property('retry', 50)
        self.source.set_property('timeout', 50)
        self.source.set_property('tcp-timeout', 5000000)
        self.source.set_property('drop-on-latency', 'true')

        # queue params
        self.queue = self.pipeline.get_by_name('m_queue')
        self.queue.set_property('max-size-buffers', 10)
        self.queue.set_property('leaky', 1)

        # decode params
        self.decode = self.pipeline.get_by_name('m_avdech264')

        # convert params
        self.convert = self.pipeline.get_by_name('m_videoconvert')

        # framerate parameters
        self.framerate_ctr = self.pipeline.get_by_name('m_videorate')
        # self.framerate_ctr.set_property('max-rate', self.framerate / 1)
        # self.framerate_ctr.set_property('drop-only', 'true')

        # sink params
        self.sink = self.pipeline.get_by_name('m_appsink')

        # Maximum number of nanoseconds that a buffer can be late before it is dropped (-1 unlimited)
        # flags: readable, writable
        # Integer64. Range: -1 - 9223372036854775807 Default: -1
        self.sink.set_property('max-lateness', 500000000)

        # The maximum number of buffers to queue internally (0 = unlimited)
        # flags: readable, writable
        # Unsigned Integer. Range: 0 - 4294967295 Default: 0
        self.sink.set_property('max-buffers', 5)

        # Drop old buffers when the buffer queue is filled
        # flags: readable, writable
        # Boolean. Default: false
        self.sink.set_property('drop', 'true')

        # Emit new-preroll and new-sample signals
        # flags: readable, writable
        # Boolean. Default: false
        self.sink.set_property('emit-signals', True)

        # # sink.set_property('drop', True)
        self.sink.set_property('sync', False)

        # The allowed caps for the sink pad
        # flags: readable, writable
        # Caps (NULL)
        caps = Gst.caps_from_string(
            'video/x-raw, format=(string){BGR, GRAY8}; video/x-bayer,format=(string){rggb,bggr,grbg,gbrg}')
        self.sink.set_property('caps', caps)

        if not self.source or not self.sink or not self.pipeline or not self.decode or not self.convert:
            logging.error("Not all elements could be created.")
            self.stop.set()
            return False

        self.sink.connect("new-sample", self.new_buffer, self.sink)

        self.cam_status = True
        return True

    def reconnect(self):
        """
        Метод для переподключения к камере

        Returns:
            bool: Статус переподключения
        """
        logging.info(f'Try to reconnect for {self.counter} time')

        status = self.create_stream()
        if not status and self.counter <= 3:
            self.counter += 1
            logging.error('Cant create pipeline, try another time')
            time.sleep(3)
            return self.reconnect()

        if not status:
            logging.error('Stream is broken, stop work')
            self.out_queue.put((StreamCommands.ERROR, None), block=False)
            return False

        else:
            logging.info('Stream was reconnect! Start stream')
            ret = self.pipeline.set_state(Gst.State.PLAYING)
            if ret == Gst.StateChangeReturn.FAILURE:
                logging.error("Unable to set the pipeline to the playing state.")
                self.out_queue.put((StreamCommands.ERROR, None), block=False)
                return False

            return True

    def run(self):
        """
        Основной поток процесса, описывает событийный цикл
        """
        # Start playing

        self.create_stream()

        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            logging.error("Unable to set the pipeline to the playing state.")
            self.stop.set()
            return False

        # Wait until error or EOS
        bus = self.pipeline.get_bus()
        logging.info('start stream')
        last_frame_time = time.monotonic()
        while not self.stop.is_set():
            current_time = time.monotonic()

            message = bus.timed_pop_filtered(10000, Gst.MessageType.ANY)
            # print "image_arr: ", image_arr
            if self.image_arr is not None and self.newImage:
                last_frame_time = time.monotonic()
                if not self.out_queue.full():
                    self.out_queue.put((StreamCommands.FRAME, self.image_arr), block=False)

                else:
                    while not self.out_queue.empty():
                        try:
                            _ = self.out_queue.get(block=False)
                        except Exception as e:
                            pass

                self.image_arr = None
                self.unexpected_cnt = 0

            if message:
                if message.type == Gst.MessageType.ERROR:
                    err, debug = message.parse_error()
                    logging.error("Error received from element %s: %s" % (
                        message.src.get_name(), err))
                    logging.error("Debugging information: %s" % debug)
                    self.pipeline.set_state(Gst.State.PAUSED)
                    self.pipeline.set_state(Gst.State.NULL)
                    self.reconnect()
                    current_time = time.monotonic()
                    last_frame_time = time.monotonic()

                elif message.type == Gst.MessageType.EOS:
                    logging.info("End-Of-Stream reached, try to reconnect")
                    self.pipeline.set_state(Gst.State.PAUSED)
                    self.pipeline.set_state(Gst.State.NULL)
                    self.reconnect()
                    current_time = time.monotonic()
                    last_frame_time = time.monotonic()

                elif message.type == Gst.MessageType.STATE_CHANGED:
                    if isinstance(message.src, Gst.Pipeline):
                        old_state, new_state, pending_state = message.parse_state_changed()
                        logging.info("Pipeline state changed from %s to %s." %
                              (old_state.value_nick, new_state.value_nick))

                else:
                    logging.warning(f"Unexpected message received: {message.type}")
                    self.unexpected_cnt = self.unexpected_cnt + 1

                    if self.unexpected_cnt == self.num_unexpected_tot:
                        logging.error('Collect {self.num_unexpected_tot} unexpected message, stop stream!')
                        self.out_queue.put((StreamCommands.ERROR, None), block=False)
                        break

            if current_time - last_frame_time >= 10:
                logging.error('Big latency, close stream!')
                self.pipeline.set_state(Gst.State.PAUSED)
                self.pipeline.set_state(Gst.State.NULL)
                self.reconnect()
                current_time = time.monotonic()
                last_frame_time = time.monotonic()

                # self.out_queue.put((StreamCommands.ERROR, None), block=False)

        logging.info('terminating cam pipe')

        self.pipeline.set_state(Gst.State.PAUSED)
        self.pipeline.set_state(Gst.State.NULL)

        logging.info('close stream')
