from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import force_text

import csv
import time
import pytz
import json
import email
import struct
import logging
import requests
from imaplib import IMAP4_SSL
from datetime import datetime

from .models import Device, LoggedPoint

LOGGER = logging.getLogger('tracking_points')
BATCH_SIZE = 600


class DeferredIMAP(object):
    '''
    Convenience class for maintaining
    a bit of state about an IMAP server
    and handling logins/logouts.
    Note instances aren't threadsafe.
    '''
    def __init__(self, host, user, password):
        self.deletions = []
        self.flags = []
        self.host = host
        self.user = user
        self.password = password

    def login(self):
        self.imp = IMAP4_SSL(self.host)
        self.imp.login(self.user, self.password)
        self.imp.select("INBOX")

    def logout(self, expunge=False):
        if expunge:
            self.imp.expunge
        self.imp.close()
        self.imp.logout()

    def flush(self):
        self.login()
        if self.flags:
            LOGGER.info("Flagging {} unprocessable emails.".format(len(self.flags)))
            self.imp.store(",".join(self.flags), '+FLAGS', r'(\Flagged)')
        if self.deletions:
            LOGGER.info("Deleting {} processed emails.".format(len(self.deletions)))
            self.imp.store(",".join(self.deletions), '+FLAGS', r'(\Deleted)')
            self.logout(expunge=True)
        else:
            self.logout()
        self.flags, self.deletions = [], []

    def delete(self, msgid):
        self.deletions.append(str(msgid))

    def flag(self, msgid):
        self.flags.append(str(msgid))

    def __getattr__(self, name):
        def temp(*args, **kwargs):
            self.login()
            result = getattr(self.imp, name)(*args, **kwargs)
            self.logout()
            return result
        return temp


def retrieve_emails(dimap, search):
    textids = dimap.search(None, search)[1][0].split(' ')
    # If no emails just return
    if textids == ['']:
        return []
    typ, responses = dimap.fetch(",".join(textids[-BATCH_SIZE:]), '(BODY.PEEK[])')
    # If protcol error just return
    if typ != 'OK':
        return []
    messages = []
    for response in responses:
        if isinstance(response, tuple):
            msgid = int(response[0].split(' ')[0])
            msg = email.message_from_string(response[1])
            messages.append((msgid, msg))
    LOGGER.info("Fetched {}/{} messages for {}.".format(len(messages), len(textids), search))
    return messages


def lat_long_isvalid(lt, lg):
    return (lt <= 90 and lt >= -90 and lg <= 180 and lg >= -180)


