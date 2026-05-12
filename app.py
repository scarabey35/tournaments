from app import create_app

app = create_app(register_blueprints=True, create_tables=True)

if __name__ == "__main__":
    app.run(debug=True)
