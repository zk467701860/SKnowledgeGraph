# _*_ coding: utf-8 _*_
import logging
import os.path
import time
import traceback

from flask import request

from db.engine_factory import EngineFactory
from db.model import Log


class Logger(object):
    def __init__(self, logger):
        '''''
            Specify the file path to save the log, log level, and call file
             Save the log to the specified file
        '''

        # create logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # create one handler，used to write log
        rq = logger + time.strftime('%Y%m%d', time.localtime(time.time()))
        log_path = os.path.dirname(os.getcwd()) + '/Logs/'  # get project dir/Logs to save the log
        # log_path = os.path.dirname(os.path.abspath('.')) + '/logs/'
        log_name = log_path + rq + '.log'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        if not os.path.exists(log_name):
            team = open(log_name, 'w')
            team.close()
        fh = logging.FileHandler(log_name)
        fh.setLevel(logging.INFO)

        # create another handler，used to write to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # define handler output
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add handler to logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def get_log(self):
        return self.logger


class SQLAlchemyHandler(logging.Handler):
    def __init__(self, session=None):
        super(SQLAlchemyHandler, self).__init__()
        self.session = session

    def get_session(self):
        if not self.session:
            self.session = EngineFactory.create_log_session()

        return self.session

    def emit(self, record):
        print("emit log")
        trace = None
        exc = record.__dict__['exc_info']
        if exc:
            trace = traceback.format_exc(exc)

        path = request.path
        method = request.method
        ip = request.remote_addr

        log = Log(logger=record.__dict__['name'],
                  level=record.__dict__['levelname'],
                  trace=trace,
                  msg=record.__dict__['msg'],
                  path=path,
                  method=method,
                  ip=ip,
                  )
        session = self.get_session()
        session.add(log)

