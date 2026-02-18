import base64
import json
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding

from datetime import datetime

class LicenseClient:

    @staticmethod
    def verify(activate_code, public_key_path):
        # 将许可证字符串进行 Base64 解码
        decoded_activate_code = base64.b64decode(activate_code).decode("utf-8")

        # 验签 用内置的公钥 (Public Key)，对 data 字符串和 signature 进行 RSA 校验
        try:
            activate_code_obj = json.loads(decoded_activate_code)
        except json.decoder.JSONDecodeError:
            return False

        license_str = activate_code_obj['data']
        signature = base64.b64decode(activate_code_obj['signature'])

        # 读取公钥
        with open(public_key_path, 'rb') as f:
            public_key = load_pem_public_key(f.read())

        # 若验签失败，说明许可证被篡改，应立即终止程序
        try:
            public_key.verify(
                signature,
                license_str.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

        except InvalidSignature:
            return False

        # 将 data 字符串反序列化为对象
        license_obj = json.loads(license_str)
        print(license_obj)

        # 检查许可证类型
        if license_obj["deployment_type"] != 'standalone':
            return False

        # 确认当前时间在 start_date 和 end_date 之间
        start_date = datetime.fromisoformat(license_obj["start_date"])
        end_date = datetime.fromisoformat(license_obj["end_date"])

        # 在软件启动时比对当前系统时间。若 end_date 小于当前时间，将状态视为过期
        current_time = datetime.now()
        if end_date < current_time:
            print("过期")
            return False

        # 重新计算本地硬件信息并与 data 中的 hardware_fingerprint 进行比对
        hardware_fingerprint = license_obj["hardware_fingerprint"]

        return True
