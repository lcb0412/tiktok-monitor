"""
TikTok X-Bogus签名生成器
"""

import base64
import hashlib
import time
from typing import Tuple


class XBogusSigner:
    def __init__(self, user_agent: str = None):
        self.user_agent = (
            user_agent
            or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
        )
        self.character = (
            "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="
        )
        self.Array = [None] * 48 + list(range(10)) + [None] * 6 + list(range(10, 16))
        self.ua_key = b"\x00\x01\x0c"

    def md5_str_to_array(self, md5_str: str) -> list:
        if len(md5_str) > 32:
            return [ord(c) for c in md5_str]
        array = []
        for i in range(0, len(md5_str), 2):
            array.append(
                (self.Array[ord(md5_str[i])] << 4) | self.Array[ord(md5_str[i + 1])]
            )
        return array

    def md5(self, data) -> str:
        if isinstance(data, str):
            data = self.md5_str_to_array(data)
        return hashlib.md5(bytes(data)).hexdigest()

    def md5_encrypt(self, url_path: str) -> list:
        return self.md5_str_to_array(
            self.md5(self.md5_str_to_array(self.md5(url_path)))
        )

    def rc4_encrypt(self, key: bytes, data: bytes) -> bytearray:
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        result = []
        i = j = 0
        for byte in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            result.append(byte ^ S[(S[i] + S[j]) % 256])
        return bytearray(result)

    def calculation(self, a: int, b: int, c: int) -> str:
        x3 = ((a & 255) << 16) | ((b & 255) << 8) | c
        return (
            self.character[(x3 & 16515072) >> 18]
            + self.character[(x3 & 258048) >> 12]
            + self.character[(x3 & 4032) >> 6]
            + self.character[x3 & 63]
        )

    def get_xbogus(self, url_path: str) -> Tuple[str, str]:
        ua_encoded = base64.b64encode(
            self.rc4_encrypt(self.ua_key, self.user_agent.encode("ISO-8859-1"))
        ).decode("ISO-8859-1")
        array1 = self.md5_str_to_array(self.md5(ua_encoded))
        array2 = self.md5_str_to_array(
            self.md5(self.md5_str_to_array("d41d8cd98f00b204e9800998ecf8427e"))
        )
        url_path_array = self.md5_encrypt(url_path)
        timer = int(time.time())
        ct = 536919696

        new_array = [
            64,
            0.00390625,
            1,
            12,
            url_path_array[14],
            url_path_array[15],
            array2[14],
            array2[15],
            array1[14],
            array1[15],
            (timer >> 24) & 255,
            (timer >> 16) & 255,
            (timer >> 8) & 255,
            timer & 255,
            (ct >> 24) & 255,
            (ct >> 16) & 255,
            (ct >> 8) & 255,
            ct & 255,
        ]

        xor_result = new_array[0]
        for i in range(1, len(new_array)):
            xor_result ^= int(new_array[i])
        new_array.append(xor_result)

        array3, array4 = [], []
        for i in range(0, len(new_array), 2):
            array3.append(new_array[i])
            if i + 1 < len(new_array):
                array4.append(new_array[i + 1])

        merge_array = array3 + array4
        garbled_code = ""
        for i in range(0, len(merge_array) - 2, 3):
            garbled_code += self.calculation(
                merge_array[i], merge_array[i + 1], merge_array[i + 2]
            )

        return f"{url_path}&X-Bogus={garbled_code}", garbled_code


def sign_url(url: str, params: dict = None, user_agent: str = None) -> str:
    signer = XBogusSigner(user_agent)
    query = "&".join([f"{k}={v}" for k, v in (params or {}).items()])
    if "?" in url:
        full_url = f"{url}&{query}"
    else:
        full_url = f"{url}?{query}" if query else url
    return signer.get_xbogus(full_url)[0]
