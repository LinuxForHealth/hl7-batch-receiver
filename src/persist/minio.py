from cdp_minio.wrapper import MinioClientApi


class PersistMinio:
    __PART_SIZE = 10 * 1024 * 1024

    def __init__(self) -> None:
        self._minio_client = None

    def init_client(self, endpoint, access_key, secret_key):
        if self._minio_client is None:
            self._minio_client = MinioClientApi(endpoint, access_key, secret_key)

    async def upload_batch(self, bucket_name, object_name, batch_data):
        response = await self._minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=batch_data,
            length=-1,
            part_size=PersistMinio.__PART_SIZE,
        )

        return response

    async def delete_batch(self, bucket_name, object_name):
        response = await self._minio_client.delete_object(
            bucket_name=bucket_name, object_name=object_name
        )

        return response

