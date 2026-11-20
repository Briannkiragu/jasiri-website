from django.db import migrations


PRODUCTS = [
    ("essential-graphic-tee", "Essential Graphic Tee", "tee", "1200.00", "Mwanzocollection/tees/9.jpg"),
    ("classic-tee", "Classic Tee", "tee", "1200.00", "Mwanzocollection/tees/8.jpg"),
    ("statement-graphic-tee", "Statement Graphic Tee", "tee", "1200.00", "Mwanzocollection/tees/T1.jpg"),
    ("everyday-graphic-tee", "Everyday Graphic Tee", "tee", "1200.00", "Mwanzocollection/tees/t9.jpg"),
    ("limited-graphic-tee", "Limited Graphic Tee", "tee", "600.00", "Mwanzocollection/tees/o.jpg"),
    ("freedom-print-tee", "Freedom Print Tee", "tee", "600.00", "Mwanzocollection/tees/t4.jpg"),
    ("essential-streetwear-tee", "Essential Streetwear Tee", "tee", "600.00", "Mwanzocollection/tees/t3.jpg"),
    ("signature-graphic-tee", "Signature Graphic Tee", "tee", "600.00", "Mwanzocollection/tees/6.jpg"),
    ("essential-utility-jacket", "Essential Utility Jacket", "jacket", "1200.00", "Mwanzocollection/jackets/1.jpg"),
    ("classic-street-jacket", "Classic Street Jacket", "jacket", "1200.00", "Mwanzocollection/jackets/3.jpg"),
    ("statement-jacket", "Statement Jacket", "jacket", "1200.00", "Mwanzocollection/jackets/4.jpg"),
    ("signature-jacket", "Signature Jacket", "jacket", "1200.00", "Mwanzocollection/jackets/7.jpg"),
    ("everyday-jacket", "Everyday Jacket", "jacket", "1200.00", "Mwanzocollection/jackets/6.jpg"),
    ("limited-jacket", "Limited Jacket", "jacket", "600.00", "Mwanzocollection/jackets/5b.jpg"),
    ("premium-layer-jacket", "Premium Layer Jacket", "jacket", "2000.00", "Mwanzocollection/jackets/2a.jpg"),
    ("statement-layer-jacket", "Statement Layer Jacket", "jacket", "2000.00", "Mwanzocollection/jackets/11.jpg"),
]


def seed_catalog(apps, schema_editor):
    Product = apps.get_model("store", "Product")
    Product.objects.bulk_create(
        [
            Product(
                slug=slug,
                name=name,
                category=category,
                price=price,
                image=image,
            )
            for slug, name, category, price, image in PRODUCTS
        ]
    )


class Migration(migrations.Migration):
    dependencies = [("store", "0001_initial")]

    operations = [migrations.RunPython(seed_catalog, migrations.RunPython.noop)]
