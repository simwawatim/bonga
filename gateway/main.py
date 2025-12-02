from flask import Flask
from modules.sales_bp import sales_bp
from modules.items_bp import items_bp
from modules.customers import customers_bp
from modules.users import users_bp
from modules.tenants import tenants_bp
from modules.stock_bp import stock_bp
from modules.stock_master import stock_master_bp
from modules.supplier import suppliers_bp
from modules.purchase_bp import purchase_bp
from modules.quotation_bp import quotation_bp

app = Flask(__name__)

app.register_blueprint(customers_bp)
app.register_blueprint(users_bp)
app.register_blueprint(tenants_bp)
app.register_blueprint(items_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(stock_master_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(quotation_bp)

app.register_blueprint(suppliers_bp)
if __name__ == "__main__":
    app.run(port=5000, debug=True)
