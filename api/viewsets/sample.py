from django.db import connections
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import SampleSerializer


class SampleViewSet(APIView):
    def get(self, _):
        with connections["LW8Process"].cursor() as cursor:
            cursor.execute(
                """
                SELECT TOP 10 SAMPLE_NUMBER, TEXT_ID, SAMPLE_VOLUME, SAMPLE_UNITS,
                               SAMPLE_TYPE, CONTAINER_TYPE
                FROM SAMPLE
            """
            )
            rows = cursor.fetchall()

        return Response(
            [
                {
                    "SAMPLE_NUMBER": row[0],
                    "TEXT_ID": row[1],
                    "SAMPLE_VOLUME": row[2],
                    "SAMPLE_UNITS": row[3],
                    "SAMPLE_TYPE": row[4],
                    "CONTAINER_TYPE": row[5],
                }
                for row in rows
            ]
        )

    def post(self, request):
        serializer = SampleSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            with connections["LW8Process"].cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM SAMPLE WHERE SAMPLE_NUMBER = %s",
                    [data.get("SAMPLE_NUMBER")],
                )
                if cursor.fetchone():
                    return Response(
                        {"error": "SAMPLE_NUMBER already exists."}, status=400
                    )

                cursor.execute(
                    """
                    INSERT INTO SAMPLE (SAMPLE_NUMBER, TEXT_ID, SAMPLE_VOLUME,
                                        SAMPLE_UNITS, SAMPLE_TYPE, CONTAINER_TYPE)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    [
                        data.get("SAMPLE_NUMBER"),
                        data.get("TEXT_ID"),
                        data.get("SAMPLE_VOLUME"),
                        data.get("SAMPLE_UNITS"),
                        data.get("SAMPLE_TYPE"),
                        data.get("CONTAINER_TYPE"),
                    ],
                )
            return Response({"message": "Sample inserted successfully."}, status=201)

        return Response(serializer.errors, status=400)
