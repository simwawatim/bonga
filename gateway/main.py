from flask import Flask
from modules.customers import customers_bp
from modules.users import users_bp
from modules.tenants import tenants_bp

app = Flask(__name__)

app.register_blueprint(customers_bp)
app.register_blueprint(users_bp)
app.register_blueprint(tenants_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
