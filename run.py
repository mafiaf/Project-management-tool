from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This will create the database tables
    app.run(debug=True)
