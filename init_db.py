from app import app, db, Borrower
db.create_all()

# Add test borrowers
for i in range(1, 31):
    borrower = Borrower(
        name=f"Borrower {i}",
        email=f"borrower{i}@mail.com",
        phone=f"0700000{i:02d}",
        address=f"Area {i}"
    )
    db.session.add(borrower)

db.session.commit()
print("Database created and 30 borrowers added.")
