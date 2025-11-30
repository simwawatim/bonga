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
        data = request.data

        try:
            serializer = ItemInfoSerializer(data=data)
            if not serializer.is_valid():
                first_field, messages = next(iter(serializer.errors.items()))
                return api_response(
                    status="fail",
                    message=f"{first_field}: {messages[0]}",
                    data={},
                    status_code=status.HTTP_400_BAD_REQUEST
                )


            external_client = CreateItem()
            external_response, generated_code = external_client.prepare_save_item_payload(data)

    
            if hasattr(external_response, "status_code"):
                if external_response.status_code != 200:
                    return external_response

            if hasattr(external_response, "json"):
                external_data = external_response.json()
            else:
                external_data = external_response

            if external_data.get("resultCd") != "000":
                return api_response(
                    status="fail",
                    message="External item creation failed",
                    data=external_data,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    
            item_instance = serializer.save(code=generated_code)

            return api_response(
                status="success",
                message="Item created successfully",
                data=ItemInfoSerializer(item_instance).data,
                status_code=status.HTTP_201_CREATED
            )

        except Exception as e:
            return api_response(
                status="error",
                message=f"Internal server error: {str(e)}",
                data={},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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