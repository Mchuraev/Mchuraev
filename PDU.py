# -*- coding: utf-8 -*-
# ========================================================
# класс управления устройстом питания , типа PDU
# от ATEN версии PE
# -
# Для корректной работы на linux необходимо установить
# следующие библиотеки libsnmp-dev
# ========================================================

from easysnmp import Session
from time import sleep
import argparse


class PDUSNMP:

    def __init__(self, hostname, socket, login):
        self.flag = 0
        if int(socket) < 9:
            self.socket = int(socket) + 1
        else:
            self.socket = int(socket) + 2
        self.mid_sk = f'.1.3.6.1.4.1.21317.1.3.2.2.2.2.{self.socket}.0'
        self.session = Session(hostname=hostname, community=login, version=2)

    def on(self):
        try:
            if self.session.get(self.mid_sk).value == '2':
                print('The socket is already on')
                return True
            elif self.session.get(self.mid_sk).value == '3':
                sleep(5)
                if self.flag > 3:
                    print('Время ожидания превышено')
                    self.flag = 0
                    return False
                self.flag += 1
                self.on()
            self.flag = 0
            return self.session.set(self.mid_sk, '2', 'INTEGER')
        except:
            print('Ошибка соединения, проверьте корректность данных и доступность стенда по порту 161')
            return False

    def off(self):
        try:
            if self.session.get(self.mid_sk).value == '1':
                print('The socket is already off')
                return True
            elif self.session.get(self.mid_sk).value == '3':
                sleep(5)
                if self.flag > 3:
                    print('Время ожидания превышено')
                    self.flag = 0
                    return False
                self.flag += 1
                self.off()
            self.flag = 0
            return self.session.set(self.mid_sk, '1', 'INTEGER')
        except:
            print('Ошибка соединения, проверьте корректность данных и доступность стенда по порту 161')
            return False

    def reboot(self):
        try:
            if self.session.get(self.mid_sk).value == '3':
                sleep(5)
                if self.flag > 3:
                    print('Время ожидания превышено')
                    self.flag = 0
                    return False
                self.flag += 1
                self.reboot()
            self.flag = 0
            return self.session.set(self.mid_sk, '4', 'INTEGER')
        except:
            print('Ошибка соединения, проверьте корректность данных и доступность стенда по порту 161')
            return False

    def status(self):
        dict_status = {'1': 'off', '2': 'on', '3': 'pending', '4': 'reboot'}
        if self.session.get(self.mid_sk).value == '3':
            sleep(5)
        print(dict_status.get(self.session.get(self.mid_sk).value))
        return dict_status.get(self.session.get(self.mid_sk).value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    opt = parser.add_argument
    opt('-u', '--user', help='username specified in the SNMP field PDU')
    opt('-a', '--address', help='ip address PDU or hostname')
    opt('-s', '--socket', help='number socket')
    opt('-c', '--command', metavar='on, off, reboot, status', help='the command to be executed')
    args = parser.parse_args()
    runner = PDUSNMP(hostname=args.address, login=args.user, socket=args.socket)
    command_mt = {'on': runner.on, 'off': runner.off, 'reboot': runner.reboot, 'status': runner.status}
    command_mt.get(args.command)()
