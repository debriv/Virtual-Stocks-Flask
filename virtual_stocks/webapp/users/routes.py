from flask import   (render_template,
                    url_for, 
                    flash, 
                    redirect, 
                    request ,                     
                    abort,
                    Blueprint)
from flask_login import (login_user, 
                        current_user, 
                        logout_user, 
                        login_required)
from webapp import db, bcrypt
from webapp.models import User, User_funds, User_stock
from webapp.users.forms import (RegistrationForm, 
                            LoginForm,
                            UpdateAccountForm,
                            BuyForm,
                            AddFundsForm,
                            RequestResetForm,
                            ResetPasswordForm,                            
                            SellForm )
from webapp.main.utils import search_key
from sqlalchemy import func
from webapp.users.utils import send_reset_email

users = Blueprint('users',__name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        user_funds = User_funds(available_funds='10000',user_id=user.id)
        db.session.add(user_funds)
        db.session.commit()
        flash('Your account has been created! Please login to continue.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title ='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessfull. Please check email and password', 'danger')

    return render_template('login.html', title ='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.','success')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! Please login to continue.', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data =current_user.email
    return render_template('account.html', title ='Account', form=form )

@users.route("/consolidated_history", methods=['GET', 'POST'])
@login_required
def consolidated_history():
    if request.method == 'GET':
        user_fund = User_funds.query.filter_by(user_id=current_user.id).first_or_404()
        user_stock_total_list = db.session.query(User_stock.stock_name,
                                            User_stock.stock_key,
                                            User_stock.stock_price,
                                            func.sum(User_stock.share).label('shares'),
                                            func.sum(User_stock.total_share_price).label('total'))\
                                            .filter_by(user_id=user_fund.user_id)\
                                            .group_by(User_stock.stock_key)\
                                            .order_by(User_stock.stock_name)\
                                            .all()
        if user_fund.author2 != current_user:
            abort(403)
    return render_template('consolidated_history.html', 
                            title ='Consolidated History', 
                            avl_funds= user_fund.available_funds,
                            user_stock_total_list=user_stock_total_list)

@users.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    user_fund = User_funds.query.filter_by(id=current_user.id).first_or_404()
    if user_fund.available_funds <= 0:
        flash('Your balance is less than or equal to zero', 'danger')
        return redirect(url_for('users.add_funds'))
    form = BuyForm()
    # if user.id != current_user:
    #     abort(403)
    if form.validate_on_submit():
        results=search_key(form.symbol.data)
        if results == None:
            flash('Invalid Keyword!', 'danger')
            return redirect(url_for('users.buy',user_id=user.id))
        # print(results['price'])
        total_stock_price = results['price'] * int(form.share.data)
        if total_stock_price > user_fund.available_funds:
            flash("Your don't have that much balance", 'danger')
            return redirect(url_for('users.buy'))
        user_stock = User_stock(stock_name=str(results['name']),
                                share=form.share.data,
                                stock_key=form.symbol.data,
                                stock_price=results['price'],
                                total_share_price=total_stock_price,
                                user_id=user.id)
        db.session.add(user_stock)
        db.session.commit()
        
        db.session.query(User_funds).filter_by(id=user.id).update({User_funds.available_funds: User_funds.available_funds - total_stock_price})
        db.session.commit()
        flash('Your bought a share!', 'success')
        return redirect(url_for('users.consolidated_history'))
    
    return render_template('buy.html', title ='Buy', form=form)



@users.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    form=SellForm()
    # if user.id != current_user:
    #     abort(403)
    stock_counts = db.session.query(func.sum(User_stock.share)\
                                .label('share_total'),
                                User_stock.stock_key)\
                                .filter(User_stock.user_id==user.id)\
                                .group_by(User_stock.stock_key)\
                                .all()
    removed_stocks=[stock_count[1] for stock_count in stock_counts if stock_count['share_total'] == 0]
    
    stock_names = db.session.query(func.distinct(User_stock.stock_key)\
                                .label('distinct_stock_key'))\
                                .filter(User_stock.user_id==user.id)\
                                .all()
    choices=["".join(stock_name) for stock_name in stock_names]
    choices= [act_chc for act_chc in choices if act_chc not in removed_stocks]

    if len(choices) == 0 :
        flash('Buy share first to sell', 'danger')
        return redirect(url_for('users.buy'))
    # stock_names = db.session.query(func.sum(User_stock.share),User_stock.stock_key).filter_by(user_id=user.id).all()
    
    choices.append("Select")
    form.symbol.choices= choices[::-1]
    form.symbol.default=0
    
    if form.validate_on_submit():
        stock_price = search_key(form.symbol.data)
        form.share.data = int(form.share.data) * (-1)
        total_stock_price = stock_price['price'] * form.share.data
        user_stock = User_stock(stock_name=str(stock_price['name']),
                                share=form.share.data,
                                stock_key=form.symbol.data,
                                stock_price=stock_price['price'],
                                total_share_price=total_stock_price,
                                user_id=user.id)
        db.session.add(user_stock)
        db.session.commit()
        
        db.session.query(User_funds).filter_by(id=user.id).update({User_funds.available_funds: User_funds.available_funds - total_stock_price})
        db.session.commit()
        flash('Your just sold the share!', 'success')
        return redirect(url_for('users.consolidated_history'))
    return render_template('buy.html', title ='Buy', form=form)



@users.route("/history", methods=['GET', 'POST'])
@login_required
def history():
    if request.method == 'GET':
        user_fund = User_funds.query.filter_by(user_id=current_user.id).first_or_404()
        user_stock_list = User_stock.query\
                                    .filter_by(user_id=user_fund.user_id)\
                                    .order_by(User_stock.stock_name)\
                                    .all()\
                                    
        user_stock_total_list = db.session.query(User_stock.stock_name,
                                            User_stock.stock_key,
                                            User_stock.stock_price,
                                            func.sum(User_stock.share).label('shares'),
                                            func.sum(User_stock.total_share_price).label('total'))\
                                            .filter_by(user_id=user_fund.user_id)\
                                            .group_by(User_stock.stock_key)\
                                            .order_by(User_stock.stock_name)\
                                            .all()
        
                                            
        # print(user_stock_total_list)
        if user_fund.author2 != current_user:
            abort(403)

    return render_template('history.html', 
                            title ='History', 
                            avl_funds= user_fund.available_funds,
                            user_stock_list=user_stock_list, 
                            user_stock_total_list=user_stock_total_list )


@users.route("/add_funds", methods=['GET', 'POST'])
@login_required
def add_funds():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    form= AddFundsForm()
    if form.validate_on_submit():
        # print(type(form.funds.data))
        db.session.query(User_funds).filter_by(id=user.id).update({User_funds.available_funds: User_funds.available_funds +  form.funds.data})
        db.session.commit()
        flash('Your just sold the share!', 'success')
        return redirect(url_for('users.consolidated_history'))
    return render_template('add_funds.html', 
                            title ='Add_funds',form=form)
