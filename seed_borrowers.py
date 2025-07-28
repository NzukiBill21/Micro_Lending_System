from app import app, db
from models import Borrower
import random

ethnic_groups = [
    ["Wanjiku", "Kamau", "Wairimu", "Muthoni"],
    ["Mutiso", "Mwikali", "Mutua", "Ndinda"],
    ["Muriuki", "Nkatha", "Mutuma", "Karimi"],
    ["Odhiambo", "Atieno", "Ochieng", "Akinyi"],
    ["Wekesa", "Naliaka", "Barasa", "Mukami"],
    ["Abdi", "Farhia", "Hassan", "Amina"],
    ["Nyaboke", "Onsongo", "Kemunto", "Morara"],
    ["Chacha", "Marwa", "Nyamongo", "Mwita"],
    ["Kiptoo", "Chebet", "Kiplagat", "Jepkoech"]
]

with app.app_context():
    for i in range(30):
        group = random.choice(ethnic_groups)
        name = random.choice(group)
        loan_amount = random.randint(50000, 1000000)
        status = random.choice(["Active", "Pending", "Defaulted"])

        borrower = Borrower(name=name, loan_amount=loan_amount, status=status)
        db.session.add(borrower)

    db.session.commit()
    print("✅ Seeded 30 borrowers!")
