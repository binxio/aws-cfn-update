import botocore
import datetime
from dateutil.tz import tzutc, tzlocal


request = {
    "Filters": [
        {"Name": "name", "Values": ["Windows_Server-2016-English-Full-Base*"]},
        {"Name": "state", "Values": ["available"]},
        {"Name": "virtualization-type", "Values": ["hvm"]},
        {"Name": "root-device-type", "Values": ["ebs"]},
    ],
    "Owners": ["801119661308"],
}
response = {
    "Images": [
        {
            "Architecture": "x86_64",
            "CreationDate": "2022-09-14T18:53:28.000Z",
            "ImageId": "ami-0d030edc442a8c188",
            "ImageLocation": "amazon/Windows_Server-2016-English-Full-Base-2022.09.14",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "801119661308",
            "Platform": "windows",
            "PlatformDetails": "Windows",
            "UsageOperation": "RunInstances:0002",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-0f7674948128a2988",
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                        "Encrypted": False,
                    },
                },
                {"DeviceName": "xvdca", "VirtualName": "ephemeral0"},
                {"DeviceName": "xvdcb", "VirtualName": "ephemeral1"},
                {"DeviceName": "xvdcc", "VirtualName": "ephemeral2"},
                {"DeviceName": "xvdcd", "VirtualName": "ephemeral3"},
                {"DeviceName": "xvdce", "VirtualName": "ephemeral4"},
                {"DeviceName": "xvdcf", "VirtualName": "ephemeral5"},
                {"DeviceName": "xvdcg", "VirtualName": "ephemeral6"},
                {"DeviceName": "xvdch", "VirtualName": "ephemeral7"},
                {"DeviceName": "xvdci", "VirtualName": "ephemeral8"},
                {"DeviceName": "xvdcj", "VirtualName": "ephemeral9"},
                {"DeviceName": "xvdck", "VirtualName": "ephemeral10"},
                {"DeviceName": "xvdcl", "VirtualName": "ephemeral11"},
                {"DeviceName": "xvdcm", "VirtualName": "ephemeral12"},
                {"DeviceName": "xvdcn", "VirtualName": "ephemeral13"},
                {"DeviceName": "xvdco", "VirtualName": "ephemeral14"},
                {"DeviceName": "xvdcp", "VirtualName": "ephemeral15"},
                {"DeviceName": "xvdcq", "VirtualName": "ephemeral16"},
                {"DeviceName": "xvdcr", "VirtualName": "ephemeral17"},
                {"DeviceName": "xvdcs", "VirtualName": "ephemeral18"},
                {"DeviceName": "xvdct", "VirtualName": "ephemeral19"},
                {"DeviceName": "xvdcu", "VirtualName": "ephemeral20"},
                {"DeviceName": "xvdcv", "VirtualName": "ephemeral21"},
                {"DeviceName": "xvdcw", "VirtualName": "ephemeral22"},
                {"DeviceName": "xvdcx", "VirtualName": "ephemeral23"},
                {"DeviceName": "xvdcy", "VirtualName": "ephemeral24"},
                {"DeviceName": "xvdcz", "VirtualName": "ephemeral25"},
            ],
            "Description": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "Windows_Server-2016-English-Full-Base-2022.09.14",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
            "DeprecationTime": "2024-09-14T18:53:28.000Z",
        },
        {
            "Architecture": "x86_64",
            "CreationDate": "2022-08-10T07:21:09.000Z",
            "ImageId": "ami-0a27d685ce855d752",
            "ImageLocation": "amazon/Windows_Server-2016-English-Full-Base-2022.08.10",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "801119661308",
            "Platform": "windows",
            "PlatformDetails": "Windows",
            "UsageOperation": "RunInstances:0002",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-0ffc356891b0aefa9",
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                        "Encrypted": False,
                    },
                },
                {"DeviceName": "xvdca", "VirtualName": "ephemeral0"},
                {"DeviceName": "xvdcb", "VirtualName": "ephemeral1"},
                {"DeviceName": "xvdcc", "VirtualName": "ephemeral2"},
                {"DeviceName": "xvdcd", "VirtualName": "ephemeral3"},
                {"DeviceName": "xvdce", "VirtualName": "ephemeral4"},
                {"DeviceName": "xvdcf", "VirtualName": "ephemeral5"},
                {"DeviceName": "xvdcg", "VirtualName": "ephemeral6"},
                {"DeviceName": "xvdch", "VirtualName": "ephemeral7"},
                {"DeviceName": "xvdci", "VirtualName": "ephemeral8"},
                {"DeviceName": "xvdcj", "VirtualName": "ephemeral9"},
                {"DeviceName": "xvdck", "VirtualName": "ephemeral10"},
                {"DeviceName": "xvdcl", "VirtualName": "ephemeral11"},
                {"DeviceName": "xvdcm", "VirtualName": "ephemeral12"},
                {"DeviceName": "xvdcn", "VirtualName": "ephemeral13"},
                {"DeviceName": "xvdco", "VirtualName": "ephemeral14"},
                {"DeviceName": "xvdcp", "VirtualName": "ephemeral15"},
                {"DeviceName": "xvdcq", "VirtualName": "ephemeral16"},
                {"DeviceName": "xvdcr", "VirtualName": "ephemeral17"},
                {"DeviceName": "xvdcs", "VirtualName": "ephemeral18"},
                {"DeviceName": "xvdct", "VirtualName": "ephemeral19"},
                {"DeviceName": "xvdcu", "VirtualName": "ephemeral20"},
                {"DeviceName": "xvdcv", "VirtualName": "ephemeral21"},
                {"DeviceName": "xvdcw", "VirtualName": "ephemeral22"},
                {"DeviceName": "xvdcx", "VirtualName": "ephemeral23"},
                {"DeviceName": "xvdcy", "VirtualName": "ephemeral24"},
                {"DeviceName": "xvdcz", "VirtualName": "ephemeral25"},
            ],
            "Description": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "Windows_Server-2016-English-Full-Base-2022.08.10",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
            "DeprecationTime": "2024-08-10T07:21:09.000Z",
        },
        {
            "Architecture": "x86_64",
            "CreationDate": "2022-10-28T01:24:13.000Z",
            "ImageId": "ami-01527f1bfc6f63543",
            "ImageLocation": "amazon/Windows_Server-2016-English-Full-Base-2022.10.27",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "801119661308",
            "Platform": "windows",
            "PlatformDetails": "Windows",
            "UsageOperation": "RunInstances:0002",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-0636cccace06ba03d",
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                        "Encrypted": False,
                    },
                },
                {"DeviceName": "xvdca", "VirtualName": "ephemeral0"},
                {"DeviceName": "xvdcb", "VirtualName": "ephemeral1"},
                {"DeviceName": "xvdcc", "VirtualName": "ephemeral2"},
                {"DeviceName": "xvdcd", "VirtualName": "ephemeral3"},
                {"DeviceName": "xvdce", "VirtualName": "ephemeral4"},
                {"DeviceName": "xvdcf", "VirtualName": "ephemeral5"},
                {"DeviceName": "xvdcg", "VirtualName": "ephemeral6"},
                {"DeviceName": "xvdch", "VirtualName": "ephemeral7"},
                {"DeviceName": "xvdci", "VirtualName": "ephemeral8"},
                {"DeviceName": "xvdcj", "VirtualName": "ephemeral9"},
                {"DeviceName": "xvdck", "VirtualName": "ephemeral10"},
                {"DeviceName": "xvdcl", "VirtualName": "ephemeral11"},
                {"DeviceName": "xvdcm", "VirtualName": "ephemeral12"},
                {"DeviceName": "xvdcn", "VirtualName": "ephemeral13"},
                {"DeviceName": "xvdco", "VirtualName": "ephemeral14"},
                {"DeviceName": "xvdcp", "VirtualName": "ephemeral15"},
                {"DeviceName": "xvdcq", "VirtualName": "ephemeral16"},
                {"DeviceName": "xvdcr", "VirtualName": "ephemeral17"},
                {"DeviceName": "xvdcs", "VirtualName": "ephemeral18"},
                {"DeviceName": "xvdct", "VirtualName": "ephemeral19"},
                {"DeviceName": "xvdcu", "VirtualName": "ephemeral20"},
                {"DeviceName": "xvdcv", "VirtualName": "ephemeral21"},
                {"DeviceName": "xvdcw", "VirtualName": "ephemeral22"},
                {"DeviceName": "xvdcx", "VirtualName": "ephemeral23"},
                {"DeviceName": "xvdcy", "VirtualName": "ephemeral24"},
                {"DeviceName": "xvdcz", "VirtualName": "ephemeral25"},
            ],
            "Description": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "Windows_Server-2016-English-Full-Base-2022.10.27",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
            "DeprecationTime": "2024-10-28T01:24:13.000Z",
        },
        {
            "Architecture": "x86_64",
            "CreationDate": "2022-11-10T13:31:43.000Z",
            "ImageId": "ami-0dd4486f71af814de",
            "ImageLocation": "amazon/Windows_Server-2016-English-Full-Base-2022.11.10",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "801119661308",
            "Platform": "windows",
            "PlatformDetails": "Windows",
            "UsageOperation": "RunInstances:0002",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-099d325d96bf48c86",
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                        "Encrypted": False,
                    },
                },
                {"DeviceName": "xvdca", "VirtualName": "ephemeral0"},
                {"DeviceName": "xvdcb", "VirtualName": "ephemeral1"},
                {"DeviceName": "xvdcc", "VirtualName": "ephemeral2"},
                {"DeviceName": "xvdcd", "VirtualName": "ephemeral3"},
                {"DeviceName": "xvdce", "VirtualName": "ephemeral4"},
                {"DeviceName": "xvdcf", "VirtualName": "ephemeral5"},
                {"DeviceName": "xvdcg", "VirtualName": "ephemeral6"},
                {"DeviceName": "xvdch", "VirtualName": "ephemeral7"},
                {"DeviceName": "xvdci", "VirtualName": "ephemeral8"},
                {"DeviceName": "xvdcj", "VirtualName": "ephemeral9"},
                {"DeviceName": "xvdck", "VirtualName": "ephemeral10"},
                {"DeviceName": "xvdcl", "VirtualName": "ephemeral11"},
                {"DeviceName": "xvdcm", "VirtualName": "ephemeral12"},
                {"DeviceName": "xvdcn", "VirtualName": "ephemeral13"},
                {"DeviceName": "xvdco", "VirtualName": "ephemeral14"},
                {"DeviceName": "xvdcp", "VirtualName": "ephemeral15"},
                {"DeviceName": "xvdcq", "VirtualName": "ephemeral16"},
                {"DeviceName": "xvdcr", "VirtualName": "ephemeral17"},
                {"DeviceName": "xvdcs", "VirtualName": "ephemeral18"},
                {"DeviceName": "xvdct", "VirtualName": "ephemeral19"},
                {"DeviceName": "xvdcu", "VirtualName": "ephemeral20"},
                {"DeviceName": "xvdcv", "VirtualName": "ephemeral21"},
                {"DeviceName": "xvdcw", "VirtualName": "ephemeral22"},
                {"DeviceName": "xvdcx", "VirtualName": "ephemeral23"},
                {"DeviceName": "xvdcy", "VirtualName": "ephemeral24"},
                {"DeviceName": "xvdcz", "VirtualName": "ephemeral25"},
            ],
            "Description": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "Windows_Server-2016-English-Full-Base-2022.11.10",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
            "DeprecationTime": "2024-11-10T13:31:43.000Z",
        },
        {
            "Architecture": "x86_64",
            "CreationDate": "2022-10-12T16:06:39.000Z",
            "ImageId": "ami-07cd9d4167c228ea0",
            "ImageLocation": "amazon/Windows_Server-2016-English-Full-Base-2022.10.12",
            "ImageType": "machine",
            "Public": True,
            "OwnerId": "801119661308",
            "Platform": "windows",
            "PlatformDetails": "Windows",
            "UsageOperation": "RunInstances:0002",
            "State": "available",
            "BlockDeviceMappings": [
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "SnapshotId": "snap-0f492bcf1abc69555",
                        "VolumeSize": 30,
                        "VolumeType": "gp2",
                        "Encrypted": False,
                    },
                },
                {"DeviceName": "xvdca", "VirtualName": "ephemeral0"},
                {"DeviceName": "xvdcb", "VirtualName": "ephemeral1"},
                {"DeviceName": "xvdcc", "VirtualName": "ephemeral2"},
                {"DeviceName": "xvdcd", "VirtualName": "ephemeral3"},
                {"DeviceName": "xvdce", "VirtualName": "ephemeral4"},
                {"DeviceName": "xvdcf", "VirtualName": "ephemeral5"},
                {"DeviceName": "xvdcg", "VirtualName": "ephemeral6"},
                {"DeviceName": "xvdch", "VirtualName": "ephemeral7"},
                {"DeviceName": "xvdci", "VirtualName": "ephemeral8"},
                {"DeviceName": "xvdcj", "VirtualName": "ephemeral9"},
                {"DeviceName": "xvdck", "VirtualName": "ephemeral10"},
                {"DeviceName": "xvdcl", "VirtualName": "ephemeral11"},
                {"DeviceName": "xvdcm", "VirtualName": "ephemeral12"},
                {"DeviceName": "xvdcn", "VirtualName": "ephemeral13"},
                {"DeviceName": "xvdco", "VirtualName": "ephemeral14"},
                {"DeviceName": "xvdcp", "VirtualName": "ephemeral15"},
                {"DeviceName": "xvdcq", "VirtualName": "ephemeral16"},
                {"DeviceName": "xvdcr", "VirtualName": "ephemeral17"},
                {"DeviceName": "xvdcs", "VirtualName": "ephemeral18"},
                {"DeviceName": "xvdct", "VirtualName": "ephemeral19"},
                {"DeviceName": "xvdcu", "VirtualName": "ephemeral20"},
                {"DeviceName": "xvdcv", "VirtualName": "ephemeral21"},
                {"DeviceName": "xvdcw", "VirtualName": "ephemeral22"},
                {"DeviceName": "xvdcx", "VirtualName": "ephemeral23"},
                {"DeviceName": "xvdcy", "VirtualName": "ephemeral24"},
                {"DeviceName": "xvdcz", "VirtualName": "ephemeral25"},
            ],
            "Description": "Microsoft Windows Server 2016 with Desktop Experience Locale English AMI provided by Amazon",
            "EnaSupport": True,
            "Hypervisor": "xen",
            "ImageOwnerAlias": "amazon",
            "Name": "Windows_Server-2016-English-Full-Base-2022.10.12",
            "RootDeviceName": "/dev/sda1",
            "RootDeviceType": "ebs",
            "SriovNetSupport": "simple",
            "VirtualizationType": "hvm",
            "DeprecationTime": "2024-10-12T16:06:39.000Z",
        },
    ],
    "ResponseMetadata": {
        "RequestId": "595905ff-d097-4e65-8aad-82e3ff3bf626",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "x-amzn-requestid": "595905ff-d097-4e65-8aad-82e3ff3bf626",
            "cache-control": "no-cache, no-store",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
            "vary": "accept-encoding",
            "content-type": "text/xml;charset=UTF-8",
            "transfer-encoding": "chunked",
            "date": "Sat, 12 Nov 2022 11:10:04 GMT",
            "server": "AmazonEC2",
        },
        "RetryAttempts": 0,
    },
}