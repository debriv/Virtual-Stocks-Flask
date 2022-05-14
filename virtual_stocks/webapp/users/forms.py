from logging import PlaceHolder
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, 
                    PasswordField, 
                    SubmitField, 
                    BooleanField,
                    SelectField,
                    IntegerField,
                    DecimalField)
from wtforms.validators import (DataRequired, 
                                Length, 
                                NumberRange,
                                Email, 
                                EqualTo, 
                                ValidationError)
from webapp.models import User, User_stock
from webapp import db
from sqlalchemy import func


class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                        validators=[DataRequired(), ])
    confirm_password = PasswordField('Confirm Password', 
                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('SignUp')

    def validate_username(self , username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken. Please choose a different username.')

    def validate_email(self , email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken. Please choose a different email.')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self , username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is taken. Please choose a different username.')

    def validate_email(self , email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is taken. Please choose a different email.')



class RequestResetForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self , email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')



class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', 
                        validators=[DataRequired(), ])

    confirm_password = PasswordField('Confirm Password', 
                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                        validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class BuyForm(FlaskForm):
    symbol = StringField('Symbol', 
                        validators=[DataRequired()])

    share = IntegerField('Share', 
                        validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Buy')


class SellForm(FlaskForm):
    symbol = SelectField('Symbol',  
                        choices = [],
                        validators=[DataRequired()])
    share = IntegerField('Share', 
                        validators=[DataRequired(),  NumberRange(min=0) , ])  
    submit = SubmitField('Sell')

    def validate_share(self,share ):
        if self.symbol.data=="Select":
            raise ValidationError("Select is not a proper symbol")
        user = db.session.query(func.sum(User_stock.share))\
            .filter_by(stock_key= self.symbol.data).first()
        print(user[0] ,share.data)
        if user[0] <= share.data:
            raise ValidationError("You don't have that many shares")


class AddFundsForm(FlaskForm):
    funds = DecimalField('ADD Funds',
                        places=2,
                        default=1,
                        validators=[DataRequired(), 
                                    NumberRange(min=1,max=1000000)])
    submit = SubmitField('Add Funds')
