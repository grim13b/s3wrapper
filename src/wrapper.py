import json
from typing import Any, Optional
import boto3


class S3Manager:
    Bucket: str

    def __get_bucket(self, Bucket: Optional[str] = None) -> Any:
        s3_resource = boto3.resource('s3')
        return s3_resource.Bucket(self.Bucket if Bucket is None else Bucket)

    def list_objects(
        self,
        Prefix: str,
        Bucket: Optional[str] = None,
        Suffix: Optional[str] = None,
        Limit: Optional[int] = None
    ) -> list[str]:
        bucket = self.__get_bucket(Bucket)
        objects = bucket.objects

        filterd_objects = objects.filter(Prefix=Prefix)\
            if Limit is None else objects.filter(Prefix=Prefix).limit(count=Limit)

        if Suffix is not None:
            filterd_objects = filter(lambda x: x.key.endswith(Suffix), filterd_objects)

        return [obj.key for obj in filterd_objects]

    def read_object(
        self,
        Key: str,
        Bucket: Optional[str] = None
    ) -> bytes:
        bucket = self.__get_bucket(Bucket)
        obj = bucket.Object(Key)
        return obj.get()['Body'].read()

    def read_object_to_json(
        self,
        Key: str,
        Bucket: Optional[str] = None
    ) -> dict:
        obj = self.read_object(Bucket=Bucket, Key=Key)
        return json.loads(obj.decode('utf8'))

    def delete_object(
        self,
        Key: str,
        Bucket: Optional[str] = None
    ):
        bucket = self.__get_bucket(Bucket)
        # SEE: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Object.delete
        bucket.Object(Key).delete()

    def copy_object(
        self,
        SourceKey: str,
        DestinationKey: str,
        Bucket: Optional[str] = None
    ):
        bucket = self.__get_bucket(Bucket)
        # SEE: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.MultipartUploadPart.copy_from
        bucket.Object(DestinationKey).copy_from(CopySource={'Bucket': bucket.name, 'Key': SourceKey})

    def move_object(
        self,
        SourceKey: str,
        DestinationKey: str,
        Bucket: Optional[str] = None
    ):
        self.copy_object(Bucket=Bucket, SourceKey=SourceKey, DestinationKey=DestinationKey)
        self.delete_object(Bucket=Bucket, Key=SourceKey)
