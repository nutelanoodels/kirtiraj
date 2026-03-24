"""
Management command: seed_products
Usage: python manage.py seed_products
       python manage.py seed_products --clear   (wipes existing data first)

Creates all 7 categories and ~120 products from the Kirtiraj product catalogue.
Products with no rate in the source data are created with price=0 so the owner
can fill them in from the Django admin.
"""

from django.core.management.base import BaseCommand
from products.models import Category, Product


CATALOGUE = {
    "Papad / Mathia / Chorafali": [
        {"name": "Gulla 6pcs",                            "size": 0.085, "price": 20},
        {"name": "Chorafali Papad 500g",                  "size": 0.5,   "price": 150},
        {"name": "Mathia Papad 500g",                     "size": 0.5,   "price": 150},
        {"name": "Green Chilli Mathia Papad 500g",        "size": 0.5,   "price": 170},
        {"name": "Suvari Papad 200g",                     "size": 0.2,   "price": 0},
        {"name": "Single Mari Papad 250g",                "size": 0.25,  "price": 0},
        {"name": "Single Mari Papad 500g",                "size": 0.5,   "price": 150},
        {"name": "Single Mari Disco Papad 400g",          "size": 0.4,   "price": 150},
        {"name": "Punjabi Double Mari Papad 250g",        "size": 0.25,  "price": 0},
        {"name": "Punjabi Double Mari Papad 500g",        "size": 0.5,   "price": 160},
        {"name": "Punjabi Doublemari Disco Papad 400g",   "size": 0.4,   "price": 160},
        {"name": "Jeera Papad 250g",                      "size": 0.25,  "price": 80},
        {"name": "Jeera Disco Papad 400g",                "size": 0.4,   "price": 0},
        {"name": "Jeera Mari Papad 250g",                 "size": 0.25,  "price": 85},
        {"name": "Rajwadi Papad 250g",                    "size": 0.25,  "price": 85},
        {"name": "Garlic Papad 250g",                     "size": 0.25,  "price": 85},
        {"name": "Green Garlic Papad 500g",               "size": 0.5,   "price": 0},
        {"name": "Moong Udad Papad 500g",                 "size": 0.5,   "price": 170},
    ],
    "Cookies / Khari / Toast": [
        {"name": "Atta Biscuit (Wheat Cookies) 200g",     "size": 0.2,   "price": 80},
        {"name": "Australian Cookies 200g",               "size": 0.2,   "price": 110},
        {"name": "Chocolate Chips Cookies 200g",          "size": 0.2,   "price": 90},
        {"name": "Dry Fruit Biscuit 200g",                "size": 0.2,   "price": 110},
        {"name": "Mix Cookies 200g",                      "size": 0.2,   "price": 110},
        {"name": "Multigrain Cookies 200g",               "size": 0.2,   "price": 110},
        {"name": "Surti Nankhatai 200g",                  "size": 0.2,   "price": 110},
        {"name": "Wheat Biscuit 200g",                    "size": 0.2,   "price": 90},
        {"name": "Tuti Fruti Toast 300g",                 "size": 0.3,   "price": 120},
        {"name": "Wheat Toast 300g",                      "size": 0.3,   "price": 120},
        {"name": "Jeera Toast 300g",                      "size": 0.3,   "price": 120},
        {"name": "Wheat Toast Mini 200g",                 "size": 0.2,   "price": 100},
        {"name": "Jeera Toast Mini 200g",                 "size": 0.2,   "price": 100},
        {"name": "Jeera Khari 200g",                      "size": 0.2,   "price": 90},
        {"name": "Plain Khari 200g",                      "size": 0.2,   "price": 90},
        {"name": "Wheat Khari 200g",                      "size": 0.2,   "price": 90},
        {"name": "Wheat Methi Masala Khari 200g",         "size": 0.2,   "price": 90},
    ],
    "Khakhra": [
        {"name": "Bajari Dhebra Khakhra 200g",            "size": 0.2,   "price": 60},
        {"name": "Chatpata Khakhra 200g",                 "size": 0.2,   "price": 60},
        {"name": "Garlic Khakhra 200g",                   "size": 0.2,   "price": 70},
        {"name": "Hot & Spicy Khakhra 200g",              "size": 0.2,   "price": 70},
        {"name": "Jeera Khakhra 500g",                    "size": 0.5,   "price": 130},
        {"name": "Masala Khakhra 500g",                   "size": 0.5,   "price": 130},
        {"name": "Mathiya Khakhra 200g",                  "size": 0.2,   "price": 130},
        {"name": "Methi Khakhra 500g",                    "size": 0.5,   "price": 130},
        {"name": "Methi Masala Khakhra 200g",             "size": 0.2,   "price": 70},
        {"name": "Multi Grain Khakhra 200g",              "size": 0.2,   "price": 70},
        {"name": "Panipuri Khakhra 200g",                 "size": 0.2,   "price": 60},
        {"name": "Plain Khakhra 500g",                    "size": 0.5,   "price": 130},
    ],
    "Khichiya": [
        {"name": "Bajra Khichiya 250g",                   "size": 0.25,  "price": 75},
        {"name": "Green Chilli Rice Papadi 400g Mini",    "size": 0.4,   "price": 130},
        {"name": "Green Chilli Rice Papadi 250g",         "size": 0.25,  "price": 75},
        {"name": "Jeera Rice Papadi 250g",                "size": 0.25,  "price": 75},
        {"name": "Jeera Rice Papadi 400g Mini",           "size": 0.4,   "price": 130},
        {"name": "Jowar Khichiya 250g",                   "size": 0.25,  "price": 75},
        {"name": "Moraiya Papadi 200g Mini",              "size": 0.2,   "price": 70},
        {"name": "Rajwadi Rice Papadi 400g Mini",         "size": 0.4,   "price": 130},
        {"name": "Rajwadi Rice Papadi 250g",              "size": 0.25,  "price": 75},
        {"name": "Sabudana Chamcho 400g",                 "size": 0.4,   "price": 120},
        {"name": "Sabudana Chakri 400g",                  "size": 0.4,   "price": 120},
    ],
    "Namkeen": [
        {"name": "Vadhvani Marcha 200g",                  "size": 0.2,   "price": 85},
        {"name": "Hing 50g",                              "size": 0.05,  "price": 110},
        {"name": "Panipuri 500g",                         "size": 0.5,   "price": 0},
        {"name": "Thick Mathia 200g",                     "size": 0.2,   "price": 85},
        {"name": "Bhel Mix 150g",                         "size": 0.15,  "price": 75},
        {"name": "Chakri 250g",                           "size": 0.25,  "price": 100},
        {"name": "Fire Puri 200g",                        "size": 0.2,   "price": 75},
        {"name": "Masala Puri 200g",                      "size": 0.2,   "price": 65},
        {"name": "Methi Puri 200g",                       "size": 0.2,   "price": 75},
        {"name": "Namak Para 200g",                       "size": 0.2,   "price": 75},
        {"name": "Methi Para 200g",                       "size": 0.2,   "price": 75},
        {"name": "Shakarpara 200g",                       "size": 0.2,   "price": 75},
        {"name": "Bhatha Kani Gathiya 200g",              "size": 0.2,   "price": 80},
        {"name": "Bhavnagri Methi Gathiya 200g",          "size": 0.2,   "price": 65},
        {"name": "Bhavnagri Gathiya 200g",                "size": 0.2,   "price": 65},
        {"name": "Chakri Gathiya 200g",                   "size": 0.2,   "price": 65},
        {"name": "Masala Gathiya 200g",                   "size": 0.2,   "price": 65},
        {"name": "Mora Gathiya 200g",                     "size": 0.2,   "price": 65},
        {"name": "Khamni Sev 200g",                       "size": 0.2,   "price": 85},
        {"name": "Masala Sev 200g",                       "size": 0.2,   "price": 65},
        {"name": "Nylon Sev 200g",                        "size": 0.2,   "price": 65},
        {"name": "Ratlami Sev 200g",                      "size": 0.2,   "price": 70},
        {"name": "Usal Sev 200g",                         "size": 0.2,   "price": 80},
        {"name": "Fulwadi 200g",                          "size": 0.2,   "price": 85},
        {"name": "Tam Tam 200g",                          "size": 0.2,   "price": 85},
        {"name": "Masala Papadi 200g",                    "size": 0.2,   "price": 0},
        {"name": "Plain Papadi Namkeen 200g",             "size": 0.2,   "price": 0},
        {"name": "Bhadrani Moong 200g",                   "size": 0.2,   "price": 65},
        {"name": "Chana Dal 200g",                        "size": 0.2,   "price": 70},
        {"name": "Chanajor Garam 200g",                   "size": 0.2,   "price": 65},
        {"name": "Chapta Mug 200g",                       "size": 0.2,   "price": 60},
        {"name": "Dal Moth 200g",                         "size": 0.2,   "price": 60},
        {"name": "Sing Bhujia 200g",                      "size": 0.2,   "price": 60},
        {"name": "Soya Chips 200g",                       "size": 0.2,   "price": 75},
        {"name": "Soya Stick 200g",                       "size": 0.2,   "price": 75},
        {"name": "Farali Chevdo Spicy 200g",              "size": 0.2,   "price": 65},
        {"name": "Indori Mix 200g",                       "size": 0.2,   "price": 65},
        {"name": "Mix Chavanu 200g",                      "size": 0.2,   "price": 90},
        {"name": "Kenyan Chevdo 200g",                    "size": 0.2,   "price": 85},
        {"name": "Navrang Chevdo 200g",                   "size": 0.2,   "price": 85},
        {"name": "New Gujarati Chevdo 400g",              "size": 0.4,   "price": 160},
        {"name": "Papad Chavanu 200g",                    "size": 0.2,   "price": 85},
        {"name": "Nylon Pauva 200g",                      "size": 0.2,   "price": 75},
        {"name": "Surati Chavanu 200g",                   "size": 0.2,   "price": 85},
        {"name": "Wheat Chevdo 200g",                     "size": 0.2,   "price": 95},
    ],
    "Roasted Namkeen": [
        {"name": "Bajra Puff Roasted 200g",               "size": 0.2,   "price": 90},
        {"name": "Channa Dal Roasted 200g",               "size": 0.2,   "price": 0},
        {"name": "Channa Pudina Dal Roasted 200g",        "size": 0.2,   "price": 90},
        {"name": "Moong Jor Roasted 200g",                "size": 0.2,   "price": 90},
        {"name": "Moong Roasted 200g",                    "size": 0.2,   "price": 0},
        {"name": "Navratan Mix Roasted 200g",             "size": 0.2,   "price": 100},
        {"name": "Total Diet Roasted 200g",               "size": 0.2,   "price": 100},
        {"name": "Wheat Puff 200g",                       "size": 0.2,   "price": 90},
    ],
    "Mukhwas": [
        {"name": "Alsi Mukhwas 150g",                     "size": 0.15,  "price": 0},
        {"name": "Banarasi Paan 220g",                    "size": 0.22,  "price": 0},
        {"name": "Chulbuli Imli 200g",                    "size": 0.2,   "price": 0},
        {"name": "Dhana Dal 180g",                        "size": 0.18,  "price": 0},
        {"name": "Jal Jeera Shots 200g",                  "size": 0.2,   "price": 0},
        {"name": "Kalkatti Paan 220g",                    "size": 0.22,  "price": 0},
        {"name": "Keri Ni Gotli 100g",                    "size": 0.1,   "price": 0},
        {"name": "Mix Fruit Shots 200g",                  "size": 0.2,   "price": 0},
        {"name": "Natural Mukhwas 130g",                  "size": 0.13,  "price": 0},
        {"name": "Paan Shot 170g",                        "size": 0.17,  "price": 110},
        {"name": "Til Alsi Dhana Dal 150g",               "size": 0.15,  "price": 0},
    ],
}


class Command(BaseCommand):
    help = "Seed the database with all Kirtiraj categories and products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing products and categories before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing products and categories."))

        total_cats = 0
        total_products = 0
        skipped = 0

        for cat_name, products in CATALOGUE.items():
            category, cat_created = Category.objects.get_or_create(name=cat_name)
            if cat_created:
                total_cats += 1
                self.stdout.write(f"  Created category: {cat_name}")

            for p in products:
                _, created = Product.objects.get_or_create(
                    name=p["name"],
                    defaults={
                        "price": p["price"],
                        "size": p.get("size"),
                        "category": category,
                        "is_available": True,
                    },
                )
                if created:
                    total_products += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Done! Created {total_cats} categories, {total_products} products. "
            f"({skipped} already existed, skipped)"
        ))
        if skipped == 0 and total_products > 0:
            self.stdout.write(self.style.NOTICE(
                "💡 Products with price=0 need their price filled in via the Django admin."
            ))
