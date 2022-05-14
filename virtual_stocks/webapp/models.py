from datetime import datetime
from flask import current_app
from sqlalchemy import except_all
from webapp import db, login_manager
from flask_login import UserMixin
import jwt
from datetime import datetime ,timedelta

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_stocks = db.relationship('User_stock', backref='author', lazy=True)
    user_funds = db.relationship('User_funds', backref='author2', lazy=True)

    def get_reset_token(self, expires_sec=180): 
            payload = {
                'exp': datetime.utcnow()+timedelta(days=0, seconds=expires_sec),
                'iat': datetime.utcnow(),
                'sub': self.id
                }
            return jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
                )


    @staticmethod
    def verify_reset_token(token):
        try:
            payload = jwt.decode(
                token, 
                current_app.config.get('SECRET_KEY'),
                'HS256')
        except:
            return None
        return User.query.get(payload['sub'])



class User_stock(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    # stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=True)
    share = db.Column(db.Integer, nullable= False)
    stock_name = db.Column(db.String(120), nullable=False)
    stock_key = db.Column(db.String(20), nullable=False)
    stock_price = db.Column(db.Numeric(60, scale=2), nullable=False)
    total_share_price = db.Column(db.Numeric(60, scale=2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User_stock('{self.stock_key}','{self.share}','{self.stock_price}')"

class User_funds(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    available_funds = db.Column(db.Numeric(60, scale=2), nullable=False, )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"User_funds('{self.user_id}','{self.available_funds}')"
# class Stock(db.Model):
#     id = db.Column(db.Integer, primary_key= True)
#     code = db.Column(db.String(100), nullable = False)
#     date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
#     buy_price = db.Column(db.String, nullable= False)
#     sell_price =db.Column(db.String, nullable= False)
#     stock_transacts = db.relationship('Stock_transact', backref='author2', lazy=True)
#     user_stocks = db.relationship('User_stock', backref='author2', lazy=True)


# class Stock_transact(db.Model):
#     id = db.Column(db.Integer, primary_key= True)
#     code = db.Column(db.String(100), nullable = False)
#     date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
#     quantity = db.Column(db.Integer, nullable= False)
#     buy_price = db.Column(db.String, nullable= False)
#     sell_price =db.Column(db.String, nullable= False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)

#     def __repr__(self):
#         return f"Post('{self.title}','{self.date_posted}')"