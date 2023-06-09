from rest_framework.views import APIView

from .reports import Report

from django.http import HttpResponse

class ReportAPIView(APIView):
    def post(self, request):
        date = request.data.get('date')
        file_extension = request.data.get('file_extension')

        if file_extension not in ['pdf', 'xlsx']:
            return HttpResponse('Invalid file extension. Only allowed "pdf" or "xlsx"', status=400)

        report = Report(date, file_extension)
        file_path, content_type = report.get_or_create()

        # Отправляем файл пользователю в качестве вложения
        response = HttpResponse(content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
        with open(file_path, 'rb') as f:
            response.write(f.read())

        return response

# from rest_framework.views import APIView
# # from rest_framework.response import Response
# from django.http import HttpResponse
# # from .handlers import get_or_create_report
# from .reports import Report
#
#
# class ReportAPIView(APIView):
#     def get(self, request):
#         date = request.GET.get('date')
#         file_extension = request.GET.get('file_extension')
#
#         if file_extension not in ['pdf', 'xlsx']:
#             return HttpResponse('Invalid file type. Only allowed "pdf" or "xlsx"', status=400)
#
#         report = Report(date, file_extension)
#         file_path, content_type = report.get_or_create()
#
#         # Отправляем файл пользователю в качестве вложения
#         response = HttpResponse(content_type=content_type)
#         response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
#         with open(file_path, 'rb') as f:
#             response.write(f.read())
#
#         return response
#         # category = request.GET.get('category')
#         # file_type = request.GET.get('file_type')
#         #
#         # report = get_or_create_report(category)
#         #
#         # # if not report:
#         # #     report = generate_category_report(category)
#         #
#         # if file_type == 'pdf':
#         #     response = FileResponse(report, content_type='application/pdf')
#         #     response['Content-Disposition'] = f'attachment; filename="category_report_{category}.pdf"'
#         # elif file_type == 'excel':
#         #     response = FileResponse(report,
#         #                             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#         #     response['Content-Disposition'] = f'attachment; filename="category_report_{category}.xlsx"'
#         # else:
#         #     return HttpResponseBadRequest({'error': 'Invalid file type'}, status=400)
#         #
#         # return response