def save_iriditrak(dimap, queueitem):
    msgid, msg = queueitem
    try:
        deviceid = int(msg["SUBJECT"].replace('SBD Msg From Unit: ', ''))
    except ValueError:
        dimap.flag(msgid)
        return
    attachment = None
    for part in msg.walk():
        if part.get_content_maintype() != 'multipart':
            attachment = part.get_payload(decode=True)
    # Make sure email is from iridium and has valid timestamp
    received = filter(lambda val: val.find("(HELO sbd.iridium.com)") > -1, msg.values())
    if 'DATE' in msg:
        timestamp = time.mktime(email.utils.parsedate(msg["DATE"]))
    elif len(received) == 1:
        timestamp = time.mktime(email.utils.parsedate(received[0].split(';')[-1].strip()))
    else:
        LOGGER.info("Can't find date in " + str(msg.__dict__))
    sbd = {'ID': deviceid, 'TU': timestamp, 'TY': 'iriditrak'}
    # BEAM binary message, 10byte or 20byte
    if len(attachment) <= 20:
        try:
            raw = struct.unpack("<BBBBBBBBBBIHHH"[:len(attachment) + 1], attachment)
            # Byte 1 Equation byte, use to detect type of message
            sbd['EQ'] = raw[0]
            # BEAM 10byte and 20byte binary messages
            if sbd['EQ'] in [1, 2, 3, 4, 18, 19, 25, 26]:
                # Byte 2: SSSS:GPS:Lat:Lng:Msd (SSSS = SQ, Msd = Most Significant Digit of Longitude)
                sbd['SQ'] = int('0' + bin(raw[1])[2:][-8:-4], 2)
                Lat = int(bin(raw[1])[2:][-3]) * '-'
                Lng = int(bin(raw[1])[2:][-2]) * '-'
                LngH = bin(raw[1])[2:][-1]
                # Byte 3,4 (Latitude HHMM)
                LatH = str(int('0' + bin(raw[2])[2:][-4:], 2)) + str(int('0' + bin(raw[2])[2:][-8:-4], 2))
                LatM = str(int('0' + bin(raw[3])[2:][-4:], 2)) + str(int('0' + bin(raw[3])[2:][-8:-4], 2))
                # Byte 5,6 (Latitude .MMMM)
                LatM += '.' + str(int('0' + bin(raw[4])[2:][-4:], 2)) + str(int('0' + bin(raw[4])[2:][-8:-4], 2))
                LatM += str(int('0' + bin(raw[5])[2:][-4:], 2)) + str(int('0' + bin(raw[5])[2:][-8:-4], 2))
                sbd['LT'] = float(Lat + str(int(LatH) + float(LatM) / 60))
                # Byte 7,8 (Longitude HHMM)
                LngH += str(int('0' + bin(raw[6])[2:][-4:], 2)) + str(int('0' + bin(raw[6])[2:][-8:-4], 2))
                LngM = str(int('0' + bin(raw[7])[2:][-4:], 2)) + str(int('0' + bin(raw[7])[2:][-8:-4], 2))
                # Byte 9,10 (Longitude .MMMM)
                LngM += '.' + str(int('0' + bin(raw[8])[2:][-4:], 2)) + str(int('0' + bin(raw[8])[2:][-8:-4], 2))
                LngM += str(int('0' + bin(raw[9])[2:][-4:], 2)) + str(int('0' + bin(raw[9])[2:][-8:-4], 2))
                sbd['LG'] = float(Lng + str(int(LngH) + float(LngM) / 60))
                if not lat_long_isvalid(sbd['LT'], sbd['LG']):
                    raise ValueError('Lon/Lat {},{} is not valid.'.format(sbd['LG'], sbd['LT']))
                if len(raw) == 14:
                    # Byte 11,12,13,14 is unix time, but local to the device??
                    # use email timestamp because within 10 secs and fairly accurate
                    # might have future issues with delayed retransmits
                    sbd['LOCALTU'] = raw[10]
                    # Byte 15,16 are speed in 10 m/h
                    sbd['VL'] = raw[11] * 10
                    # Byte 17,18 is altitude in m above sea level
                    sbd['AL'] = raw[12]
                    # Byte 19,20 is direction in degrees
                    sbd['DR'] = raw[13]
                LOGGER.debug(str(sbd))
            else:
                LOGGER.warning("Don't know how to read " + force_text(sbd['EQ']) + " - " + force_text(raw))
                dimap.flag(msgid)
                return
        except Exception as e:
            LOGGER.warning("error: " + force_text(e))
            dimap.flag(msgid)
            return
    else:
        LOGGER.warning("Flagging IridiTrak message {}".format(msgid))
        dimap.flag(msgid)
        return

    LoggedPoint.parse_sbd(sbd)
    dimap.delete(msgid)


def save_dplus(dimap, queueitem):
    msgid, msg = queueitem
    sbd = {"RAW": msg.get_payload().strip().split("|")}
    try:
        deviceid = sbd["ID"] = int(sbd["RAW"][0])
        sbd["LT"] = float(sbd["RAW"][4])
        sbd["LG"] = float(sbd["RAW"][5])
        if not lat_long_isvalid(sbd['LT'], sbd['LG']):
            raise ValueError('Lon/Lat {},{} is not valid.'.format(sbd['LG'], sbd['LT']))
        sbd["TU"] = time.mktime(datetime.strptime(sbd["RAW"][1], "%d-%m-%y %H:%M:%S").timetuple())
        sbd["VL"] = int(sbd["RAW"][6]) * 1000
        sbd["DR"] = int(sbd["RAW"][7])
        sbd["AL"] = int(sbd["RAW"][9])
        sbd["TY"] = 'dplus'
    except ValueError, e:
        LOGGER.error(e)
        dimap.flag(msgid)
        return
    try:
        LoggedPoint.parse_sbd(sbd)
    except Exception as e:
        LOGGER.error(e)
        dimap.flag(msgid)
        return

    dimap.delete(msgid)


