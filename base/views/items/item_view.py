from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from base.models import ItemInfo
from base.serializers.item.item_serializer import ItemInfoSerializer
from base.utils.response_handler import api_response
from rest_framework.response import Response
from zra_client.create_item import CreateItem
from django.db.models import ProtectedError


class ItemInfoListCreateView(APIView):
    def get(self, request):
        items = ItemInfo.objects.all()
        serializer = ItemInfoSerializer(items, many=True)
        return api_response("success", serializer.data, status_code=200)


    def post(self, request):
        try:
            serializer = ItemInfoSerializer(data=request.data)
            if not serializer.is_valid():
                first_field, messages = next(iter(serializer.errors.items()))
                return api_response(
                    "error",
                    f"{first_field}: {messages[0]}",
                    status_code=400,
                    is_error=True
                )

            external_client = CreateItem()
            external_response = external_client.prepare_save_item_payload()
            data = external_response.json()
            
            if data.get("resultCd") != "000":
                return Response(
                    {
                        "error": "External item creation failed",
                        "message": external_response,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(created_by=request.user if request.user.is_authenticated else None)

            return api_response("success", serializer.data, status_code=201)

        except Exception as e:
            return api_response(
                "error",
                f"Internal server error: {str(e)}",
                status_code=500,
                is_error=True
            )

class ItemInfoDetailView(APIView):
    def get(self, request, pk):
        item = get_object_or_404(ItemInfo, pk=pk)
        serializer = ItemInfoSerializer(item)
        return api_response("success", serializer.data, status_code=200)

    def put(self, request, pk):
        item = get_object_or_404(ItemInfo, pk=pk)
        serializer = ItemInfoSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return api_response("success", serializer.data)
        first_field, messages = next(iter(serializer.errors.items()))
        return api_response("error", f"{first_field}: {messages[0]}", status_code=400, is_error=True)

    def delete(self, request, pk):
        try:
            item = get_object_or_404(ItemInfo, pk=pk)
            item.delete()
            return api_response(
                "success",
                "Item deleted successfully.",
                status_code=200,
                is_error=False
            )
        except ProtectedError:
            return api_response(
                "error",
                "Cannot delete item because it is referenced in other records.",
                status_code=400,
                is_error=True
            )
        except Exception as e:
            return api_response(
                "error",
                f"Internal server error during delete: {str(e)}",
                status_code=500,
                is_error=True
            )