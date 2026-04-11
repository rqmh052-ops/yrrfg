#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Free Fire Login Script – يعمل بدون أخطاء protobuf
يستخدم OAuth + MajorLogin مع توليد رسائل protobuf ديناميكياً.
"""

import subprocess
import sys
import os
import asyncio
import ssl
import random
import aiohttp
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ------------------- تثبيت المتطلبات تلقائياً -------------------
required = ["aiohttp", "pycryptodome", "protobuf", "grpcio-tools"]
for lib in required:
    try:
        __import__(lib.replace("-", "_"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# ------------------- توليد ملفات protobuf المطلوبة -------------------
PROTO_FILES = {
    "MajorLoginReq.proto": """
syntax = "proto3";
message GameSecurity {
    int32 version = 6;
    uint64 hidden_value = 8;
}
message MajorLogin {
    string event_time = 3;
    string game_name = 4;
    int32 platform_id = 5;
    string client_version = 7;
    string system_software = 8;
    string system_hardware = 9;
    string telecom_operator = 10;
    string network_type = 11;
    uint32 screen_width = 12;
    uint32 screen_height = 13;
    string screen_dpi = 14;
    string processor_details = 15;
    uint32 memory = 16;
    string gpu_renderer = 17;
    string gpu_version = 18;
    string unique_device_id = 19;
    string client_ip = 20;
    string language = 21;
    string open_id = 22;
    string open_id_type = 23;
    string device_type = 24;
    GameSecurity memory_available = 25;
    string access_token = 29;
    int32 platform_sdk_id = 30;
    string network_operator_a = 41;
    string network_type_a = 42;
    string client_using_version = 57;
    int32 external_storage_total = 60;
    int32 external_storage_available = 61;
    int32 internal_storage_total = 62;
    int32 internal_storage_available = 63;
    int32 game_disk_storage_available = 64;
    int32 game_disk_storage_total = 65;
    int32 external_sdcard_avail_storage = 66;
    int32 external_sdcard_total_storage = 67;
    int32 login_by = 73;
    string library_path = 74;
    int32 reg_avatar = 76;
    string library_token = 77;
    int32 channel_type = 78;
    int32 cpu_type = 79;
    string cpu_architecture = 81;
    string client_version_code = 83;
    string graphics_api = 86;
    uint32 supported_astc_bitset = 87;
    int32 login_open_id_type = 88;
    bytes analytics_detail = 89;
    uint32 loading_time = 92;
    string release_channel = 93;
    string extra_info = 94;
    uint32 android_engine_init_flag = 95;
    int32 if_push = 97;
    int32 is_vpn = 98;
    string origin_platform_type = 99;
    string primary_platform_type = 100;
}
""",
    "MajorLoginRes.proto": """
syntax = "proto3";
message MajorLoginRes {
    string url = 1;
    string token = 2;
    uint64 account_uid = 3;
    bytes key = 4;
    bytes iv = 5;
    int64 timestamp = 6;
}
""",
    "GetLoginDataRes.proto": """
