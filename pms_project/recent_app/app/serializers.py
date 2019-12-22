from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.fields import CharField


from app.models import Supplier, Item, ItemCategory, Purchase, Quality, Tapeline, TapeType, TapeStock, Inventory, \
    Customer, Stereo, BagType, Order, Loom, LoomStock, Printing, PrintingStock ,Dispatch


class SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name", "address", "contact", "email", "NTN", "GST")


class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ("id", "category", "name",)


class ItemCategorySerializer(ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ("id", "name",)


class PurchaseSerializer(ModelSerializer):

    supplier_name = CharField(source="supplier.name", read_only=True)
    item_name = CharField(source="item.name", read_only=True)
    item_category = CharField(source="item.category", read_only=True)

    class Meta:
        model = Purchase
        fields = ("id", "supplier", "item", "unit","quantity", "price", "comments", "supplier_name", "item_name", "item_category",  "date_time", )

    def create(self, v):

        i, created = Inventory.objects.get_or_create(item=v["item"], defaults={
            "quantity": v["quantity"],
            "price": v["price"]
        })

        if created:
            return Purchase.objects.create(**v)
        else:
            i.quantity = i.quantity + v["quantity"]
            i.price = i.price + v["price"]
            i.save()
            return Purchase.objects.create(**v)


class InventorySerializer(ModelSerializer):

    item_category = CharField(source="item.category", read_only=True)
    item = ItemSerializer()

    class Meta:
        model = Inventory
        fields = ("id", "item", "quantity", "price", "item_category")


class BagTypeSerializer(ModelSerializer):
    class Meta:
        model = BagType
        fields = ("id", "quality", "width", "length", "frame", "color", "weight",)


class LoomSerializer(ModelSerializer):
    quality = CharField(source="tape_type.quality", read_only=True)
    denier = CharField(source="tape_type.denier", read_only=True)
    color = CharField(source="tape_type.color", read_only=True)
    width = CharField(source="bag_type.width", read_only=True)
    length = CharField(source="bag_type.length", read_only=True)
    frame = CharField(source="bag_type.frame", read_only=True)
    weight = CharField(source="bag_type.weight", read_only=True)

    bag_type = BagTypeSerializer()

    class Meta:
        model = Loom
        fields = ("id", "loom_number", "circumference", "tape_type","bag_type", "quantity" ,"quality","denier","color","width","length","frame","weight",  "date_time", )
        #read_only_fields = ("quantity",)

    def create(self, validated_data):
        # updating BagType
        bag_type = validated_data.pop("bag_type")
        bag_type_obj, created2 = BagType.objects.get_or_create(**bag_type)

        # rpm_from_sensor = 12
        # quantity_meter = rpm_from_sensor * validated_data["circumference"]
        # bag_length_meter = (bag_type.length+2) / 39.3701
        # weight_per_meter = (bag_type.weight-1) / bag_length_meter
        # weight = float(quantity_meter) * weight_per_meter

        weight = 100.00

        # updating loomstock

        i, created = LoomStock.objects.get_or_create(bag_type_id=1, defaults={
            "quantity" : weight
        })

        if created:
            print("created: ",created)
            return Loom.objects.create(**validated_data)
        else:
            i.quantity += weight
            i.save()

        return Loom.objects.create(**validated_data, bag_type=bag_type_obj)

    def update(self, instance, validated_data):
        bag_type = validated_data.pop("bag_type")
        bag_type_obj, created = BagType.objects.get_or_create(**bag_type)
        instance.bag_type = bag_type_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class LoomStockSerializer(ModelSerializer):
    class Meta:
        model = LoomStock
        fields = ("id", "bag_type_id", "quantity",)


class PrintingSerializer(ModelSerializer):
    width = CharField(source="loom_stock.bag_type.width", read_only=True)
    length = CharField(source="loom_stock.bag_type.length", read_only=True)
    frame = CharField(source="loom_stock.bag_type.frame", read_only=True)
    color = CharField(source="loom_stock.bag_type.color", read_only=True)
    weight = CharField(source="loom_stock.bag_type.weight", read_only=True)
    quality = CharField(source="loom_stock.bag_type.quality", read_only=True)

    stereo_name = CharField(source="stereo.name", read_only=True)
    stereo_width = CharField(source="stereo.width", read_only=True)
    stereo_length = CharField(source="stereo.length", read_only=True)

    class Meta:
        model = Printing
        fields = ("id", "order", "machine", "loom_stock", "stereo", "quantity",
                  "width", "length", "frame", "color", "weight", "quality",
                  "stereo_name", "stereo_width", "stereo_length",  "date_time", )

    def create(self, validated_data):
        loomstock = validated_data["loom_stock"]
        loomstock.quantity -= validated_data["quantity"]
        loomstock.save()

        # updating printing stock
        try:
            i = PrintingStock.objects.get(order_id=validated_data["order"].id)
            i.quantity = i.quantity + validated_data["quantity"]
            i.save()

        except:
            i = PrintingStock.objects.create(order_id=validated_data["order"].id, quantity=validated_data["quantity"])

        return Printing.objects.create(**validated_data)


class PrintingStockSerializer(ModelSerializer):
    class Meta:
        model = PrintingStock
        fields = ("id", "order_id", "quantity")


class DispatchSerializer(ModelSerializer):
    customer_name = CharField(source="customer.name", read_only=True)
    width = CharField(source="printing.loom_stock.bag_type.width", read_only=True)
    length = CharField(source="printing.loom_stock.bag_type.length", read_only=True)
    frame = CharField(source="printing.loom_stock.bag_type.frame", read_only=True)
    color = CharField(source="printing.loom_stock.bag_type.color", read_only=True)
    weight = CharField(source="printing.loom_stock.bag_type.weight", read_only=True)
    quality = CharField(source="printing.loom_stock.bag_type.quality", read_only=True)
    class Meta:
        model = Dispatch
        fields = ("id", "printing", "order", "quantity", "dispatch_time", "customer_name",
                  "width", "length", "frame", "color", "weight", "quality",  "date_time", )


    def create(self, validated_data):
        print("Validated: ", validated_data)

        i = PrintingStock.objects.get(order_id=validated_data["order"].id)
        i.quantity -= validated_data["quantity"]
        i.save()

        return Dispatch.objects.create(**validated_data)


class QualitySerializer(ModelSerializer):
    class Meta:
        model = Quality
        fields=("id","name")


class TapeTypeSerializer(ModelSerializer):
    class Meta:
        model = TapeType
        fields = ("id", "quality", "denier", "color",)


class TapeStockSerializer(ModelSerializer):
    class Meta:
        model = TapeStock
        fields = ("id", "tape_type_id", "quantity",)


class TapelineSerializer(ModelSerializer):
    item_name = CharField(source="inventory.item.name", read_only=True)
    item_category = CharField(source="inventory.item.category.name", read_only=True)
    tape_type = TapeTypeSerializer()

    class Meta:
        model = Tapeline
        fields = ("id", "batch_id", "inventory", "tape_type", "quantity", "item_name","item_category", "date_time", )

    def create(self, validated_data):
        tape_type = validated_data.pop("tape_type")
        tape_type_obj, created = TapeType.objects.get_or_create(**tape_type)
        tapeline = Tapeline.objects.create(**validated_data, tape_type=tape_type_obj)

        # Update inventory
        i = validated_data["inventory"]
        price_per_kg = i.price/i.quantity;
        i.quantity = i.quantity - validated_data["quantity"]
        i.price = i.price - (validated_data["quantity"]*price_per_kg)
        i.save()

        # update Tapestock
        try:
            i = TapeStock.objects.get(tape_type_id=tape_type_obj.id)
            i.quantity = i.quantity + validated_data["quantity"]
            i.save()

        except:
            i = TapeStock.objects.create(tape_type_id=tape_type_obj.id, quantity=validated_data["quantity"])

        return tapeline

    def update(self, instance, validated_data):
        tape_type = validated_data.pop("tape_type")

        tape_type_obj, created = TapeType.objects.get_or_create(**tape_type)

        instance.tape_type = tape_type_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class CustomerSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ("id", "name", "address", "contact", "email", "NTN", "GST",)


class StereoSerializer(ModelSerializer):
    class Meta:
        model = Stereo
        fields = ("id", "name", "width", "length",)


class OrderSerializer(ModelSerializer):

    customer_name = CharField(source="customer.name", read_only=True)
    stereo_name = CharField(source="stereo.name", read_only=True)
    bag_type = BagTypeSerializer()
    stereo = StereoSerializer()

    class Meta:
        model = Order
        fields = ("id", "customer", "stereo", "bag_type", "quantity", "customer_name", "stereo_name",  "date_time", )

    def create(self, validated_data):
        stereo = validated_data.pop("stereo")
        bag_type = validated_data.pop("bag_type")

        stereo_obj, created = Stereo.objects.get_or_create(**stereo)
        bag_type_obj, created = BagType.objects.get_or_create(**bag_type)

        order = Order.objects.create(**validated_data, bag_type=bag_type_obj, stereo=stereo_obj)

        return order

    def update(self, instance, validated_data):
        stereo = validated_data.pop("stereo")
        bag_type = validated_data.pop("bag_type")

        stereo_obj, created = Stereo.objects.get_or_create(**stereo)
        bag_type_obj, created = BagType.objects.get_or_create(**bag_type)

        instance.stereo = stereo_obj
        instance.bag_type = bag_type_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance



    #     bag_type = validated_data.pop("bag_type")
    #     bag_type_obj, created = BagType.objects.get_or_create(**bag_type)
    #
    #     order = Order.objects.create(**validated_data, bag_type=bag_type_obj)
    #
    #     return order
    #
    # def update(self, instance, validated_data):
    #     bag_type = validated_data.pop("bag_type")
    #     bag_type_obj, created = BagType.objects.get_or_create(**bag_type)
    #     instance.bag_type = bag_type_obj
    #
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     instance.save()
    #
    #     return instance