import os

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import base64
import json
from datetime import datetime, timedelta

# from license_client import LicenseClient

def _generate(lic_name, data):
    data_str = json.dumps(data)

    path = os.path.join("PEM", lic_name)
    # 读取私钥
    with open(os.path.join(path, "private.pem"), 'rb') as f:
        private_key = load_pem_private_key(f.read(), password=None)

    # 签名
    signature = private_key.sign(
        data_str.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode()

    license_data = {
        "data": data_str,
        "signature": signature_b64
    }
    json_str = json.dumps(license_data)
    activate_code = base64.b64encode(json_str.encode()).decode()
    return activate_code

def get_time_data(days):
    current_time = datetime.now()
    start_date = current_time.isoformat()

    end_time = current_time + timedelta(days=int(days))
    end_date = end_time.isoformat()

    data = {
        "start_date": start_date,
        "end_date": end_date
    }
    return data

class License:

    @staticmethod
    def generate(lic_name, machine_code, days):
        data = get_time_data(days)
        data['deployment_type'] = 'standalone'

        data['hardware_fingerprint'] = machine_code
        return _generate(lic_name, data)


    @staticmethod
    def generate_floating(lic_name, max_usage, days):
        data = get_time_data(days)
        data['deployment_type'] = 'floating'

        data['max_usage'] = max_usage
        return _generate(lic_name, data)


    @staticmethod
    def generate_key(lic_name):
        path = os.path.join("PEM", lic_name)
        os.mkdir(path)
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        with open(os.path.join(path, "private.pem"), "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(os.path.join(path, "public.pem"), "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))


# License.generate_key("VR Manager")
# activate_code = License.generate("VR Manager", "123", 30)
# print(activate_code)
# LicenseClient.verify(activate_code, 'PEM/VR Manager/public.pem')