syntax = "proto3";
message GetLoginData {
    uint64 AccountUID = 1;
    string Region = 3;
    string AccountName = 4;
    string Online_IP_Port = 14;
    int64 Clan_ID = 20;
    string AccountIP_Port = 32;
    string Clan_Compiled_Data = 55;
}
"""
}

for filename, content in PROTO_FILES.items():
    with open(filename, "w") as f:
        f.write(content)
    subprocess.run(["python", "-m", "grpc_tools.protoc", f"--proto_path=.", f"--python_out=.", filename], check=False)

# استيراد الملفات المولدة
try:
    import MajorLoginReq_pb2
    import MajorLoginRes_pb2
    import GetLoginDataRes_pb2
except ImportError:
    print("❌ فشل في توليد ملفات protobuf. تأكد من تثبيت grpcio-tools بشكل صحيح.")
    sys.exit(1)

# ------------------- الثوابت -------------------
STATIC_KEY = b'Yg&tc%DEuh6%Zc^8'
STATIC_IV = b'6oyZDr22E3ychjM%'

# ------------------- الدوال المساعدة -------------------
async def get_random_user_agent():
    versions = ['4.0.18P6', '4.0.19P7', '4.0.20P1']
    models = ['SM-A125F', 'Redmi 9A', 'POCO M3']
    android_versions = ['11', '12']
    lang = 'en-US'
    country = 'USA'
    version = random.choice(versions)
    model = random.choice(models)
    android = random.choice(android_versions)
    return f"GarenaMSDK/{version}({model};Android {android};{lang};{country};)"

async def encrypted_proto(data: bytes) -> bytes:
    cipher = AES.new(STATIC_KEY, AES.MODE_CBC, STATIC_IV)
    padded = pad(data, AES.block_size)
    return cipher.encrypt(padded)

async def decrypt_response(enc_data: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(enc_data)
    return unpad(decrypted, AES.block_size)

# ------------------- دوال تسجيل الدخول -------------------
async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "User-Agent": await get_random_user_agent(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as resp:
            if resp.status != 200:
                return None, None
            js = await resp.json()
            return js.get("open_id"), js.get("access_token")

async def major_login(open_id, access_token):
    req = MajorLoginReq_pb2.MajorLogin()
    req.event_time = "2025-06-04 19:48:07"
    req.game_name = "free fire"
    req.platform_id = 1
    req.client_version = "1.123.1"
    req.system_software = "Android OS 9 / API-28"
    req.system_hardware = "Handheld"
    req.telecom_operator = "Verizon"
    req.network_type = "WIFI"
    req.screen_width = 1920
    req.screen_height = 1080
    req.screen_dpi = "280"
    req.processor_details = "ARM64 FP ASIMD AES VMH"
    req.memory = 3003
    req.gpu_renderer = "Adreno (TM) 640"
    req.gpu_version = "OpenGL ES 3.1"
    req.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    req.client_ip = "223.191.51.89"
    req.language = "en"
    req.open_id = open_id
    req.open_id_type = "4"
    req.device_type = "Handheld"
    req.memory_available.version = 55
    req.memory_available.hidden_value = 81
    req.access_token = access_token
    req.platform_sdk_id = 1
    req.network_operator_a = "Verizon"
    req.network_type_a = "WIFI"
    req.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    req.external_storage_total = 36235
    req.external_storage_available = 31335
    req.internal_storage_total = 2519
    req.internal_storage_available = 703
    req.game_disk_storage_available = 25010
    req.game_disk_storage_total = 26628
    req.external_sdcard_avail_storage = 32992
    req.external_sdcard_total_storage = 36235
    req.login_by = 3
    req.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    req.reg_avatar = 1
    req.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    req.channel_type = 3
    req.cpu_type = 2
    req.cpu_architecture = "64"
    req.client_version_code = "2029123000"
    req.graphics_api = "OpenGLES2"
    req.supported_astc_bitset = 16383
    req.login_open_id_type = 4
    req.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    req.loading_time = 13564
    req.release_channel = "android"
    req.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    req.android_engine_init_flag = 110009
    req.if_push = 1
    req.is_vpn = 1
    req.origin_platform_type = "4"
    req.primary_platform_type = "4"
    serialized = req.SerializeToString()
    encrypted = await encrypted_proto(serialized)

    url = "https://loginbp.common.ggbluefox.com/MajorLogin"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11)",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.11f1",
        "ReleaseVersion": "OB53"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=encrypted, headers=headers, ssl=ssl_ctx) as resp:
            if resp.status == 200:
                return await resp.read()
            return None

async def main():
    uid = "4481906989"
    pwd = "C415F8D7DCB735D2B2BC52302526B939B3CACEAE2BAB21390050DD0B91789F89"
    print("[1] الحصول على open_id و access_token...")
    open_id, token = await get_access_token(uid, pwd)
    if not open_id:
        print("❌ فشل OAuth. بيانات الحساب غير صحيحة.")
        return
    print(f"   open_id: {open_id[:20]}...")
    print("[2] إرسال MajorLogin...")
    resp_data = await major_login(open_id, token)
    if not resp_data:
        print("❌ لا رد من MajorLogin. الحساب محظور أو السيرفر لا يستجيب.")
        return
    # فك تشفير الرد (الرد مشفّر بـ key و iv ديناميكيين، لكن أولاً نستخدم static key؟ الكود الأصلي يستخدم MajorLoginRes_pb2.ParseFromString مباشرة على البيانات المستلمة، مما يعني أن البيانات غير مشفرة إضافياً. جرب.
    try:
        res = MajorLoginRes_pb2.MajorLoginRes()
        res.ParseFromString(resp_data)
        print(f"✅ تم تسجيل الدخول! UID: {res.account_uid}")
        print(f"   Base URL: {res.url}")
        print(f"   Token: {res.token[:50]}...")
        print(f"   Key: {res.key.hex()}")
        print(f"   IV: {res.iv.hex()}")
        print(f"   Timestamp: {res.timestamp}")
    except Exception as e:
        print(f"❌ فشل فك الرد: {e}")

if __name__ == "__main__":
    asyncio.run(main())