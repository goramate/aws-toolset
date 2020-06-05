#!/usr/bin/python3.7
import argparse
import base64
import hashlib
import hmac


def hash_iam_secret(sakey, version):
    key_bytes = str.encode(sakey)
    message_bytes = str.encode('SendRawEmail')
    version_bytes = str.encode(version)
    dig = hmac.new(key_bytes, message_bytes, digestmod=hashlib.sha256)
    return base64.b64encode(version_bytes+dig.digest()).decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('iam_secret_access_key',
                        type=str,
                        help='The AWS IAM secret access key')
    parser.add_argument('version',
                        type=str,
                        nargs='?',
                        default='\0x2',
                        help='Optional version number, default is 2')
    args = parser.parse_args()

    if len(args.iam_secret_access_key) != 40:
        print('AWS secret access keys should be 40 characters.')
    else:
        dig = hash_iam_secret(args.iam_secret_access_key,
                              args.version)

    print(dig)


if __name__ == '__main__':
    main()
