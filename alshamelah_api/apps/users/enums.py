from enum import Enum


class OTPStatus(Enum):
    Verified = 1
    Expired = 2
    Used = 3
    Invalid = 4


class OTPTypes(object):
    Email = 'E'
    Phone = 'P'
