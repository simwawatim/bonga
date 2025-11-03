from flask import Flask
from modules.items_bp import items_bp
from modules.customers import customers_bp
from modules.users import users_bp
from modules.tenants import tenants_bp
from modules.stock_bp import stock_bp
app = Flask(__name__)

app.register_blueprint(customers_bp)
app.register_blueprint(users_bp)
app.register_blueprint(tenants_bp)
app.register_blueprint(items_bp)
app.register_blueprint(stock_bp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