def save_spot(dimap, queueitem):
    msgid, msg = queueitem
    if 'DATE' in msg:
        timestamp = time.mktime(email.utils.parsedate(msg["DATE"]))
    else:
        LOGGER.info("Can't find date in " + str(msg.__dict__))
        dimap.flag(msgid)
        return
    try:
        sbd = {
            'ID': msg['X-SPOT-Messenger'],
            'LT': msg['X-SPOT-Latitude'],
            'LG': msg['X-SPOT-Longitude'],
            'Type': msg['X-SPOT-Type'],
            'LOCALTU': msg['X-Spot-Time'],
            'TU': timestamp,
            'DR': 0,
            'AL': 0,
            'VL': 0,
            'TY': 'spot'
        }
        if not lat_long_isvalid(sbd['LT'], sbd['LG']):
            raise ValueError('Lon/Lat {},{} is not valid.'.format(sbd['LG'], sbd['LT']))
    except ValueError as e:
        LOGGER.warning("Couldn't parse {}, error: {}".format(sbd, e))
        dimap.flag(msgid)
        return
    LoggedPoint.parse_sbd(sbd)
    dimap.delete(msgid)


def save_tracplus():
    if not settings.TRACPLUS_URL:
        return
    latest = list(csv.DictReader(requests.get(settings.TRACPLUS_URL).content.split("\r\n")))
    updated = 0
    for row in latest:
        device = Device.objects.get_or_create(deviceid=row["Device IMEI"])[0]
        device.callsign = row["Asset Name"]
        device.model = row["Asset Model"]
        device.registration = row["Asset Regn"][:32]
        device.velocity = int(row["Speed"]) * 1000
        device.altitude = row["Altitude"]
        device.heading = row["Track"]
        device.seen = timezone.make_aware(datetime.strptime(row["Transmitted"], "%Y-%m-%d %H:%M:%S"), pytz.timezone("UTC"))
        device.point = "POINT ({} {})".format(row["Longitude"], row["Latitude"])
        device.source_device_type = 'tracplus'
        device.save()
        lp, new = LoggedPoint.objects.get_or_create(device=device, seen=device.seen)
        lp.velocity = device.velocity
        lp.heading = device.heading
        lp.altitude = device.altitude
        lp.point = device.point
        lp.seen = device.seen
        lp.source_device_type = device.source_device_type
        lp.raw = json.dumps(row)
        lp.save()
        if new:
            updated += 1
    LOGGER.info("Updated {} of {} scanned TracPLUS devices".format(updated, len(latest)))


def harvest_tracking_email(request=None):
    """Download and save tracking point emails.
    """
    dimap = DeferredIMAP(
        host=settings.EMAIL_HOST, user=settings.EMAIL_USER, password=settings.EMAIL_PASSWORD)
    start = timezone.now()

    LOGGER.info('Harvesting IridiTRAK emails')
    emails = retrieve_emails(dimap, '(FROM "sbdservice@sbd.iridium.com" UNFLAGGED)')
    for message in emails:
        save_iriditrak(dimap, message)
    dimap.flush()

    LOGGER.info('Harvesting DPlus emails')
    emails = retrieve_emails(dimap, '(FROM "Dplus@asta.net.au" UNFLAGGED)')
    for message in emails:
        save_dplus(dimap, message)
    dimap.flush()

    LOGGER.info('Harvesting Spot emails')
    emails = retrieve_emails(dimap, '(FROM "noreply@findmespot.com" UNFLAGGED)')
    for message in emails:
        save_spot(dimap, message)
    dimap.flush()

    LOGGER.info('Harvesting TracPlus emails')
    try:
        save_tracplus()
    except Exception as e:
        LOGGER.error(e)

    delta = timezone.now() - start
    html = "<html><body>Tracking point email harvest run at {} for {}</body></html>".format(start, delta)
    if request:
        return HttpResponse(html)
    else:
        return
