from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
# from django_filters.rest_framework import  DjangoFilterBackend
# from rest_framework.filters import  OrderingFilter, SearchFilter
from django_filters import rest_framework as filters
from app.filters import RpmReadingsFilter

from app.models import Supplier, Item, ItemCategory, Purchase, Quality, TapeType, Tapeline, TapeStock, \
    Inventory, Customer, Stereo, BagType, Order, Loom, LoomStock, Printing, PrintingStock, Dispatch, RpmReading

from app.serializers import SupplierSerializer, ItemSerializer, ItemCategorySerializer, PurchaseSerializer,\
    QualitySerializer, TapeTypeSerializer, TapelineSerializer, TapeStockSerializer, \
    InventorySerializer, CustomerSerializer, StereoSerializer, BagTypeSerializer, OrderSerializer, LoomSerializer, \
    LoomStockSerializer, PrintingSerializer, PrintingStockSerializer, DispatchSerializer, RpmReadingSerializer

import datetime
from django.db.models import Sum

class RpmReadingView(ModelViewSet):
    queryset = RpmReading.objects.all()
    serializer_class = RpmReadingSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RpmReadingsFilter

    # def retrieve(self, request, *args, **kwargs):
    #     super(RpmReadingView, self).retrieve(request, *args, **kwargs)

    #filter_backends = (DjangoFilterBackend, OrderingFilter)
    #filter_fields = ("machine_no",)
    #ordering_fields = ('time')

    # def get_queryset(self):
    #     #print("self: ",self)
    #     queryset = RpmReading.objects.all()
    #
    #     try:
    #         last_values = int(self.request.query_params.get('last_values',''))
    #         machine_no = int(self.request.query_params.get('machine_no',''))
    #         if machine_no and last_values:
    #             return RpmReading.objects.filter(machine_no=machine_no).order_by('-time')[:last_values]
    #
    #     except:
    #         try:
    #             last_minutes = int(self.request.query_params.get('last_minutes',''))
    #             machine_no = int(self.request.query_params.get('machine_no',''))
    #             if last_minutes and machine_no:
    #                 now = datetime.datetime.now()
    #                 earlier = datetime.datetime.now() - datetime.timedelta(minutes=last_minutes)
    #
    #                 return RpmReading.objects.filter(machine_no=machine_no).filter(time__range=(earlier,now))
    #         except:
    #             try:
    #                 last_minutes = int(self.request.query_params.get('last_minutes',''))
    #                 if last_minutes:
    #                     now = datetime.datetime.now()
    #                     earlier = datetime.datetime.now() - datetime.timedelta(minutes=last_minutes)
    #                     return RpmReading.objects.filter(time__range=(earlier,now))
    #
    #             except:
    #                 try:
    #                     last_values = int(self.request.query_params.get('last_values',''))
    #                     if last_values:
    #                         return RpmReading.objects.all().order_by('-id')[:last_values*15]
    #                 except:
    #                     try:
    #                         machine_meters = int(self.request.query_params.get('machine_meters',''))
    #                         meters_sum = {}
    #                         if machine_meters:
    #                             now = datetime.datetime.now()
    #                             earlier = datetime.datetime.now() - datetime.timedelta(minutes=machine_meters)
    #                             print("Now ", now, "\n earlier ", earlier)
    #                             for machine in range(1,16):
    #                                 res = (RpmReading.objects.filter(machine_no=machine).filter(time__range=(earlier,now)).aggregate(Sum('meters')))
    #                                 print(res["meters__sum"])
    #                                 meters_sum[str(machine)] = str(res["meters__sum"])
    #
    #                             z = json.dumps(meters_sum)
    #                             X = {'name': 'John'}
    #                             #print(meters_sum)
    #                             y = json.dumps(X)
    #                             print("y",y)
    #                             return y
    #
    #                     except:
    #                         return RpmReading.objects.filter(machine_no=-1)
    #                     return RpmReading.objects.filter(machine_no=-1)
    #
    #                 return RpmReading.objects.filter(machine_no=-1)
    #             return RpmReading.objects.filter(machine_no=-1)
    #         return RpmReading.objects.filter(machine_no=-1)
    #     return RpmReading.objects.all()
    #
    #

class SupplierView(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ItemView(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


    # queryset = Item.objects.all().order_by('category')
    # print("orderby: ", queryset)


class ItemCategoryView(ModelViewSet):
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer


class PurchaseView(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


    def destroy(self, request, *args, **kwargs):
        try:
            # updating inventory
            j = Purchase.objects.get(id=kwargs['pk'])
            i = Inventory.objects.get(item=j.item)
            i.quantity = i.quantity - j.quantity
            i.price = i.price - j.price
            i.save()
            return super(PurchaseView, self).destroy(request, *args, **kwargs)

        except:
            print("exception in Destroy of PurchaseView")


class InventoryView(ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    # filter_backends = (DjangoFilterBackend,)
    # filter_fields = ("item__name",)

    # def get_queryset(self):
    #     print("self: ",self)
    #     return Inventory.objects.filter(id=self.request["id"])


class LoomView(ModelViewSet):
    queryset = Loom.objects.all()
    serializer_class = LoomSerializer


class LoomStockView(ModelViewSet):
    queryset = LoomStock.objects.all()
    serializer_class = LoomStockSerializer


class PrintingView(ModelViewSet):
    queryset = Printing.objects.all()
    serializer_class = PrintingSerializer


class PrintingStockView(ModelViewSet):
    queryset = PrintingStock.objects.all()
    serializer_class = PrintingStockSerializer


class DispatchView(ModelViewSet):
    queryset = Dispatch.objects.all()
    serializer_class = DispatchSerializer


class QualityView(ModelViewSet):
    queryset = Quality.objects.all()
    serializer_class = QualitySerializer


class TapeTypeView(ModelViewSet):
    queryset = TapeType.objects.all()
    serializer_class = TapeTypeSerializer


class TapelineView(ModelViewSet):
    queryset = Tapeline.objects.all()
    serializer_class = TapelineSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            # Updating Inventory
            j = Tapeline.objects.get(id=kwargs['pk'])
            i = j.inventory
            price_per_kg = i.price / i.quantity
            i.quantity = i.quantity + j.quantity
            i.price = i.price + (j.quantity * price_per_kg)
            i.save()

            # Updating Tapestock
            i = TapeStock.objects.get(tape_type_id=j.tape_type.id)
            i.quantity = i.quantity - j.quantity
            i.save()


            return super(TapelineView, self).destroy(request, *args, **kwargs)

        except:
            print("exception in Destroy of TapelineView")


class TapeStockView(ModelViewSet):
    queryset = TapeStock.objects.all()
    serializer_class = TapeStockSerializer


class CustomerView(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class StereoView(ModelViewSet):
    queryset = Stereo.objects.all()
    serializer_class = StereoSerializer


class BagTypeView(ModelViewSet):
    queryset = BagType.objects.all()
    serializer_class = BagTypeSerializer


class OrderView(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
