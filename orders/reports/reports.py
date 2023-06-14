import os
from django.conf import settings
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import openpyxl

from alfafood.settings import STATIC_URL
from common.services import date_format_validate
from orders.models.order import Order, OrderItem


class Report:
    def __init__(self, user_role, date, file_extension):
        self.user_role = user_role
        self.date = date
        self.validated_date = date_format_validate(date).date()
        self.file_extension = file_extension
        self.file_name = f"{user_role}_report_{date}.{self.file_extension}"
        self.file_path = os.path.join(settings.BASE_DIR, 'static', 'reports', self.file_name)
        self.content = ""

    def generate(self):
        if self.file_extension == 'pdf':
            # self._generate_pdf_report()
            if self.user_role == "canteen":
                self.content = self._generate_canteen_pdf_report()
            elif self.user_role == "teacher":
                self.content = self._generate_teacher_pdf_report()
        elif self.file_extension == 'xlsx':
            ...
            # self._generate_excel_report()

    def _generate_teacher_pdf_report(self):
        queryset = OrderItem.objects.filter(order_id__order_date=self.validated_date)

        result = {}

        for order_item in queryset:
            result.setdefault(order_item.order_id.student_id, {})\
                .update({order_item.product_name: order_item.quantity if
                        result[order_item.order_id.student_id].get(order_item.product_name) is None else
                        result[order_item.order_id.student_id].get(order_item.product_name)+order_item.quantity})

        table_data = [
            ["Приём пищи", "Наименование блюда", "Количество порций"]
        ]


    def _generate_canteen_pdf_report(self):
        # Получение данных из модели OrderItem
        queryset = OrderItem.objects.filter(order_id__order_date=self.validated_date)

        # Преобразование обработанных данных в список списков
        first_table_data = [
            ["Приём пищи", "Наименование блюда", "Количество порций"]
        ]

        second_table_data = [
            ["Наименование блюда", "Количество порций"]
        ]

        queryset = sorted(queryset, key=lambda x: ['Завтрак', 'Обед', 'Полдник', 'Ужин'].index(x.meal_category))

        # Обработка данных для объединения и суммирования
        first_table_processed_data = {}

        second_table_processed_data = {}

        for item in queryset:
            category = item.meal_category or ""
            product = item.product_name or ""
            quantity = item.quantity or 0

            # print(category, product, quantity)

            if category not in first_table_processed_data:
                first_table_processed_data[category] = {
                    "products": {},
                    # "row_index": len(processed_data)+1,  # сохраняем индекс строки для каждой категории
                }

            if product not in first_table_processed_data[category]["products"]:
                first_table_processed_data[category]["products"][product] = 0

            first_table_processed_data[category]["products"][product] += quantity

            # TODO: переделать опираясь на данные выше.
            # current_quantity = second_table_processed_data.get(product, 0)
            # second_table_processed_data.setdefault(product, quantity).update(quantity)

            second_table_processed_data[product] = second_table_processed_data.get(product, 0) + quantity

            # if product in second_table_processed_data:
            #     second_table_processed_data[product] += first_table_processed_data[category]["products"][product]
            # else:
            #     second_table_processed_data[product] = first_table_processed_data[category]["products"][product]

        # second_table_processed_data =

        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.yellow),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'FreeSans-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 16),
            # ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'TOP'),  # Прижатие содержимого первого столбца к верху
            ('FONTNAME', (0, 1), (-1, -1), 'FreeSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 14),
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('RIGHTPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ]

        for category, values in first_table_processed_data.items():
            # row_index = values["row_index"]
            first_index = len(first_table_data) if len(first_table_data) != 0 else 1
            # получаем сохраненный индекс строки
            for product, quantity in values["products"].items():
                first_table_data.append([category, product, quantity])
            rows_to_merge = (first_index, len(first_table_data) - 1)  # определяем диапазон строк для объединения
            table_style.append(
                ('SPAN', (0, rows_to_merge[0]), (0, rows_to_merge[1])))  # добавляем объединение в стиль таблицы

        buffer = BytesIO()  # Создание буфера памяти

        doc = SimpleDocTemplate(buffer, pagesize=letter)

        table = Table(first_table_data)
        table.setStyle(TableStyle(table_style))

        pdfmetrics.registerFont(TTFont('FreeSans', f'{STATIC_URL}fonts/FreeSans.ttf'))
        pdfmetrics.registerFont(TTFont('FreeSans-Bold', f'{STATIC_URL}fonts/FreeSansBold.ttf'))

        # region start Разграничитель!!!
        [second_table_data.append([str(key), str(value)]) for key, value in second_table_processed_data.items()]
        table_2 = Table(second_table_data)
        table_style_2 = [rule for rule in table_style if rule[0] != 'SPAN']  # Исключаю совмещение полей.
        table_2.setStyle(TableStyle(table_style_2))

        # region end

        # Создайте стили для текста
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        # Создайте новый стиль с нужными атрибутами шрифта
        custom_paragraph_style = ParagraphStyle(
            'CustomStyle',
            parent=normal_style,
            fontName='FreeSans',
            fontSize=14,
            alignment=1
        )

        elements = []

        # Название отчёта
        text0 = Paragraph(f"Отчёт на {self.date}", ParagraphStyle("custom_paragraph_style_2",
                                                                  parent=custom_paragraph_style,
                                                                  fontName="FreeSans-Bold",
                                                                  fontSize=18))
        elements.append(text0)

        elements.append(Spacer(1, 30))

        # Название первой таблицы
        text1 = Paragraph("Обобщающая таблица", custom_paragraph_style)
        elements.append(text1)

        # Отступ между хедером таблицы и её самой
        elements.append(Spacer(1, 10))

        # Вторая таблица
        elements.append(table_2)

        # Отступ между первой таблицей и второй таблицей
        elements.append(Spacer(1, 60))

        # Название второй таблицы
        text2 = Paragraph("Таблица с разбивкой по приёмам пищи", custom_paragraph_style)
        elements.append(text2)

        # Отступ между хедером таблицы и её самой
        elements.append(Spacer(1, 10))

        # Первая таблица
        elements.append(table)

        doc.build(elements)

        buffer.seek(0)  # Перемещение указателя в начало буфера

        result_content = buffer.getvalue()  # Получение данных PDF из буфера

        # Здесь вы можете использовать pdf_data по своему усмотрению, например, отправить его по электронной почте или передать веб-серверу.

        buffer.close()  # Закрытие буфера

        return result_content

    # def _generate_pdf_report(self):
    #     # Получение всех заказов блюд для выбранной даты, отсортированных по дате
    #     orders = Order.objects.filter(order_date=self.date)
    #
    #     # Создание PDF-документа
    #     buffer = BytesIO()
    #     pdf = canvas.Canvas(buffer, pagesize=letter)
    #
    #     pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    #     pdf.setFont("FreeSans", 12)
    #
    #     # Запись информации о заказах в PDF
    #     y = 700
    #     for order in orders:
    #         text = f"Дата заказа: {order.order_date}, Блюдо: {order.parent_id}, Количество: {order.student_id}"
    #         pdf.drawString(100, y, text)
    #         y -= 20
    #
    #     pdf.showPage()
    #     pdf.save()
    #
    #     # Получение содержимого PDF-документа
    #     buffer.seek(0)
    #     self.content = buffer.getvalue()
    #     buffer.close()

    # def _generate_excel_report(self):
    #     # Создание нового Excel-документа
    #     workbook = openpyxl.Workbook()
    #     sheet = workbook.active
    #
    #     # Получение данных из модели OrderItem
    #     queryset = OrderItem.objects.filter(order_id__order_date=self.validated_date)
    #
    #     # Преобразование обработанных данных в список списков
    #     first_table_data = [
    #         ["Приём пищи", "Наименование блюда", "Количество порций"]
    #     ]
    #
    #     second_table_data = [
    #         ["Наименование блюда", "Количество порций"]
    #     ]
    #
    #     queryset = sorted(queryset, key=lambda x: ['Завтрак', 'Обед', 'Полдник', 'Ужин'].index(x.meal_category))
    #
    #     # Обработка данных для объединения и суммирования
    #     first_table_processed_data = {}
    #
    #     second_table_processed_data = {}
    #
    #     for item in queryset:
    #         category = item.meal_category or ""
    #         product = item.product_name or ""
    #         quantity = item.quantity or 0
    #
    #         if category not in first_table_processed_data:
    #             first_table_processed_data[category] = {
    #                 "products": {},
    #             }
    #
    #         if product not in first_table_processed_data[category]["products"]:
    #             first_table_processed_data[category]["products"][product] = 0
    #
    #         first_table_processed_data[category]["products"][product] += quantity
    #
    #         second_table_processed_data[product] = second_table_processed_data.get(product, 0) + quantity
    #
    #     for category, values in first_table_processed_data.items():
    #         first_index = len(first_table_data) if len(first_table_data) != 0 else 1
    #         for product, quantity in values["products"].items():
    #             first_table_data.append([category, product, quantity])
    #         rows_to_merge = (first_index, len(first_table_data) - 1)
    #         # Добавление объединения ячеек в Excel-таблицу
    #         sheet.merge_cells(start_row=rows_to_merge[0], start_column=1, end_row=rows_to_merge[1], end_column=1)
    #
    #     for row in first_table_data:
    #         sheet.append(row)
    #
    #     for row in second_table_data:
    #         sheet.append(row)
    #
    #     # Сохранение Excel-документа в памяти
    #     buffer = BytesIO()
    #     workbook.save(buffer)
    #
    #     # Получение содержимого Excel-документа
    #     buffer.seek(0)
    #     self.content = buffer.getvalue()
    #
    #     buffer.close()

    def get_or_create(self):
        # TODO: Пока что отключил проверку на существование, т.к. не все условия, а просто присутсвие.
        #  Надо будет сделать так, чтобы сначала проверка шла на изменение хотя бы 1 заказа и сразу перерасчёт.
        # if not os.path.exists(self.file_path):
        #     self.generate()
        #     with open(self.file_path, 'wb') as f:
        #         f.write(self.content)
        self.generate()
        with open(self.file_path, 'wb') as f:
            f.write(self.content)
        return self.file_path, self.file_extension
